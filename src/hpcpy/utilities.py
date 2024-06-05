"""Utilities."""
import subprocess as sp
from jinja2 import BaseLoader, Environment
from pathlib import Path
from importlib import resources


def shell(cmd, shell=True, check=True, capture_output=True, **kwargs):
    """Execute a shell command.

    Parameters
    ----------
    cmd : str
        Command
    shell : bool, optional
        Execute as shell, by default True
    check : bool, optional
        Check output, by default True
    capture_output : bool, optional
        Capture output, by default True

    Returns
    -------
    subprocess.CompletedProcess
        Process object.
    
    Raises
    ------
    subprocess.CalledProcessError
    """
    return sp.run(
        cmd,
        shell=shell,
        check=check,
        capture_output=capture_output,
        **kwargs
    )


def interpolate_string_template(template, **kwargs) -> str:
    """Interpolate into a string template.

    Parameters
    ----------
    template : str
        Template.

    Returns
    -------
    str
        Interpolated template.
    """
    _template = Environment(loader=BaseLoader()).from_string(template)
    return _template.render(**kwargs)


def interpolate_file_template(filepath, **kwargs):
    """Interpolate directly from a file template.

    Parameters
    ----------
    filepath : Path
        Path to the file.

    Returns
    -------
    str
        Interpolated template.
    """
    template = open(filepath, 'r').read()
    return interpolate_string_template(template, **kwargs)

def get_installed_root() -> Path:
    """Get the installed root of the benchcab installation.

    Returns
    -------
    Path
        Path to the installed root.

    """
    return Path(resources.files("hpcpy"))