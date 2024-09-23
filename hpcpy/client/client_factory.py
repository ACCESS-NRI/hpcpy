"""Client Factory."""

from hpcpy.client.pbs import PBSClient
from hpcpy.client.slurm import SlurmClient
from hpcpy.client.mock import MockClient
import os
import hpcpy.exceptions as hx
from hpcpy.utilities import shell
from typing import Union


class ClientFactory:

    def get_client(*args, **kwargs) -> Union[PBSClient, SlurmClient, MockClient]:
        """Get a client object based on what kind of scheduler we are using.

        Arguments:
        ----------
        **kwargs
            Arguments for the specific client.

        Returns
        -------
        Union[PBSClient, SlurmClient, MockClient]
            Client object suitable for the detected scheduler.

        Raises
        ------
        hx.NoClientException
            When no scheduler can be detected.
        """

        clients = dict(ls=MockClient, qsub=PBSClient, sbatch=SlurmClient)

        # Remove the MockClient if dev mode is off
        if os.getenv("HPCPY_DEV_MODE", "0") != "1":
            _ = clients.pop("ls")

        # Loop through the clients in order, looking for a valid scheduler
        for cmd, client in clients.items():
            if shell(f"which {cmd}", check=False).returncode == 0:
                return client(*args, **kwargs)

        raise hx.NoClientException()
