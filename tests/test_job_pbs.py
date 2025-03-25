"""Tests for the Job class."""

import pytest
import hpcpy.utilities as hu
import hpcpy.constants as hc
from hpcpy.constants.pbs import COMMANDS
from hpcpy.job import Job
from hpcpy import PBSClient


@pytest.fixture
def client():
    return PBSClient()


@pytest.fixture
def status_json():
    return open(
        hu.get_installed_root() / "data" / "test" / "status-pbs.json", "rb"
    ).read()


@pytest.fixture
def status_json_held():
    return open(
        hu.get_installed_root() / "data" / "test" / "status-pbs-held.json", "rb"
    ).read()


@pytest.fixture
def job_id():
    return "132058409.gadi-pbs"


@pytest.fixture
def job_status():
    return "Q"


def test_status(fp, client, status_json, job_id, job_status):
    """Test Job.status()."""

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


def test_hold(fp, client, status_json, status_json_held, job_id):
    """Test Job.hold()."""

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=status_json,
    )

    # Test that the status is collected on instantiation
    job = Job(job_id, client)
    assert job._status == hc.STATUS_QUEUED

    # Register the hold command
    fp.register(COMMANDS["hold"].format(job_id=job_id).split(), stdout=b"")

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(), stdout=status_json_held
    )

    # Test that the status is updated explicitly
    job.hold()
    assert job._status == hc.STATUS_HELD


def test_release(fp, client, status_json, status_json_held, job_id):
    """Test Job.release()."""

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=status_json_held,
    )

    # Test that the status is collected on instantiation
    job = Job(job_id, client)

    # Make sure we start with something that is held
    assert job._status == hc.STATUS_HELD

    # Register the release command
    fp.register(COMMANDS["release"].format(job_id=job_id).split(), stdout=b"")

    # Register the status command with a queued state
    fp.register(COMMANDS["status"].format(job_id=job_id).split(), stdout=status_json)

    # Test that the status is updated explicitly
    job.release()
    assert job._status == hc.STATUS_QUEUED


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
