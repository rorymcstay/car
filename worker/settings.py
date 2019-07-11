import os

import requests

nanny_params = {
    "host": os.getenv("NANNY_HOST", "localhost"),
    "port": os.getenv("FLASK_PORT"),
    "api_prefix": "containercontroller",
    "params_manager": "parametercontroller"
}

browser_params = {
    "host": os.getenv("BROWSER_CONTAINER_HOST", "host.docker.internal"),
    "base_port": os.getenv("SELENIUM_PORT", 4444)
}


kafka_params = {
    "bootstrap_servers": [os.getenv("KAFKA_ADDRESS", "localhost:29092")],
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