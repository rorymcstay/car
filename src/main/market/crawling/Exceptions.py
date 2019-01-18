class ExcludedResultNotifier(Exception):
    pass


class PageOutOfRange(Exception):
    pass


class EndOfQueueNotification(Exception):
    def __init__(self, member, exception, attempt):
        self.attempt = attempt
        self.exception = exception
        self.member = member


class PageLoadedError(Exception):
    pass


class QueueServicingError(Exception):
    def __init__(self, url, attempt, reason, exception):
        self.attempt = attempt
        self.reason = reason
        self.url = url
        self.exception = exception


class ResultCollectionFailure(Exception):
    def __init__(self, url, reason, exception):
        self.reason = reason
        self.url = url
        self.exception = exception

