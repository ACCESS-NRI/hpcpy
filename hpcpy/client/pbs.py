"""PBS implementation."""

from hpcpy.client.base import BaseClient
from hpcpy.constants.pbs import COMMANDS, DIRECTIVES, STATUSES, DELAY_DIRECTIVE_FMT
from datetime import datetime, timedelta
from typing import Union
import json
from pathlib import Path
from shlex import quote


class PBSClient(BaseClient):
    """PBS interface.

    Parameters
    ----------
    *args
        Positional arguments forwarded to the base class.
    **kwargs
        Keyword arguments forwarded to the base class.
    """

    def __init__(self, *args, **kwargs):
        # Set up the templates
        super().__init__(
            cmd_templates=COMMANDS,
            directive_templates=DIRECTIVES,
            statuses=STATUSES,
            status_attribute="short",
            *args,
            **kwargs,
        )

    def status(self, job_id):
        """Get the status of a job.

        Parameters
        ----------
        job_id : str
            Job ID.

        Returns
        -------
        str
            Generic status code.
        """
        # Get the raw response
        raw = super().status(job_id=job_id)

        # Parse the status as per this implementation
        generic_status, native_full = self._parse_status(raw, job_id)

        # Return the generic status
        return generic_status, native_full

    def _render_variables(self, variables):
        """Render the variables flag for PBS.

        Parameters
        ----------
        variables : dict
            Dictionary of variables

        Returns
        -------
        str
            String formatted variables for PBS
        """

        formatted = list()

        for k, v in variables.items():

            # Fix for broken quotes #52
            if isinstance(v, str) and " " in v:
                v = quote(v)
                line = f'"{k}={v}"'
                formatted.append(line)
            else:
                formatted.append(f"{k}={v}")

        formatted = ",".join(formatted)
        return f"-v {formatted}"

    def submit(
        self,
        job_script: Union[str, Path],
        directives: list = None,
        render: bool = False,
        dry_run: bool = False,
        depends_on: list = None,
        delay: Union[datetime, timedelta] = None,
        queue: str = None,
        walltime: timedelta = None,
        storage: list = None,
        variables: dict = None,
        **context,
    ):
        """Submit a job to the scheduler.

        Parameters
        ----------
        job_script : Union[str, Path]
            Path to the script.
        directives : list, optional
            List of complete directives to submit, by default list()
        render : bool, optional
            Render the job script from a template, by default False
        dry_run : bool, optional
            Return rather than executing the command, by default False
        depends_on : list, optional
            List of job IDs with successful exit on which this job depends, by default list()
        delay: Union[datetime, timedelta]
            Delay the start of this job until specific date or interval, by default None
        queue: str, optional
            Queue on which to submit the job, by default None
        walltime: timedelta, optional
            Walltime expressed as a timedelta, by default None
        storage: list, optional
            List of storage mounts to apply, by default None
        variables: dict, optional
            Key/value environment variable pairs added to the qsub command.
        **context:
            Additional key/value pairs to be added to command/jobscript interpolation

        Returns
        -------
        Job : hpcpy.job.Job
            Job object.
        """
        # Initialise the directives to an empty list
        directives = directives if isinstance(directives, list) else []

        # Add job depends
        if depends_on:

            # Normalise to a list of strs
            depends_on = super()._normalise_depends_on(depends_on)

            directives = self._interpolate_directive(
                directives,
                "depends_on",
                depends_on_str=":".join(depends_on),
            )

        # Add delay (specified time or delta)
        if delay:
            delay_directive = self._assemble_delay_directive(delay, DELAY_DIRECTIVE_FMT)
            directives.append(delay_directive)

        # Add queue
        if queue:
            directives = self._interpolate_directive(directives, "queue", queue=queue)
            context["queue"] = queue

        # Add walltime
        if walltime:
            _walltime = str(walltime)
            directives.append(f"-l walltime={_walltime}")
            context["walltime"] = _walltime

        # Add storage
        if storage:
            storage_str = "+".join(storage)
            directives.append(f"-l storage={storage_str}")
            context["storage"] = storage
            context["storage_str"] = storage_str

        # Add variables
        if isinstance(variables, dict) and len(variables) > 0:
            directives.append(self._render_variables(variables))

        # Call the super
        job_or_cmd = super().submit(
            job_script=job_script,
            directives=directives,
            render=render,
            dry_run=dry_run,
            **context,
        )

        # Return the command if requested
        if dry_run:
            return job_or_cmd

        # Point to this client from the job and switch on auto_update
        job_or_cmd.set_client(self)
        job_or_cmd._auto_update = True

        # Return the job object
        return job_or_cmd

    def _parse_status(self, raw, job_id):
        """Extract the status from the raw response.

        Parameters
        ----------
        raw : str
            Raw response from the scheduler.
        job_id : str
            Job ID required to extract status from the response.

        Returns
        -------
        str
            Status code.
        """
        # Convert to JSON
        parsed = json.loads(raw)

        # Get the status out of the job ID
        native_full = parsed.get("Jobs").get(job_id)
        native_status = native_full.get("job_state")

        # Set the generic status attribute
        generic_status = None

        for s in self.statuses:
            if native_status == s.short:
                generic_status = s.status
                break

        # Return the generic status
        return generic_status, native_full
