import os
from os.path import join, dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

feeds = {
    "feed_name":{
        "json_identifier": "window.adDetails",
        "attrs":{
            "price": "etc",
        }
    },
    "donedeal": {
        "result": "card-item",
        "json_identifier": "window.adDetails",
        "result_css": ".card__body",
        "wait_for_car": ".cad-header",
        'next_page_xpath': "//*[@id]",
        "next_button_text": "next",
        "result_stub": "https://www.donedeal.co.uk/cars-for-sale/",
        "sortString": "publishdate%20desc",
        "result_exclude": ['compare', 'insurance'],
        "home": "https://donedeal.co.uk/cars",
    },
    "piston_heads": {
        "result": "result-contain",
        "json_identifier": "pageDnaObj",
        "result_css": ".result-contain",
        "wait_for_car": ".theImage",
        'next_page_xpath': "//*[@id=\"next\"]",
        "next_button_text": "next",
        "result_stub": "https://www.pistonheads.com/classifieds/used-cars/",
        "sortString": "NewestWithImageFirst", # the sort by newest url string for router
        "result_exclude": ["we will buy", 'compare', 'insurance'], # ignore commonly named adverts
        "home": "https://www.pistonheads.com/classifieds?Category=",
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