import os

import docker

docker_client = docker.client.from_env()

class BrowserConstants:

    def __init__(self):
        self.CONTAINER_TIMEOUT = int(os.getenv('CONTAINER_TIMEOUT', 10))
        self.CONTAINER_SUCCESS = 'Selenium Server is up and running on port'
        self.host = os.getenv('DRIVER_HOST', 'localhost')
        self.base_port = int(os.getenv('DRIVER_PORT', '4444'))

        self.browser_image = docker_client.images.get(os.getenv('BROWSER_IMAGE', 'selenium/standalone-chrome'))
        self.client_connect = 'wd/hub'
        self.worker_timeout = int(os.getenv('WORKER_TIMEOUT', '3'))
