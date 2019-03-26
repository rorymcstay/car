
class HealthStatus(object):
    def __init__(self, exception: Exception, browser: str, webCrawler: str):
        """
        The HealthStatus class

        :param exception:
        :param browser:
        :param webcrawler:
        """
        self.exception = exception
        self.exception_message = exception.args[0]
        self.browser = browser
        self.webCrawler = webCrawler

    def __dict__(self):
        return dict(exception_message=self.exception_message, browser=self.browser, webCrawler=self.webCrawler)