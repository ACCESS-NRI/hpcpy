"""SLURM Client Tests."""
import pytest
from hpcpy.client.slurm import SlurmClient
import hpcpy.utilities as hu
import hpcpy.constants as hc
import json


@pytest.fixture
def client():
    return SlurmClient()

@pytest.fixture
def status_json():
    return open(hu.get_installed_root() / "data" / "test" / "status-slurm.json", "rb").read()

@pytest.fixture
def job_id():
    return "1234"

def test_status(fp, client, status_json, job_id):
    """Test client.status()"""

    fp.register(
        f"squeue -j {job_id} --json".split(),
        stdout=status_json
    )
    
    status, _ = client.status(job_id)

    assert status == hc.STATUS_RUNNING