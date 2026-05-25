"""Tests for the Job class with DirectClient."""

import pytest
import hpcpy.utilities as hu
from hpcpy import DirectClient


@pytest.fixture
def client():
    return DirectClient()


@pytest.fixture
def status_running():
    return "R"


@pytest.fixture
def status_held():
    return "H"


@pytest.fixture
def status_finished():
    return "F"


@pytest.fixture
def job_script_path():
    return hu.get_installed_root() / "data" / "test" / "direct.sh"


def test_submit(client, job_script_path):
    """Test client.submit()"""

    # Submit the job script
    job = client.submit(job_script_path)

    # Check that it has a PID
    assert job.id is not None
    job.delete()


def test_status(client, job_script_path, status_running):
    """Test Job.status()."""

    # Submit the job script
    job = client.submit(job_script_path)

    # Check that it has a PID
    assert job.status() == status_running
    job.delete()


def test_hold_release(client, job_script_path, status_running, status_held):
    """Test Job.status()."""

    # Submit the job script
    job = client.submit(job_script_path)

    # Check that it is running
    assert job.status() == status_running

    # Hold it, check new status
    job.hold()
    assert job.status() == status_held

    # Release it
    job.release()
    assert job.status() == status_running

    job.delete()


def test_delete(client, job_script_path, status_finished):
    """Test client.submit()"""

    # Submit the job script
    job = client.submit(job_script_path)

    # Check that it has a PID (i.e. is running on the OS)
    assert job.id is not None

    # Delete it
    job.delete()

    # Check it has finished
    assert job.status() == status_finished


def test_submit_variables(client, job_script_path):
    """Test client.submit() with directives."""

    variables = dict(var1="SUCCESSFUL TEST", var2=1, var3=10.0)

    # Dry-submit the job, get the result
    result = client.submit("test.sh", variables=variables, dry_run=True)
    assert result == "var1='SUCCESSFUL TEST' var2=1 var3=10.0 bash test.sh"
