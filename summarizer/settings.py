import os

import requests

nanny_params = {
    "host": os.getenv("NANNY_HOST", "localhost"),
    "port": os.getenv("FLASK_PORT"),
    "api_prefix": "containercontroller",
    "params_manager": "parametercontroller"
}

summary_feeds = requests.get("http://{host}:{port}/parametercontroller/getParameter/summary_feeds".format(**nanny_params)).json()

kafka_params = {
    "bootstrap_servers": [os.getenv("KAFKA_ADDRESS")],
}

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST"), "port": os.getenv("HAZELCAST_PORT", 5701)
}
