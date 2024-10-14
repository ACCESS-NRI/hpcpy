"""Top-level package for hpcpy."""

from . import _version
from hpcpy.client.client_factory import ClientFactory
from hpcpy.client.pbs import PBSClient
from hpcpy.client.slurm import SlurmClient
from typing import Union

__version__ = _version.get_versions()["version"]


def get_client(*args, **kwargs) -> Union[PBSClient, SlurmClient]:
    """Get a client object specific for the current scheduler.

    Returns
    -------
    Union[PBSClient, SLURMClient, MockClient]
        Client object for this scheduler.
    """
    return ClientFactory().get_client(*args, **kwargs)
