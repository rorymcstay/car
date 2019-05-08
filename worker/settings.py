import os
from os.path import join, dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

stream_params = {
    "donedeal":{
        "class": "result-contain",
        "single": False,
        "page_ready": ""
    }
}

browser_params = {
    "host": os.getenv("BROWSER_CONTAINER_HOST", "localhost")
}

nanny_params = {
    "host": os.getenv("NANNY_HOST", "localhost"),
    "port": os.getenv("NANNY_PORT"),
    "api_prefix": "containercontroller"
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