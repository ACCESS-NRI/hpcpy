from hpcpy.client.base import BaseClient
import hpcpy.constants as hc
import hpcpy.utilities as hu
from datetime import datetime, timedelta
from typing import Union
import json
from pathlib import Path


class PBSClient(BaseClient):

    def __init__(self, *args, **kwargs):

        # Set up the templates
        super().__init__(
            tmp_submit=hc.PBS_SUBMIT, tmp_status=hc.PBS_STATUS, tmp_delete=hc.PBS_DELETE
        )

    def status(self, job_id):

        # Get the raw response
        raw = super().status(job_id=job_id)

        # Convert to JSON
        parsed = json.loads(raw)

        # Get the status out of the job ID
        _status = parsed.get("Jobs").get(job_id).get("job_state")
        return hc.PBS_STATUSES[_status]
    
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
            Key/value pairs added to the qsub command.
        **context:
            Additional key/value pairs to be added to command/jobscript interpolation
        """

        directives = directives if isinstance(directives, list) else list()

        # Add job depends
        if depends_on:
            depends_on = hu.ensure_list(depends_on)
            directives.append("-W depend=afterok:" + ":".join(depends_on))

        # Add delay (specified time or delta)
        if delay:

            current_time = datetime.now()
            delay_str = None

            if isinstance(delay, datetime) and delay > current_time:
                delay_str = delay.strftime("%Y%m%d%H%M.%S")

            elif isinstance(delay, timedelta) and (current_time + delay) > current_time:
                delay_str = (current_time + delay).strftime("%Y%m%d%H%M.%S")
            else:
                raise ValueError(
                    "Job submission delay argument either incorrect or puts the job in the past."
                )

            # Add the delay directive
            directives.append(f"-a {delay_str}")

        # Add queue
        if queue:
            directives.append(f"-q {queue}")
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
        return super().submit(
            job_script=job_script,
            directives=directives,
            render=render,
            dry_run=dry_run,
            **context,
        )
