"""Class to manage the status of a job."""


class Status:

    def __init__(self, short, long, description, generic=None):
        self.short = short
        self.long = long
        self.description = description
        self.status = generic
