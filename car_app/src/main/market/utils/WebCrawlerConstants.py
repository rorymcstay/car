import os


class WebCrawlerConstants:
    def __init__(self):
        self.return_timeout = int(os.getenv('RETURN_TIMEOUT', 3))
        self.click_timeout = int(os.getenv('CLICK_TIMEOUT', 3))
        self.max_attempts = int(os.getenv('MAX_CLICK_ATTEMPTS', 5))
