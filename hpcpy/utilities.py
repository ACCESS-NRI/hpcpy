"""Utilities."""

import subprocess as sp
import jinja2 as j2
import jinja2.meta as j2m
from pathlib import Path
from importlib import resources
from hpcpy.exceptions import ShellException
import logging
import sys
import shlex
import json


def shell(
    cmd, check=True, capture_output=True, env=None, **kwargs
) -> sp.CompletedProcess:
    """Execute a shell command.

    Parameters
    ----------
    cmd : str
        Command
    check : bool, optional
        Check output, by default True
    capture_output : bool, optional
        Capture output, by default True
    env : dict, optional
        Dictionary of environment variables to add to the execution.

    Returns
    -------
    subprocess.CompletedProcess
        Process object.

    Raises
    ------
    hpcpy.exceptions.ShellException :
        When the shell call fails.
    """
    try:
        return sp.run(
            shlex.split(cmd),
            shell=False,
            check=check,
            capture_output=capture_output,
            env=env,
            **kwargs,
        )
    except sp.CalledProcessError as ex:
        raise ShellException(ex)


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

    Raises
    ------
    jinja2.exceptions.UndefinedError :
        When a variable is undeclared nor has a default applied.
    """

    # Set up the rendering environment
    env = j2.Environment(loader=j2.BaseLoader(), undefined=j2.DebugUndefined)

    # Render the template
    _template = env.from_string(template)
    rendered = _template.render(**kwargs)

    # Look for undefined variables (those that remain even after conditionals)
    ast = env.parse(rendered)
    undefined = j2m.find_undeclared_variables(ast)

    if undefined:
        raise j2.UndefinedError(f"The following variables are undefined: {undefined!r}")

    return rendered


def interpolate_file_template(filepath, **kwargs) -> str:
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
    template = open(filepath, "r").read()
    return interpolate_string_template(template, **kwargs)


def get_installed_root() -> Path:
    """Get the installed root of the hpcpy installation.

    Returns
    -------
    Path
        Path to the installed root.

    """
    return Path(resources.files("hpcpy"))


def ensure_list(obj) -> list:
    """Ensure the object provided is a list.

    Parameters
    ----------
    obj : mixed
        Object of any type
    """
    return obj if isinstance(obj, list) else [obj]


def decode_status(status_json):
    """Decode the status_json (byte) string.

    Parameters
    ----------
    status_json : bytes
        Byte string.

    Returns
    -------
    dict
        Status dictionary.
    """
    return json.loads(status_json.decode("utf-8"))


def encode_status(status_json):
    """Encode status_json.

    Parameters
    ----------
    status_json : dict
        Status dictionary.

    Returns
    -------
    bytes
        Bytes array.
    """
    return json.dumps(status_json).encode()

def get_logger(name="hpcpy", level="debug"):
    """Get a logger instance.

    Parameters
    ----------
    name : str, optional
        Name, by default 'benchcab'
    level : str, optional
        Level, by default 'debug'

    Returns
    -------
    logging.Logger
        A logger instance guaranteed to be singleton if called with the same params.

    """
    # Get or create a logger
    logger = logging.getLogger(name)

    # Workaround for native singleton property.
    # NOTE: This will ignore the provided level and give you whatever was first set.
    if logger.level != logging.NOTSET:
        return logger

    # Set the level
    level = getattr(logging, level.upper())
    logger.setLevel(level)

    # Create the formatter
    log_format = (
        "%(asctime)s - %(levelname)s - %(module)s.%(filename)s:%(lineno)s - %(message)s"
    )
    formatter = logging.Formatter(log_format)

    # Create/set the handler to point to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger