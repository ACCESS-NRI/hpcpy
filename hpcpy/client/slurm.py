"""SLURM client"""

from hpcpy.client.base import BaseClient
from hpcpy.job import Job
from hpcpy.constants.slurm import COMMANDS, STATUSES, DIRECTIVES
import hpcpy.utilities as hu
from datetime import datetime, timedelta
from typing import Union
import json
from pathlib import Path


class SlurmClient(BaseClient):

    def __init__(self, *args, **kwargs):

        # Set up the templates
        super().__init__(
            cmd_templates=COMMANDS,
            directive_templates=DIRECTIVES,
            statuses=STATUSES,
            status_attribute="short",
            delay_directive_fmt="%Y-%m-%dT%H:%M:%S",
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
        variables: dict, optional
            Key/value environment variable pairs added to the qsub command.
        **context:
            Additional key/value pairs to be added to command/jobscript interpolation

        Returns
        -------
        Job : hpcpy.job.Job
            Job object.
        """

        directives = directives if isinstance(directives, list) else []

        # Add job depends
        if depends_on:
            directives = self._interpolate_directive(
                directives,
                "depends_on",
                depends_on_str=":".join(hu.ensure_list(depends_on)),
            )

        # Add delay (specified time or delta)
        if delay:
            delay_directive = self._assemble_delay_directive(delay)
            directives.append(delay_directive)

        # Add queue
        if queue:
            directives = self._interpolate_directive(directives, "queue", queue=queue)
            context["queue"] = queue

        # Add walltime
        if walltime:
            walltime_str = str(int(walltime.total_seconds() / 60.0))
            directives = self._interpolate_directive(
                directives, "walltime", walltime_str=walltime_str
            )

        # Call the super
        job_id = super().submit(
            job_script=job_script,
            directives=directives,
            render=render,
            dry_run=dry_run,
            env=variables,
            **context,
        )

        if dry_run:
            return job_id

        # Return the job object
        return Job(id=job_id, client=self)

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


# from hpcpy.client.base import BaseClient
# import hpcpy.constants as hc
# from typing import Union
# from pathlib import Path
# from datetime import datetime, timedelta
# import json


# class SlurmClient(BaseClient):

#     def __init__(self, *args, **kwargs):
#         super().__init__(
#             cmd_templates=hc.SLURM_COMMANDS,
#             statuses=hc.SLURM_STATUSES,
#             directive_templates=hc.SLURM_DIRECTIVES,
#             status_attribute="long",
#             *args, **kwargs
#         )

#     def submit(
#         self,
#         job_script: Union[str, Path],
#         directives: list = None,
#         render: bool = False,
#         dry_run: bool = False,
#         depends_on: list = None,
#         delay: Union[datetime, timedelta] = None,
#         queue: str = None,
#         walltime: timedelta = None,
#         storage: list = None,
#         variables: dict = None,
#         **context,
#     ):
#         directives = directives if isinstance(directives, list) else []

#         # Add dependencies
#         if depends_on:
#             directives.append(f"--dependency=afterok:" + ":".join(depends_on))


#     def status(self, job_id):
#         """Get the statys of a job with id job_id.

#         Parameters
#         ----------
#         job_id : str
#             Job ID.

#         Returns
#         -------
#         str
#             Generic status code.
#         """
#         raw = super().status(job_id=job_id)
#         return self._parse_status(raw, job_id)

#     def _parse_status(self, raw, job_id):
#         """Extract the statue from the raw response.

#         Parameters
#         ----------
#         raw : str
#             Raw response from the scheduler.
#         job_id : str
#             Job ID.

#         Returns
#         -------
#         generic_status : str
#             Generic status code.
#         native_full : dict
#             Full native status dictionary.
#         """

#         # Parse the response
#         parsed = json.loads(raw)

#         # Get the status from the first job
#         native_full = parsed.get("jobs")[0]
#         native_status = native_full.get("job_state")[0]

#         # Set the default generic status to None
#         generic_status = None

#         # Look up the generic status
#         for s in self.statuses:
#             if native_status == s.long:
#                 generic_status = s.status
#                 break

#         return generic_status, native_full
