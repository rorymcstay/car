import os

feeds = {
    "donedeal":{
        "json_identifier": "window.adDetails",
        "attrs":{
            "price": "etc",
        }
    }
}

summary_feeds = {
    "donedeal": {
        "url": {
            "class": ['card__link'],  # the unique path in terms of classes to the tag containg the info
            "single": True,  # singleton data item or not. eg list of images == False
            "attr": "href", # the name of the attribute if a tag variable (eg. link) if text item let be none
            "name": "a", # the name of the tage to find

        },
        "price": {
            "class": ["card__price"],
            "single": True,
            "attr": None,
            "name": "span"
        },
        "imgs": {
            "class": ["card__photo"],
            "single": True,
            "attr": "src",
            "name": "img"
        },
        "attrs": {
            "class": ["card__body-keyinfo"],
            "single": False,
            "attr": None,
            "name": "li"
        }

    },

}

kafka_params = {
    "bootstrap_servers": [os.getenv("KAFKA_ADDRESS")],
}

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST"), "port": os.getenv("HAZELCAST_PORT", 5701)
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