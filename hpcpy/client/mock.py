"""Mock client for testing."""

from hpcpy.client.base import BaseClient
import hpcpy.constants as hc


class MockClient(BaseClient):
    """Mock client object for testing."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            tmp_submit=hc.MOCK_SUBMIT,
            tmp_status=hc.MOCK_STATUS,
            tmp_delete=hc.MOCK_DELETE,
        )

    def status(self, job_id) -> str:
        """Get the status of the job.

        Parameters
        ----------
        job_id : str
            Job ID

        Returns
        -------
        str
            Status.
        """
        status_code = super().status(job_id=job_id)
        return hc.MOCK_STATUSES[status_code]
