"""SLURM Client Tests."""

import pytest
from hpcpy.client.slurm import SlurmClient
import hpcpy.utilities as hu
import hpcpy.constants as hc
from hpcpy.job import Job
import datetime


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
    return "1234"


def test_submit(fp, client, status_json, job_id):
    """Test if the submit command is executed."""
    job_script = "test.sh"

    # Register the sbatch command
    fp.register(f"sbatch {job_script}".split(), stdout=job_id)

    # Register the squeue command
    fp.register(f"squeue -j {job_id} --json".split(), stdout=status_json)

    # Submit the job, should return a job object
    job = client.submit(job_script)

    # Assert that the job object is correct
    assert isinstance(job, Job)

    # Assert that the job ID is correct
    assert job_id == job.id


def test_status(fp, client, status_json, job_id):
    """Test client.status()"""

    fp.register(f"squeue -j {job_id} --json".split(), stdout=status_json)

    status, _ = client.status(job_id)

    assert status == hc.STATUS_QUEUED


def test_directives(client):
    """Test that directives are correctly applied to the command string."""
    expected = "sbatch --job-name=myjob test.sh"
    result = client.submit("test.sh", directives=["--job-name=myjob"], dry_run=True)
    assert expected == result


def test_depends_on(client):
    """Test that job dependency is correctly applied to the command string."""
    expected = "sbatch --dependency=afterok:1234 test.sh"
    result = client.submit("test.sh", depends_on=["1234"], dry_run=True)
    assert expected == result


def test_delay(client):
    """Test that delay is correctly applied to the command string."""
    # Set execution to an hour's time
    when = datetime.datetime(2050, 1, 1, 13, 15)
    expected = "sbatch --begin=2050-01-01T13:15:00 test.sh"
    result = client.submit("test.sh", delay=when, dry_run=True)
    assert result == expected


def test_queue(client):
    """Test that a queue directive is correctly applied to the command string."""
    expected = "sbatch -p myqueue test.sh"
    result = client.submit("test.sh", queue="myqueue", dry_run=True)
    assert result == expected


def test_walltime(client):
    """Test that the walltime correctly applied to the command string."""
    expected = "sbatch --time 60 test.sh"
    result = client.submit(
        "test.sh", walltime=datetime.timedelta(minutes=60), dry_run=True
    )
    assert result == expected


def test_variables(client):
    """Test that variables are not added to the command string (as they go into the environment in SLURM)"""
    expected = "sbatch test.sh"
    result = client.submit("test.sh", variables=dict(test="test"), dry_run=True)
    assert result == expected


def test_variables_empty(client):
    """Test that empty variables are correctly omitted from the command string."""
    expected = "sbatch test.sh"
    result = client.submit("test.sh", variables=dict(), dry_run=True)
    assert result == expected
