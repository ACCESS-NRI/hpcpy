"""Custom exception classes."""

import subprocess as sp


class NoClientException(Exception):
    """Exception class raised when no scheduler can be detected."""

    def __init__(self):
        super().__init__(
            "Unable to detect scheduler type, cannot determine client type."
        )


class ShellException(Exception):
    """Exception class to improve readability of the subprocess.CalledProcessError.

    Parameters
    ----------
    called_process_error : sp.CalledProcessError
        Source subprocess.CalledError

    """

    def __init__(self, called_process_error: sp.CalledProcessError):
        self.returncode = called_process_error.returncode
        self.cmd = called_process_error.cmd[0]
        self.stdout = called_process_error.stdout.decode()
        self.stderr = called_process_error.stderr.decode()
        self.output = called_process_error.output

    def __str__(self):
        """Improved string representation of the error message.

        Returns
        -------
        str
            Improved error messaging

        """
        return f"Error {self.returncode}: {self.stderr}"
