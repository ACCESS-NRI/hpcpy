"""PBS implementation."""

from hpcpy.client.base import BaseClient
from hpcpy.constants.pbs import (
    COMMANDS,
    DIRECTIVES,
    STATUSES,
    DELAY_DIRECTIVE_FMT,
    DEPENDENCY,
)
from datetime import datetime, timedelta
from typing import Union
import json
from pathlib import Path
from shlex import quote
import hpcpy.utilities as hu


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
            dependency_map=DEPENDENCY,
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
        module_purge: bool = False,
        module_use: str = None,
        modules: Union[str, list] = None,
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
            List of dependencies. Each element is a Job/str (assumed state
            "afterok"), or a (state, Job or str) tuple, by default list()
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
        module_purge: bool, optional
            Add a `module purge` command to `{{ modules_head }}`, by default False.
        module_use: str optional
            Path(s) to supply to a `module use` command in `{{ modules_head }}`.
        modules: Union[str,list], optional
            Modules to load with `module load` in `{{ modules_head }}`.
        **context:
            Additional key/value pairs to be added to command/jobscript interpolation.

        Returns
        -------
        Job : hpcpy.job.Job
            Job object.
        """
        # Initialise the directives to an empty list
        directives = directives if isinstance(directives, list) else []

        # Add job depends
        if depends_on:

            # Normalise into a scheduler-native dependency string
            depends_on_str = super()._normalise_depends_on(depends_on)

            directives = self._interpolate_directive(
                directives,
                "depends_on",
                depends_on_str=depends_on_str,
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

        # Generate modules_head
        modules_head = self._generate_modules_head(module_purge, module_use, modules)
        if modules_head:
            context["modules_head"] = modules_head

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

    def _generate_modules_head(
        self,
        module_purge: bool,
        module_use: Union[str, list],
        modules: Union[str, list],
    ) -> str:
        """Generate `{{ modules_head }}` template tag for job submission scripts.

        Parameters
        ----------
        module_purge : bool
            Whether to add a `module purge` at the start of the tag.
        module_use : Union[str, list]
            A string path or list of paths to populate `module use` commands.
        modules : Union[str, list]
            A string module or list of modules to populate `module load` commands.

        Returns
        -------
        str
            A formatted header block.
        """
        modules_head = list()

        # Add the purge
        if module_purge:
            modules_head.append("module purge")

        # The the use
        if module_use:
            for _module_use in hu.ensure_list(module_use):
                modules_head.append(f"module use {_module_use}")

        # Add each module
        if modules:
            for module in hu.ensure_list(modules):
                modules_head.append(f"module load {module}")

        # Bail out for empty head
        if len(modules_head) == 0:
            return ""

        return "\n".join(modules_head)
