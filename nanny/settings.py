import os

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST", "hazelcast"),
    "port": os.getenv("HAZELCAST_PORT", 5701)
}
browser_params = {
    "image": os.getenv('BROWSER_IMAGE', 'selenium/standalone-chrome:3.141.59'),
    "base_port": int(os.getenv('BROWSER_BASE_PORT', 4444)),
    "max": int(os.getenv("MAX_CONTAINERS", 4))
}
mongo_params = {
    "host":os.getenv("MONGO_HOST"),
    "username":os.getenv("MONGO_USER"),
    "password":os.getenv("MONGO_PASS"),
    "serverSelectionTimeoutMS":5
}

class BrowserConstants:
    CONTAINER_TIMEOUT = int(os.getenv('CONTAINER_TIMEOUT', 10))
    CONTAINER_SUCCESS = 'Selenium Server is up and running on port'
    CONTAINER_QUIT = "Shutdown complete"
    client_connect = 'wd/hub'
    worker_timeout = int(os.getenv('WORKER_TIMEOUT', '3'))


feeds = {
    "donedeal": {
        "name": "donedeal",
        'next_page_xpath': "//*[@id]",
        "next_button_text": "next",
        "result_stub": "https://www.donedeal.co.uk/cars-for-sale/",
        "wait_for": ".cad-header",
        "base_url": "https://donedeal.co.uk/cars",
        "result_stream": {
            "class": "card-item",
            "single": False
        },
    }
}

stream_params = {
    "donedeal":{
        "class": None,
        "single": True,
        "page_ready": "img"
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
    "pistonheads": {
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
}

objects = {
    "donedeal":{
        "json_identifier": "window.adDetails",
        "attrs": {
            "price": "price",
            "county": "county",
            "currency": "currency",
            "photos": "medium",
            "ad_age": "age",
            "keyInfo": "keyInfo",
            "title": "header",
            "description": "description"
        }
    }
}

home_config = {
    "donedeal": {
        "skeleton": ["https://www.donedeal.co.uk/cars/", "{make}", "/", "{model}", "?sort=", "{sort}"],
        "sort_first": {
            "newest": "publishdate%20desc",
            "oldest": "publishdate%20asc",
            "high": "price%20desc",
            "low": "price%20asc"
        }
    }
}