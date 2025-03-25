import pytest
from hpcpy import PBSClient
import hpcpy.utilities as hu
import hpcpy.constants as hc
from hpcpy.job import Job
from datetime import datetime, timedelta
import json


@pytest.fixture
def client():
    return PBSClient()


@pytest.fixture
def status_json():
    return open(
        hu.get_installed_root() / "data" / "test" / "status-pbs.json", "rb"
    ).read()


@pytest.fixture
def job_id():
    return "132058409.gadi-pbs"


@pytest.fixture
def job():
    _job = Job("132058409.gadi-pbs", PBSClient(), auto_update=False)
    _job._auto_update = True
    return _job


def _change_status(status_json, job_id, new_status):
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
    status_json["Jobs"][job_id]["job_state"] = new_status

    # Re-encode and pass to the caller
    return json.dumps(status_json).encode()


def test_directives(client):
    """Test if the directives are properly interpolated"""
    expected = "qsub -q express -l walltime=10:00:00 test.sh"
    result = client.submit(
        "test.sh", directives=["-q express", "-l walltime=10:00:00"], dry_run=True
    )

    assert result == expected


def test_depends_on(client):
    """Test if the depends_on argument is correctly applied."""
    expected = "qsub -W depend=afterok:job1:job2 test.sh"
    result = client.submit("test.sh", depends_on=["job1", "job2"], dry_run=True)

    assert result == expected


def test_delay(client):
    """Test if delay is correctly applied"""
    run_at = datetime(2200, 7, 26, 12, 0, 0)
    run_at_str = run_at.strftime("%Y%m%d%H%M.%S")
    expected = f"qsub -a {run_at_str} test.sh"
    result = client.submit("test.sh", delay=run_at, dry_run=True)

    assert result == expected


def test_queue(client):
    """Test if the queue argument is added."""
    expected = "qsub -q express test.sh"
    result = client.submit("test.sh", dry_run=True, queue="express")

    assert result == expected


def test_walltime(client):
    """Test if the walltime argument is added."""
    expected = "qsub -l walltime=2:30:12 test.sh"
    result = client.submit(
        "test.sh", dry_run=True, walltime=timedelta(hours=2, minutes=30, seconds=12)
    )

    assert result == expected


def test_storage(client):
    """Test if the storage argument is added."""
    expected = "qsub -l storage=gdata/rp23+scratch/rp23 test.sh"
    result = client.submit(
        "test.sh", dry_run=True, storage=["gdata/rp23", "scratch/rp23"]
    )

    assert result == expected


def test_variables(client):
    """Test passing variables to the qsub command."""
    expected = "qsub -v var1=1234,var2=abcd test.sh"
    result = client.submit(
        "test.sh", dry_run=True, variables=dict(var1=1234, var2="abcd")
    )

    assert result == expected


def test_variables_empty(client):
    """Test passing empty variables dict to the qsub command works as expected."""
    expected = "qsub test.sh"
    result1 = client.submit("test.sh", dry_run=True, variables=dict())
    result2 = client.submit("test.sh", dry_run=True)

    assert result1 == expected
    assert result2 == expected


def test_submit(fp, client, status_json, job_id):
    """Test if the submit command is executed."""
    job_script = "test.sh"

    # Register the qsub command
    fp.register(f"qsub {job_script}".split(), stdout=job_id)

    # Register the qstat command
    fp.register(f"qstat -f -F json {job_id}".split(), stdout=status_json)

    # Submit the job, should return a job object
    job = client.submit(job_script)

    # Assert that the job object is correct
    assert isinstance(job, Job)

    # Assert that the job ID is correct
    assert job_id == job.id


def test_status(fp, client, status_json, job_id):
    """Test if the status command is executed as expected."""

    # Register the qstat command
    fp.register(f"qstat -f -F json {job_id}".split(), stdout=status_json)

    # Get the generic status of the job
    status = client.status(job_id)[0]
    assert status == hc.STATUS_QUEUED


def test_hold_release(fp, client, status_json, job_id):
    """Test client.hold()"""

    # Register the qstat command
    fp.register(f"qstat -f -F json {job_id}".split(), stdout=status_json)

    job = Job(job_id, client)
    assert job.status != hc.STATUS_HELD

    # Register the hold command
    fp.register(f"qhold {job_id}".split(), stdout=None)

    # Register the qstat command with an updated status
    fp.register(
        f"qstat -f -F json {job_id}".split(),
        stdout=_change_status(status_json, job_id, "H"),
    )

    job.hold()  # Will update the status in the background

    assert job._status == hc.STATUS_HELD

    # Register the qstat command with an updated status
    fp.register(
        f"qstat -f -F json {job_id}".split(),
        stdout=_change_status(status_json, job_id, "Q"),
    )

    # Register the hold command
    fp.register(f"qrls {job_id}".split(), stdout=None)

    # Release the job, also updates status in the background
    job.release()

    # Ensure it is queued
    assert job._status == hc.STATUS_QUEUED
