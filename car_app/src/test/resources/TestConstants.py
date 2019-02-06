import os
import docker

client=docker.client.from_env()

class TestConstants:
    def __init__(self):
        self.mongo_port = 27000
        self.browser_port = os.getenv('TEST_BROWSER_PORT', '4444')
        self.browser_host = os.getenv('TEST_LOCALHOST', 'localhost')
        self.mongo_image= client.images.get(os.getenv('MONGO_IMAGE', 'mongo'))
