import os

import docker

client=docker.client.from_env()


class TestConstants:
    def __init__(self, mongo_port):
        self.mongo_name = 'test_mongo_{}'.format(mongo_port)
        self.browser_host = os.getenv('LOCALHOST', 'localhost')
        self.mongo_image = client.images.get(os.getenv('MONGO_IMAGE', 'mongo'))
