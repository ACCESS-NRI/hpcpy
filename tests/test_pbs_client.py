import pytest
from hpcpy.client import PBSClient
from datetime import datetime, timedelta


@pytest.fixture
def client():
    return PBSClient()


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
