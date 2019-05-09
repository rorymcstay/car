import os

import requests

nanny_params = {
    "host": os.getenv("NANNY_HOST", "localhost"),
    "port": os.getenv("FLASK_PORT"),
    "api_prefix": "containercontroller",
    "params_manager": "parametercontroller"
}

stream_params = requests.get("http://{host}:{port}/{params_manager}/getParameter/stream_params".format(**nanny_params)).json()

browser_params = {
    "host": os.getenv("BROWSER_CONTAINER_HOST", "host.docker.internal")
}


kafka_params = {
    "bootstrap_servers": [os.getenv("KAFKA_ADDRESS")],
}

pistonheads= {
    "url": {
        "class": ["mainimg"],
        "single": True,
        "attr": "href",
        "name": "a",

    },
    "price": {
        "class": ["card__price"],
        "single": True,
        "attr": None,
        "name": "span"
    },
    "attrs": {
        "class": ["card__body-keyinfo"],
        "single": False,
        "attr": None,
        "name": "li"
    },
    "imgs": {
        "class": ["mainimg"],
        "single": False,
        "attr": "src",
        "name": "img"
    }
}