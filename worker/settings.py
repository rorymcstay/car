import os


stream_params = {
    "donedeal":{
        "class": "result-contain",
        "single": False,
        "page_ready": ""
    }
}

browser_params = {
    "host": os.getenv("BROWSER_CONTAINER_HOST", "host.docker.internal")
}

nanny_params = {
    "host": os.getenv("NANNY_HOST", "localhost"),
    "port": os.getenv("FLASK_PORT", 5000),
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