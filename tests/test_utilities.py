"""Tests for utilities.py"""

import hpcpy.exceptions as hx
import hpcpy.utilities as hu


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


def test_extract_storage_directive():
    """Test to extract storage directives from various paths."""

    project = "abc123"

    # gdata
    assert f"gdata/{project}" == hu.extract_storage_directive(
        f"/g/data/{project}/test/test"
    )

    # scratch
    assert f"scratch/{project}" == hu.extract_storage_directive(
        f"/scratch/{project}/test/test"
    )

    # None
    assert None == hu.extract_storage_directive("should/be/none")
