import docker

docker_client = docker.client.from_env()

class BrowserConstants:

    def __init__(self):
        self.CONTAINER_SUCCESS = 'Selenium Server is up and running on port'
        self.host = '127.0.0.1'
        self.browser_image_debug = docker_client.images.get('selenium/standalone-chrome-debug')
        self.browser_image = docker_client.images.get('selenium/standalone-chrome-debug')
        self.client_connect = 'wd/hub'
        self.node_connect = 'grid/register'
        self.base_port = 4444
