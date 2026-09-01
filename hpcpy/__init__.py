"""Top-level package for hpcpy."""

from typing import Union

from hpcpy.client.client_factory import ClientFactory
from hpcpy.client.direct import DirectClient
from hpcpy.client.pbs import PBSClient
from hpcpy.client.slurm import SlurmClient

from . import _version

__version__ = _version.get_versions()["version"]


def get_client(*args, **kwargs) -> Union[PBSClient, SlurmClient, DirectClient]:
    """Get a client object specific for the current scheduler.

    Returns
    -------
    Union[PBSClient, SlurmClient, DirectClient]
        Client object for this scheduler.

    """
    return ClientFactory().get_client(*args, **kwargs)
