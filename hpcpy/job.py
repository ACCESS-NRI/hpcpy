"""Job class."""


class Job:

    def __init__(self, id, client, auto_update=True) -> None:
        """Constructor.

        Parameters
        ----------
        id : str
            Job ID.
        client : object
            Client object.
        auto_update : bool, optional
            Automatically update this object after each action, by default True
        """
        self.id = id
        self._client = client
        self._auto_update = auto_update
        self._status = None
        self._native_full = None

        # Automatically get the status of the job on instantiation
        if self._auto_update:
            self._update()

    def _update(self) -> None:
        """Update the job status."""
        # Get the generic status and the full native status object from the client
        generic_status, native_full = self._client.status(self.id)

        # Set the native status attribute on the class with the full response
        self._native_full = native_full

        # Set the generic status attribue on the class
        self._status = generic_status

    def status(self) -> str:
        """Get the status of the job from the scheduler.

        Returns
        -------
        hpcpy.status.Status
            Status object
        """
        # Update the status
        self._update()

        # Return the generic status
        return self._status

    def hold(self) -> None:
        """Hold the job on the scheduler."""

        # Hold the job
        self._client.hold(self.id)

        # Update the status
        if self._auto_update:
            self._update()

    def release(self) -> None:
        """Release the job on the scheduler."""

        # Release the job
        self._client.release(self.id)

        # Update the status
        if self._auto_update:
            self._update()

    def delete(self) -> None:
        """Delete the job from the scheduler."""
        # Delete the job
        self._client.delete(self.id)
