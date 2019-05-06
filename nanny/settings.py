import os
from os.path import join, dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST"), "port": os.getenv("HAZELCAST_PORT", 5701)
}
browser_params = {
    "port": 4444,
    "host": os.getenv("BROWSER_HOST", "127.0.0.1"),
    "image": os.getenv('BROWSER_IMAGE', 'selenium/standalone-chrome:3.141.59')
}


class BrowserConstants:
    CONTAINER_TIMEOUT = int(os.getenv('CONTAINER_TIMEOUT', 10))
    CONTAINER_SUCCESS = 'Selenium Server is up and running on port'
    CONTAINER_QUIT = "Shutdown complete"
    client_connect = 'wd/hub'
    worker_timeout = int(os.getenv('WORKER_TIMEOUT', '3'))