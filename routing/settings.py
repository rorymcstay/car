import os

import requests

nanny_params = {
    "host": os.getenv("NANNY_HOST", "localhost"),
    "port": os.getenv("FLASK_PORT", 5003),
    "api_prefix": "containercontroller",
    "params_manager": "parametercontroller"
}

home_config = requests.get("http://{host}:{port}/{params_manager}/getParameter/home_config".format(**nanny_params)).json()

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST", "localhost"), "port": os.getenv("HAZELCAST_PORT", 5701)
}
