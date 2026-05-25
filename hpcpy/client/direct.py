"""Direct execution client (no scheduler)."""

import subprocess
import shlex
import os
import re
from pathlib import Path
from typing import Union

from hpcpy.client.base import BaseClient
from hpcpy.constants.direct import COMMANDS, DIRECTIVES, STATUSES
from hpcpy.utilities import shell
from hpcpy.job import Job
import hpcpy.constants as hc


class DirectClient(BaseClient):
    """Direct execution interface for systems without a scheduler.

    Runs scripts directly as local processes, using the process ID as the
    job ID. Status is tracked via ps(1).

    Parameters
    ----------
    *args
        Positional arguments forwarded to the base class.
    **kwargs
        Keyword arguments forwarded to the base class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            cmd_templates=COMMANDS,
            directive_templates=DIRECTIVES,
            statuses=STATUSES,
            status_attribute="short",
            *args,
            **kwargs,
        )

    def status(self, job_id):
        """Get the status of a directly-executed process.

        Parameters
        ----------
        job_id : str
            Process ID.

        Returns
        -------
        tuple
            Generic status code and native status dictionary.
        """
        cmd = self.cmd_templates["status"].format(job_id=job_id)

        # ps returns non-zero when the process does not exist, so use check=False
        result = shell(cmd, check=False)
        raw = result.stdout.decode("utf8").strip()

        return self._parse_status(raw, job_id)

    def submit(
        self,
        job_script: Union[str, Path],
        directives: list = None,
        render: bool = False,
        dry_run: bool = False,
        variables: dict = dict(),
        **context,
    ):
        """Submit a job by running it directly as a local process.

        Parameters
        ----------
        job_script : Union[str, Path]
            Path to the script to execute.
        directives : list, optional
            Ignored for direct execution.
        render : bool, optional
            Render the job script from a template, by default False
        dry_run : bool, optional
            Return the command rather than executing it, by default False
        variables : dict, optional
            Environment variables to set for the process.
        **context :
            Additional key/value pairs for job script rendering.

        Returns
        -------
        Union[Job, str]
            Submitted job object, or the command string if dry_run=True.
        """
        # Sanitize the variables, if there are any, then create string version and add to context
        variables_sanitized = self._sanitize_dict(variables)
        variables_str = []
        for key, value in variables_sanitized.items():
            variables_str.append(f"{key}={value}")

        context["variables_str"] = (
            " ".join(variables_str) + " " if variables_str else ""
        )

        # Delegate command assembly (directive rendering, job script rendering) to the parent
        cmd = super().submit(
            job_script=job_script,
            directives=directives if isinstance(directives, list) else [],
            render=render,
            dry_run=True,
            variables=self._sanitize_dict(variables),
            **context,
        )

        if dry_run:
            return cmd

        _env = os.environ.copy()
        if isinstance(variables_sanitized, dict) and variables_sanitized:
            _env.update({k: str(v) for k, v in variables_sanitized.items()})

        proc = subprocess.Popen(shlex.split(cmd), env=_env)
        job_id = str(proc.pid)

        job = Job(job_id, client=None, auto_update=False)
        job.set_client(self)
        job._auto_update = True

        return job

    def _parse_status(self, raw, job_id):
        """Extract the status from the raw ps output.

        Parameters
        ----------
        raw : str
            Raw output from ps(1). Empty string means the process has finished.
        job_id : str
            Process ID.

        Returns
        -------
        tuple
            Generic status code and native status dictionary.
        """
        # Empty output means the process no longer exists
        if not raw:
            return hc.STATUS_FINISHED, {"pid": job_id, "state": "FINISHED"}

        # ps -o stat= returns one or more characters; the first is the main state
        state_char = raw[0]
        generic_status = None

        for s in self.statuses:
            if state_char == s.short:
                generic_status = s.status
                break

        return generic_status, {"pid": job_id, "state": raw}

    def _sanitize_dict(self, user_dict: dict) -> dict:
        """Sanitize user-supplied dict for use with subprocess.run.

        Parameters
        ----------
        user_dict : dict
            Key/value pairs.

        Returns
        -------
        dict
            Sanitized version of the dict.

        Raises
        ------
        ValueError
            When a key is invalid.
            When a value is invalid.
            When a null byte is provided.
        """
        VALID_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        sanitized = dict()

        for key, value in user_dict.items():

            # Validate key
            if not isinstance(key, str):
                raise ValueError(f"Key {key!r} must be a string")

            if not VALID_KEY.match(key):
                raise ValueError(
                    f"Key {key!r} is invalid: must start with a letter or underscore "
                    f"and contain only alphanumeric characters and underscores"
                )

            # Validate and sanitize value
            if not isinstance(value, (str, int, float, bool)):
                raise ValueError(
                    f"Value for key {key!r} must be a string, int, float, or bool; "
                    f"got {type(value).__name__}"
                )

            str_value = str(value)

            # Reject null bytes — they silently truncate strings in most shells
            if "\x00" in str_value:
                raise ValueError(f"Value for key {key!r} contains a null byte")

            # Add to dict and quote for safety
            sanitized[key] = shlex.quote(str_value)

        return sanitized
