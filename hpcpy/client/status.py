"""Object for holding status information."""
class Status:

    def __init__(self, code : str, native: object):
        """Constructor

        Parameters
        ----------
        code : str
            Scheduler-agnostic status code from hpcpy.constants.
        native : object
            Native status object or dict from the client scheduler.
        """
        self.code = code
        self.native = native