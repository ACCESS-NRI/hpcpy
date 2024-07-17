class NoClientException(Exception):
    def __init__(self):
        super().__init__(
            "Unable to detect scheduler type, cannot determine client type."
        )
