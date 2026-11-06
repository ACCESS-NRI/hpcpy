"""Client tests."""

import os
import tempfile as tf

import pytest

import hpcpy.utilities as hu
from hpcpy import PBSClient


@pytest.fixture(autouse=True)
def environment():
    os.environ["HPCPY_DEV_MODE"] = "1"


@pytest.fixture()
def client():
    return PBSClient()


@pytest.fixture()
def template_filepath():
    return hu.get_installed_root() / "data" / "test" / "test.j2"


def test_get_job_script_filename(client):
    """Test get_job_script_filename."""
    hash_length = 5
    input_filename = "file.sh"
    result = client._get_job_script_filename(
        f"/path/to/{input_filename}", hash_length=hash_length
    )
    assert result != input_filename
    assert len(result) == len(input_filename) + hash_length + 1  # underscore


def test_render_job_script(client, template_filepath):
    """Test rendering the job script."""

    # Write it out.
    rendered_filepath = client._render_job_script(template_filepath, myarg="world")

    rendered = open(rendered_filepath, "r").read().strip()
    assert rendered == "hello world"


def test_clean_rendered_job_scripts(client):
    """Test cleaning out the rendered job scripts."""

    # Run the clean command
    client.job_script_expiry = "0h"

    # Ensure that the job script directory is empty
    client.clean_rendered_job_scripts(force=True)
    rjs = client.list_rendered_job_scripts()

    assert len(rjs) == 0


def test_custom_job_script_dir(template_filepath):
    """Test that the custom job script dir actually writes where it is expected."""

    # Use a temporary directory
    with tf.TemporaryDirectory() as tmpdir:

        client = PBSClient(job_script_dir=tmpdir)

        # Check it lands in the right place
        rendered_filepath = client._render_job_script(template_filepath, myarg="world")
        assert os.path.dirname(rendered_filepath) == tmpdir

        # Check it gets cleaned up
        client._clean_rendered_job_scripts(force=True)
        assert os.path.isfile(rendered_filepath) == False
