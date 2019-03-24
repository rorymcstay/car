
class HealthStatus:
    def __init__(self, exception: Exception, browser: str, webcrawler: str):
        """
        The HealthStatus class

        :param exception:
        :param browser:
        :param webcrawler:
        """
        self.exception = exception
        self.exception_message = exception.args[0]
        self.browser = browser
        self.webcrawler = webcrawler
