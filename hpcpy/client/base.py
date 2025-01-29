"""Base client object."""

from hpcpy.utilities import shell, interpolate_file_template
import hpcpy.constants as hc
from random import choice
from string import ascii_uppercase
import os
from datetime import datetime, timedelta
import pandas as pd


class BaseClient:
    """A base class from which all others inherit."""

    def __init__(
        self,
        cmd_templates,
        directive_templates,
        statuses,
        status_attribute,
        job_script_expiry="1H",
        delay_directive_fmt="-a %Y%m%d%H%M.%S",
        depends_directive_fmt="-W depend=afterok:{depends_on_str}",
    ):
        """Constructor.

        Parameters
        ----------
        cmd_templates : dict
            Dictionary of command templates.
        statuses : list
            List of statuses.
        status_attribute : str
            Attribute to use for status lookup.
        job_script_expiry : str, optional
            Job script expiry interval, by default "1H"
        """

        # Set the command templates
        self.cmd_templates = cmd_templates
        self.job_script_expiry = job_script_expiry
        self.statuses = statuses
        self.status_attribute = status_attribute
        self.delay_directive_fmt = delay_directive_fmt
        self.depends_directive_fmt = depends_directive_fmt
        self.directive_templates = directive_templates

    def _clean_rendered_job_scripts(self) -> None:
        """Clean the rendered job scripts from the JOB_SCRIPT_DIR."""

        # Disable option
        if self.job_script_expiry is None:
            return

        # List the rendered files.
        rendered_job_scripts = self.list_rendered_job_scripts()

        # Work out the threshold
        now = datetime.now()
        threshold = now - pd.to_timedelta(self.job_script_expiry).to_pytimedelta()

        for rjs in rendered_job_scripts:

            # Ensure actually a file
            if not os.path.isfile(rjs):
                continue

            # Get the modified time of the file, check threshold and delete
            mod_time = datetime.fromtimestamp(os.path.getmtime(rjs))
            if mod_time <= threshold:
                os.remove(rjs)

    def list_rendered_job_scripts(self) -> list:
        """List the rendered job scripts in the JOB_SCRIPT_DIR

        Returns
        -------
        list
            List of paths to job scripts.
        """
        return [hc.JOB_SCRIPT_DIR / rjs for rjs in os.listdir(hc.JOB_SCRIPT_DIR)]

    def submit(
        self,
        job_script,
        directives=list(),
        render=False,
        dry_run=False,
        env=None,
        **context,
    ) -> str:
        """Submit the job script.


        Parameters
        ----------
        job_script : path-like
            Path to the job script or template if render=True
        render : bool
            Use the job_script as a template and render **context into it.
        dry_run : bool
            Return the command that would have been executed.
        env : dict
            Append the specified dictionary to the execution environment
        **context :
            Additional key/value pairs interpolated into the command and job script.

        Returns
        -------
        str
            Command response text (job id).
        """
        if render:
            _job_script = self._render_job_script(job_script, **context)

        else:
            _job_script = job_script

        # Add the directives to the interpolation context (will return blank string if nothing there)
        context["directives"] = self._render_directives(directives)

        context["job_script"] = _job_script
        cmd = self.cmd_templates["submit"].format(**context)

        # Just return the command string for the user without submitting
        if dry_run:
            return cmd

        result = self._shell(cmd)
        return result

    def status(self, job_id):
        """Check the status of a job.

        Parameters
        ----------
        job_id : str
            Job ID.
        """
        cmd = self.cmd_templates["status"].format(job_id=job_id)
        result = self._shell(cmd)
        return result

    def delete(self, job_id):
        """Delete/cancel a job.

        Parameters
        ----------
        job_id : str
            Job ID.
        """
        cmd = self.cmd_templates["delete"].format(job_id=job_id)
        result = self._shell(cmd)
        return result

    def is_queued(self, job_id):
        """Check if the job is queued.

        Parameters
        ----------
        job_id : str
            Job ID.

        Returns
        -------
        bool
            True if queued, False otherwise.
        """
        return self.status(job_id) == hc.STATUS_QUEUED

    def is_running(self, job_id):
        """Check if the job is running.

        Parameters
        ----------
        job_id : str
            Job ID.

        Returns
        -------
        bool
            True if running, False otherwise.
        """
        return self.status(job_id) == hc.STATUS_RUNNING

    def _shell(self, cmd, decode=True, env=None):
        """Generic shell interface to capture exceptions.

        Parameters
        ----------
        cmd : str
            Command to run.
        decode : bool
            Automatically decode response with utf-8, defaults to True
        env : dict, optional
            Add environment variables to the command.
        Raises
        ------
        hpcpy.exceptions.ShellException :
            When the underlying shell call fails.

        Returns
        -------
        str
            Result from the underlying called command.
        """
        result = shell(cmd, env=env)

        if decode:
            result = result.stdout.decode("utf8").strip()

        return result

    def _get_job_script_filename(self, filepath, hash_length=8) -> str:
        """Generate a script filename with a random prefix.

        Parameters
        ----------
        filepath : str
            Path to the file.
        hash_length : int, optional
            Length of the random hash, by default 8

        Returns
        -------
        str
            Hash-prefixed filename.
        """
        filename, ext = os.path.splitext(filepath)
        filename = os.path.basename(filename)
        _hash = "".join(choice(ascii_uppercase) for i in range(hash_length))
        return f"{filename}_{_hash}{ext}"

    def _render_job_script(self, template, **context):
        """Render a job script.

        Parameters
        ----------
        template : str, path-like.
            Path to the template.

        Returns
        -------
        str
            Path to the rendered job script.
        """

        # Render the template
        _rendered = interpolate_file_template(template, **context)

        # Generate the output filepath
        os.makedirs(hc.JOB_SCRIPT_DIR, exist_ok=True)
        output_filename = self._get_job_script_filename(template)
        output_filepath = hc.JOB_SCRIPT_DIR / output_filename

        # Write it out
        with open(output_filepath, "w") as fo:
            fo.write(_rendered)

        return output_filepath

    def _render_directives(self, directives):
        """Render the directives into a single string for command interpolation.

        Parameters
        ----------
        directives : list
            List of scheduler-compliant directives. One per item.

        Returns
        -------
        str
            Rendered directives, or blank string.
        """

        # Render blank directives if empty
        if not directives:
            return ""

        return " " + " ".join(directives)

    def hold(self, job_id):
        """Hold a job.

        Parameters
        ----------
        job_id : str
            Job ID.
        """
        cmd = self.cmd_templates["hold"].format(job_id=job_id)
        result = self._shell(cmd)
        return result

    def release(self, job_id):
        """Release a job.

        Parameters
        ----------
        job_id : str
            Job ID.
        """
        cmd = self.cmd_templates["release"].format(job_id=job_id)
        result = self._shell(cmd)
        return result

    def _assemble_delay_directive(self, delay) -> str:
        """Assemble the delay directive for the scheduler.

        Parameters
        ----------
        delay : datetime or timedelta
            Either a specific datetime or delta from now.

        Returns
        -------
        str
            Formatted delay directive for the current scheduler.

        Raises
        ------
        ValueError
            When the delay argument is incorrect or puts the job in the past.
        """

        current_time = datetime.now()
        delay_str = None

        if isinstance(delay, datetime) and delay > current_time:
            delay_str = delay.strftime(self.delay_directive_fmt)

        elif isinstance(delay, timedelta) and (current_time + delay) > current_time:
            delay_str = (current_time + delay).strftime(self.delay_directive_fmt)
        else:
            raise ValueError(
                "Job submission delay argument either incorrect or puts the job in the past."
            )

        return self.directive_templates["delay"].format(delay_str=delay_str)

    def _interpolate_directive(self, directives, key, **kwargs):

        directives.append(self.directive_templates[key].format(**kwargs))
        return directives

    # def _assemble_depends_directive(self, depends_on_str) -> str:
    #     """Assemble the depends directive for the scheduler.

    #     Parameters
    #     ----------
    #     depends_on_str : str
    #         List of job IDs to depend on.

    #     Returns
    #     -------
    #     str
    #         Formatted depends directive for the current scheduler.
    #     """
    #     # depends_on_str = ":".join(ensure_list(depends_on))
    #     return self.depends_directive_fmt.format(depends_on_str=depends_on_str)
