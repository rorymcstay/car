import os
from os.path import join, dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

kafka_params = {
    "bootstrap_servers": '{}:9092'.format(os.getenv("KAFKA_HOST")),
}

hazelcast_params = {
    "host": "127.0.0.1", "port": 5701
}

routing_params = {
    "host": os.getenv("ROUTER_HOST", "localhost"),
    "port": os.getenv("ROUTER_PORT"),
    "api_prefix": "routingcontroller"
}

mongo_params = {
    "host": "localhost",
    "port": 27017,
}

browser_params = {
    "port": 4444,
    "host": os.getenv("BROWSER_HOST", "127.0.0.1"),
    "image": os.getenv('BROWSER_IMAGE', 'selenium/standalone-chrome:3.141.59')
}