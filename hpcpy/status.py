"""Class to manage the status of a job."""


class Status:
    """Class to assist in mapping statuses from native to common.

    Parameters
    ----------
    short : str
        Short status code (i.e. SLURM)
    long : str
        Long status code.
    description : str
        Description of status.
    generic : str, optional
        Generic status, by default None
    """

    def __init__(self, short, long, description, generic=None):
        self.short = short
        self.long = long
        self.description = description
        self.status = generic
