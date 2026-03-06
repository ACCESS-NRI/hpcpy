"""Tests for the Job class with DirectClient."""

import pytest
import hpcpy.constants as hc
from hpcpy.constants.direct import COMMANDS
from hpcpy.job import Job
from hpcpy import DirectClient


@pytest.fixture
def client():
    return DirectClient()


@pytest.fixture
def status_running():
    return b"R"


@pytest.fixture
def status_sleeping():
    return b"S"


@pytest.fixture
def status_stopped():
    return b"T"


@pytest.fixture
def job_id():
    return "1234"


@pytest.fixture
def job_status():
    return hc.STATUS_RUNNING


def test_status(fp, client, status_running, job_id, job_status):
    """Test Job.status()."""

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=status_running,
        occurrences=2,
    )

    # Test that the status is collected on instantiation
    job = Job(job_id, client, auto_update=True)
    assert job._status == job_status

    # Test that the status is updated explicitly
    status = job.status()
    assert status == job_status


def test_hold(fp, client, status_running, status_stopped, job_id):
    """Test Job.hold()."""

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=status_running,
    )

    # Test that the status is collected on instantiation
    job = Job(job_id, client)
    assert job._status == hc.STATUS_RUNNING

    # Register the hold command
    fp.register(COMMANDS["hold"].format(job_id=job_id).split(), stdout=b"")

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(), stdout=status_stopped
    )

    # Test that the status is updated after holding
    job.hold()
    assert job._status == hc.STATUS_SUSPENDED


def test_release(fp, client, status_running, status_stopped, job_id):
    """Test Job.release()."""

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=status_stopped,
    )

    # Test that the status is collected on instantiation
    job = Job(job_id, client)

    # Make sure we start with something that is stopped
    assert job._status == hc.STATUS_SUSPENDED

    # Register the release command
    fp.register(COMMANDS["release"].format(job_id=job_id).split(), stdout=b"")

    # Register the status command with a running state
    fp.register(COMMANDS["status"].format(job_id=job_id).split(), stdout=status_running)

    # Test that the status is updated after releasing
    job.release()
    assert job._status == hc.STATUS_RUNNING


def test_delete(fp, client, status_running, job_id):
    """Test Job.delete()."""

    fp.register(
        COMMANDS["status"].format(job_id=job_id).split(),
        stdout=status_running,
    )

    # Test that the status is collected on instantiation
    job = Job(job_id, client)
    assert job._status == hc.STATUS_RUNNING

    # Register the delete command
    fp.register(COMMANDS["delete"].format(job_id=job_id).split(), stdout=b"")

    # Test that the job can be deleted
    job.delete()
