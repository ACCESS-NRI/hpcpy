"""Client tests."""

import pytest
from hpcpy import get_client
import hpcpy.constants as hc
import hpcpy.utilities as hu
import os


@pytest.fixture(autouse=True)
def environment():
    os.environ["HPCPY_DEV_MODE"] = "1"


@pytest.fixture()
def client():
    return get_client()


def test_get_job_script_filename(client):
    """Test get_job_script_filename."""
    hash_length = 5
    input_filename = "file.sh"
    result = client._get_job_script_filename(
        f"/path/to/{input_filename}", hash_length=hash_length
    )
    assert result != input_filename
    assert len(result) == len(input_filename) + hash_length + 1  # underscore


def test_submit(client):
    """Test submit."""
    result = client.submit("test.txt")
    assert result == "12345"


def test_status(client):
    """Test status."""
    result = client.status("12345")
    assert result == hc.STATUS_QUEUED


def test_delete(client):
    """Test delete."""
    result = client.delete("12345")
    assert result == "DELETED"


def test_render_job_script(client):
    """Test rendering the job script."""

    # Write it out.
    template_filepath = hu.get_installed_root() / "data" / "test" / "test.j2"
    rendered_filepath = client._render_job_script(template_filepath, myarg="world")

    rendered = open(rendered_filepath, "r").read().strip()
    assert rendered == "hello world"


def test_clean_rendered_job_scripts(client):
    """Test cleaning out the rendered job scripts."""

    # Run the clean command
    client.job_script_expiry = "0h"

    # Ensure that the job script directory is empty
    client._clean_rendered_job_scripts()
    rjs = client.list_rendered_job_scripts()

    assert len(rjs) == 0
