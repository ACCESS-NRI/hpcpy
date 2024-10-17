"""Tests for utilities.py"""

import hpcpy.utilities as hu
import hpcpy.exceptions as hx


def test_interpolate_string_template():
    """Test interpolating a string template."""
    assert hu.interpolate_string_template("hello {{arg}}", arg="world") == "hello world"


def test_shell_exception():
    """Test that error messaging is being raised to the user."""
    try:
        hu.shell("blah")
    except hx.ShellException as ex:
        assert ex.__str__() == "Error 127: /bin/sh: blah: command not found\n"
