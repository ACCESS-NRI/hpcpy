"""Tests for utilities.py"""

import hpcpy.utilities as hu
import hpcpy.exceptions as hx


def test_interpolate_string_template():
    """Test interpolating a string template."""
    assert hu.interpolate_string_template("hello {{arg}}", arg="world") == "hello world"


def test_shell_exception():
    """Test that error messaging is being raised to the user."""
    try:
        hu.shell("bash blah")
    except hx.ShellException as ex:

        expected = f"Error {ex.returncode}: {ex.stderr}"
        assert ex.__str__() == expected
