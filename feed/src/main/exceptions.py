class MaxAttemptsReached(Exception):
    pass


class NextPageException(Exception):
    def __init__(self, page, message):
        self.page = page
        self.message = message
