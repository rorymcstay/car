
class HealthStatus(dict):
    def __init__(self, exception: Exception, browser: str, webCrawler: str, **kwargs):
        """
        The HealthStatus class

        :param exception:
        :param browser:
        :param webcrawler:
        """
        super().__init__(**kwargs)
        self.exception = exception
        self.exception_message = exception.args[0]
        self.browser = browser
        self.webCrawler = webCrawler

    def __repr__(self):
        return dict(exception_message=self.exception_message, browser=self.browser, webCrawler=self.webCrawler)
