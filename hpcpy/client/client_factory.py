"""Client Factory."""

from hpcpy.client.direct import DirectClient
from hpcpy.client.pbs import PBSClient
from hpcpy.client.slurm import SlurmClient
from hpcpy.utilities import shell
from typing import Union


class ClientFactory:
    """An object that agnostically selects a scheduler."""

    def get_client(
        self, *args, **kwargs
    ) -> Union[PBSClient, SlurmClient, DirectClient]:

        """Get a client object based on what kind of scheduler we are using.

        Falls back to DirectClient when no scheduler can be detected.

        Arguments:
        ----------
        **kwargs
            Arguments for the specific client.

        Returns
        -------
        Union[PBSClient, SlurmClient, DirectClient]
            Client object suitable for the detected scheduler.
        """
        clients = dict(qsub=PBSClient, sbatch=SlurmClient)

        # Loop through the clients in order, looking for a valid scheduler
        for cmd, client in clients.items():
            if shell(f"which {cmd}", check=False).returncode == 0:
                return client(*args, **kwargs)

        # No scheduler found; fall back to direct execution
        return DirectClient(*args, **kwargs)
