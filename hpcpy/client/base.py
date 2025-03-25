"""Base client object."""

from hpcpy.utilities import shell, interpolate_file_template, get_logger
from hpcpy.job import Job
import hpcpy.constants as hc
from random import choice
from string import ascii_uppercase
import os
from datetime import datetime, timedelta
from pandas import to_timedelta


class BaseClient:
    """A base class from which all others inherit.

    Parameters
    ----------
    cmd_templates : dict
        Dictionary of command templates.
    directive_templates : dict
        Dictionary of directive templates.
    statuses : list
        List of statuses.
    status_attribute : str
        Attribute to use for status lookup.
    job_script_expiry : str, optional
        Job script expiry interval, by default "1H"
    delay_directive_fmt : str, optional
        Delay directive format.
    depands_directive_fmt : str, optional
        Depends directive format.
    """

    def __init__(
        self,
        cmd_templates,
        directive_templates,
        statuses,
        status_attribute,
        job_script_expiry="1H",
    ):
        # Set the command templates etc.
        self.cmd_templates = cmd_templates
        self.job_script_expiry = job_script_expiry
        self.statuses = statuses
        self.status_attribute = status_attribute
        self.directive_templates = directive_templates

        # Set up a shared logger
        self._logger = get_logger()

    def _clean_rendered_job_scripts(self, force=False) -> None:
        """Clean the rendered job scripts from the JOB_SCRIPT_DIR.

        Parameters
        ----------
        force : bool, optional
            Clean regardless of expiry, by default False
        """
        # Disable option
        if self.job_script_expiry is None and force is False:
            return

        self._logger.debug(f"Cleaning rendered jobscripts (force={force}).")

        # List the rendered files.
        rendered_job_scripts = self.list_rendered_job_scripts()

        # Work out the threshold
        now = datetime.now()
        threshold = now - to_timedelta(self.job_script_expiry).to_pytimedelta()

        for rjs in rendered_job_scripts:

            # Ensure actually a file
            if not os.path.isfile(rjs):
                continue

            # Get the modified time of the file, check threshold and delete
            mod_time = datetime.fromtimestamp(os.path.getmtime(rjs))

            # Check if the file has expired
            if mod_time <= threshold or force == True:
                self._logger.debug(f"Removing {rjs}")
                os.remove(rjs)

    def list_rendered_job_scripts(self) -> list:
        """List the rendered job scripts in the JOB_SCRIPT_DIR.

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
        env=dict(),
        **context,
    ) -> str:
        """Submit the job script.

        Parameters
        ----------
        job_script : path-like
            Path to the job script or template if render=True
        render : bool
            Use the job_script as a template and render **context into it.
        directives : list
            List of directives to add to the command.
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
            self._logger.debug("Rendering job script.")
            _job_script = self._render_job_script(job_script, **context)
        else:
            _job_script = job_script

        self._logger.debug(f"Using job script as {_job_script}")

        # Add the directives to the interpolation context (will return blank string if nothing there)
        _directives = self._render_directives(directives)
        context["directives"] = _directives
        self._logger.debug(f"Directives rendered as {directives}")

        # Add the job script to the context
        context["job_script"] = _job_script

        # Assemble the submit command
        cmd = self.cmd_templates["submit"].format(**context)
        self._logger.debug("Command rendered as:")
        self._logger.debug(cmd)

        # Just return the command string for the user without submitting
        if dry_run:
            self._logger.debug("dry_run requested, returning submission command.")
            return cmd

        # Attach the user environment to the call
        self._logger.debug("Updating user environment.")
        _env = os.environ
        _env.update(env)

        # Submit
        self._logger.debug("Submitting to the shell.")
        result = self._shell(cmd, env=_env)

        # Job ID is the last part of the returned string for either client
        job_id = result.split()[-1]

        # Return the job object, but switch off auto_update so it doesn't attempt to get status
        return Job(job_id, client=None, auto_update=False)

    def status(self, job_id):
        """Check the status of a job.

        Parameters
        ----------
        job_id : str
            Job ID.

        Returns
        -------
        str
            Command response text.
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

        Returns
        -------
        str
            Command response text.
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
        """Run the shell utility for the given command.

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
        """Generate a script filename with a random suffix.

        Parameters
        ----------
        filepath : str
            Path to the file.
        hash_length : int, optional
            Length of the random hash, by default 8

        Returns
        -------
        str
            Hash-suffixed filename.
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
        **context :
            Key/value pairs to be interpolated into the script.

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

        Returns
        -------
        str
            Command response text.
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

        Returns
        -------
        str
            Command response text.
        """
        cmd = self.cmd_templates["release"].format(job_id=job_id)
        result = self._shell(cmd)
        return result

    def _assemble_delay_directive(self, delay, delay_directive_fmt) -> str:
        """Assemble the delay directive for the scheduler.

        Parameters
        ----------
        delay : datetime or timedelta
            Either a specific datetime or delta from now.
        delay_directive_fmt : str
            Delay directive format.

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
            delay_str = delay.strftime(delay_directive_fmt)

        elif isinstance(delay, timedelta) and (current_time + delay) > current_time:
            delay_str = (current_time + delay).strftime(delay_directive_fmt)
        else:
            raise ValueError(
                "Job submission delay argument either incorrect or puts the job in the past."
            )

        return self.directive_templates["delay"].format(delay_str=delay_str)

    def _interpolate_directive(self, directives, key, **kwargs):
        """Interpolate a directive into the keyed template and add to the list.

        Parameters
        ----------
        directives : list
            Directives
        key : str
            Key to the template to interpolate into.
        **kwargs :
            Key/value pairs to use in interpolation.

        Returns
        -------
        list
            Updated directives list.
        """
        directives.append(self.directive_templates[key].format(**kwargs))
        return directives
