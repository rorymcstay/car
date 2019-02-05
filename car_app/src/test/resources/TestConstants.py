import os


class TestConstants:
    def __init__(self):
        self.browser_port = os.getenv('TEST_BROWSER_PORT', '4444')
        self.browser_host = os.getenv('TEST_LOCALHOST', 'localhost')