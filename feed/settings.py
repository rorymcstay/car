import os
from os.path import join, dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

market = {
    "name": os.getenv("NAME"),
    'next_page_xpath': "//*[@id]",
    "next_button_text": "next",
    "result_stub": "https://www.donedeal.co.uk/cars-for-sale/",
    "result_exclude": ['compare', 'insurance'],
    "wait_for_car": ".cad-header",

    "home": "https://donedeal.co.uk/cars",

    "result_stream": {
        "class": "card-item",
        "single": False
    },
    "worker_stream": None
}

markets = {
    "piston_heads": {
        'next_page_xpath': "//*[@id=\"next\"]",
        "next_button_text": "next",
        "result_exclude": ["we will buy", 'compare', 'insurance'], # ignore commonly named adverts
        "result_stub": "https://www.pistonheads.com/classifieds/used-cars/",
        "wait_for_car": ".theImage",

        "home": "https://www.pistonheads.com/classifieds?Category=",

        "market_stream": {
            "class": "result-contain",
            "single": False
        },
        "worker_stream": None
    }
}

kafka_params = {
    "bootstrap_servers": ['{}'.format(os.getenv("KAFKA_ADDRESS"))],
}

hazelcast_params = {
    "host": "127.0.0.1", "port": 5701
}

routing_params = {
    "host": os.getenv("ROUTER_HOST", "localhost"),
    "port": os.getenv("ROUTER_PORT"),
}

mongo_params = {
    "host": "localhost",
    "port": 27017,
}

browser_params = {
    "port": 4444,
    "host": os.getenv("BROWSER_HOST", "127.0.0.1"),
    "image": os.getenv('BROWSER_IMAGE', 'selenium/standalone-chrome:3.141.59')
}