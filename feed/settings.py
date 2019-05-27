import os

import requests

kafka_params = {
    "bootstrap_servers": [os.getenv("KAFKA_ADDRESS")],
}

hazelcast_params = {
    "host": "127.0.0.1", "port": 5701
}

browser_params = {
    "port": os.getenv("BROWSER_PORT", 4444),
    "host": os.getenv("BROWSER_CONTAINER_HOST", "localhost"),
    "image": os.getenv('BROWSER_IMAGE', 'selenium/standalone-chrome:3.141.59')

}

routing_params = {
    "host": os.getenv("ROUTER_HOST", "localhost"),
    "port": os.getenv("FLASK_PORT", 5002),
    "api_prefix": "routingcontroller"
}

nanny_params = {
    "host": os.getenv("NANNY_HOST", "localhost"),
    "port": os.getenv("FLASK_PORT", 5003),
    "api_prefix": "containercontroller",
    "params_manager": "parametercontroller"
}


params = requests.get("http://{host}:{port}/{params_manager}/getParameter/{name}/results".format(**nanny_params, name=os.getenv("NAME")))

feed_params = params.json()
