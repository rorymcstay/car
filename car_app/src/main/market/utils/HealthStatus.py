
class HealthStatus:
    def __init__(self, exception, browser, webcrawler):
        self.exception = exception
        self.exception_message = exception.args[0]
        self.browser = browser
        self.webcrawler = webcrawler
