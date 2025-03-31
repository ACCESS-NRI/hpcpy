"""SLURM Client."""

from hpcpy.client.base import BaseClient
from hpcpy.constants.slurm import COMMANDS, STATUSES, DIRECTIVES, DELAY_DIRECTIVE_FMT
from datetime import datetime, timedelta
from typing import Union
import json
from pathlib import Path
import os


class SlurmClient(BaseClient):
    """SLURM interface.

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
        formatted = ",".join([f"{k}={v}" for k, v in variables.items()])
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
        variables: dict = dict(),
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
        variables: dict, optional
            Key/value environment variable pairs added to the qsub command.
        **context:
            Additional key/value pairs to be added to command/jobscript interpolation

        Returns
        -------
        Job : hpcpy.job.Job
            Job object.
        """
        # Get a logger from the parent
        self._logger.debug(f"Submitting {job_script}")

        # Initialise directives
        directives = directives if isinstance(directives, list) else []

        # Add job depends
        if depends_on:

            self._logger.debug("Job dependency specified.")

            # Normalise depends_on to strs
            depends_on = super()._normalise_depends_on(depends_on)

            directives = self._interpolate_directive(
                directives,
                "depends_on",
                depends_on_str=":".join(depends_on),
            )

        # Add delay (specified time or delta)
        if delay:
            self._logger.debug("Delay specified.")
            delay_directive = self._assemble_delay_directive(delay, DELAY_DIRECTIVE_FMT)
            directives.append(delay_directive)

        # Add queue
        if queue:
            self._logger.debug(f"Queue specified ({queue})")
            directives = self._interpolate_directive(directives, "queue", queue=queue)
            context["queue"] = queue

        # Add walltime
        if walltime:
            walltime_str = str(int(walltime.total_seconds() / 60.0))
            self._logger.debug(f"Walltime specified ({walltime_str})")
            directives = self._interpolate_directive(
                directives, "walltime", walltime_str=walltime_str
            )

        # Update the environment with the variables (which is how Slurm does job variables)
        self._logger.debug("Updating environment.")
        _env = os.environ.copy()
        _env.update(variables)

        # Call the super submit
        self._logger.debug("Submitting via parent class.")
        job_or_cmd = super().submit(
            job_script=job_script,
            directives=directives,
            render=render,
            dry_run=dry_run,
            env=_env,
            **context,
        )

        # Return the command from the super
        if dry_run:
            self._logger.debug("Dry run requested, returning fully-formed command.")
            return job_or_cmd

        # Point to this client in the job object and switch on auto_update
        job_or_cmd.set_client(self)
        job_or_cmd._auto_update = True

        # Get the job ID out of the return string
        self._logger.debug(f"job_id={job_or_cmd.id}")

        # Return the job object
        return job_or_cmd

    def _parse_status(self, raw, job_id):
        """Extract the statue from the raw response.

        Parameters
        ----------
        raw : str
            Raw response from the scheduler.
        job_id : str
            Job ID.

        Returns
        -------
        generic_status : str
            Generic status code.
        native_full : dict
            Full native status dictionary.
        """
        # Parse the response
        parsed = json.loads(raw)

        # Get the status from the first job
        native_full = parsed.get("jobs")[0]
        native_status = native_full.get("job_state")[0]

        # Set the default generic status to None
        generic_status = None

        # Look up the generic status
        for s in self.statuses:
            if native_status == s.long:
                generic_status = s.status
                break

        return generic_status, native_full
