"""Utilities."""

import subprocess as sp
import Jinja2 as j2
import Jinja2.meta as j2m
from pathlib import Path
from importlib import resources


def shell(
    cmd, shell=True, check=True, capture_output=True, **kwargs
) -> sp.CompletedProcess:
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
        cmd, shell=shell, check=check, capture_output=capture_output, **kwargs
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
    """Get the installed root of the benchcab installation.

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
