import os

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST", "localhost"),
    "port": os.getenv("HAZELCAST_PORT", 5701)
}
browser_params = {
    "image": os.getenv('BROWSER_IMAGE', 'selenium/standalone-chrome:3.141.59'),
    "base_port": int(os.getenv('BROWSER_BASE_PORT', 4444)),
    "max": int(os.getenv("MAX_CONTAINERS", 4))
}
mongo_params = {
    "host": os.getenv("MONGO_HOST", "localhost:27017"),
    "username": os.getenv("MONGO_USER", "root"),
    "password": os.getenv("MONGO_PASS", "root"),
    "serverSelectionTimeoutMS": 5
}

kafka_params = {
    "bootstrap_servers": [os.getenv("KAFKA_ADDRESS", "localhost:29092")],
}

class BrowserConstants:
    CONTAINER_TIMEOUT = int(os.getenv('CONTAINER_TIMEOUT', 10))
    CONTAINER_SUCCESS = 'Selenium Server is up and running on port'
    CONTAINER_QUIT = "Shutdown complete"
    client_connect = 'wd/hub'
    worker_timeout = int(os.getenv('WORKER_TIMEOUT', '3'))
