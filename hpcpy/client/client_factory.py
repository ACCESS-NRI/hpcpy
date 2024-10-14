"""Client Factory."""

from hpcpy.client.pbs import PBSClient
from hpcpy.client.slurm import SlurmClient
import hpcpy.exceptions as hx
from hpcpy.utilities import shell
from typing import Union


class ClientFactory:

    def get_client(*args, **kwargs) -> Union[PBSClient, SlurmClient]:
        """Get a client object based on what kind of scheduler we are using.

        Arguments:
        ----------
        **kwargs
            Arguments for the specific client.

        Returns
        -------
        Union[PBSClient, SlurmClient]
            Client object suitable for the detected scheduler.

        Raises
        ------
        hx.NoClientException
            When no scheduler can be detected.
        """

        clients = dict(qsub=PBSClient, sbatch=SlurmClient)

        # Loop through the clients in order, looking for a valid scheduler
        for cmd, client in clients.items():
            if shell(f"which {cmd}", check=False).returncode == 0:
                return client(*args, **kwargs)

        raise hx.NoClientException()
