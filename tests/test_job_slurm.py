"""Tests for the Job class."""

import pytest
import hpcpy.utilities as hu
import hpcpy.constants as hc
from hpcpy.constants.slurm import COMMANDS
from hpcpy.job import Job
from hpcpy import SlurmClient
import json


@pytest.fixture
def client():
    return SlurmClient()


@pytest.fixture
def status_json():
    return open(
        hu.get_installed_root() / "data" / "test" / "status-slurm.json", "rb"
    ).read()


@pytest.fixture
def job_id():
    return "132058409.gadi-pbs"


@pytest.fixture
def job_status():
    return "R"


def _change_status(status_json, new_status):
    """Helper function to adjust statuses at runtime without having multiple test references.

    Parameters
    ----------
    status_json : bytes
        Bytes from loading the status json.
    new_status : str
        A new status to inject.

    Returns
    -------
    bytes
        Modified status_json with new status.
    """

    # Decode the byte array
    status_json = json.loads(status_json.decode("utf-8"))

    # Override the status
    status_json["jobs"][0]["job_state"][0] = new_status

    # Re-encode and pass to the caller
    return json.dumps(status_json).encode()


def test_status(fp, client, status_json, job_id, job_status):
    """Test Job.status()."""

    status_json = _change_status(status_json, "RUNNING")

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=status_json,
        occurrences=2,
    )

    # Test that the status is collected on instantiation
    job = Job(job_id, client, auto_update=True)
    assert job._status == job_status

    # Test that the status is updated explicitly
    status = job.status()
    assert status == job_status


def test_hold(fp, client, status_json, job_id):
    """Test Job.hold()."""

    # Set it to queued
    status_json = _change_status(status_json, "RUNNING")

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=status_json,
    )

    # Test that the status is collected on instantiation
    job = Job(job_id, client)
    assert job._status == hc.STATUS_RUNNING

    # Set it to held
    status_json = _change_status(status_json, "PENDING")

    # Register the hold command
    fp.register(COMMANDS["hold"].format(job_id=job_id).split(), stdout=b"")

    fp.register(COMMANDS["status"].format(job_id=job_id).split(), stdout=status_json)

    # Test that the status is updated explicitly
    # Note SLURM considered queued and held to be the same
    job.hold()
    assert job._status == hc.STATUS_QUEUED


def test_release(fp, client, status_json, job_id):
    """Test Job.release()."""

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=_change_status(status_json, "PENDING"),
    )

    # Test that the status is collected on instantiation
    job = Job(job_id, client)

    # Make sure we start with something that is held
    assert job._status == hc.STATUS_QUEUED

    # Register the release command
    fp.register(COMMANDS["release"].format(job_id=job_id).split(), stdout=b"")

    # Register the status command with a queued state
    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=_change_status(status_json, "RUNNING"),
    )

    # Test that the status is updated explicitly
    job.release()
    assert job._status == hc.STATUS_RUNNING


def test_delete(fp, client, status_json, job_id):
    """Test Job.delete()."""

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=status_json,
    )

    # Test that the status is collected on instantiation
    job = Job(job_id, client)
    assert job._status == hc.STATUS_QUEUED

    # Register the delete command
    fp.register(COMMANDS["delete"].format(job_id=job_id).split(), stdout=b"")

    # Test that the status is updated explicitly
    job.delete()
