import os

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST", "hazelcast"),
    "port": os.getenv("HAZELCAST_PORT", 5701)
}
browser_params = {
    "image": os.getenv('BROWSER_IMAGE', 'selenium/standalone-chrome:3.141.59')
}
mongo_params = {
    "host":os.getenv("MONGO_HOST"),
    "username":os.getenv("MONGO_USER"),
    "password":os.getenv("MONGO_PASS"),
    "serverSelectionTimeoutMS":5
}

class BrowserConstants:
    CONTAINER_TIMEOUT = int(os.getenv('CONTAINER_TIMEOUT', 10))
    CONTAINER_SUCCESS = 'Selenium Server is up and running on port'
    CONTAINER_QUIT = "Shutdown complete"
    client_connect = 'wd/hub'
    worker_timeout = int(os.getenv('WORKER_TIMEOUT', '3'))
