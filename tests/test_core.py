import pytest
import importlib
import os


def _import_from(a, b):
    """Programmatic version of `import a from b`"""
    return getattr(importlib.import_module(a), b)


@pytest.fixture(autouse=True)
def environment():
    os.environ["HPCPY_DEV_MODE"] = "1"


def test_import_pbs_toplevel():
    """Test getting a PBSClient at the top level."""
    _import_from("hpcpy", "PBSClient")


def test_import_slurm_toplevel():
    """Test getting a SlurmClient at the top level."""
    _import_from("hpcpy", "SlurmClient")
