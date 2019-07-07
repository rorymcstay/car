class ResultCollectionFailure(Exception):
    def __init__(self, url, reason, exception):
        self.reason = reason
        self.url = url
        self.exception = exception