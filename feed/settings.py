from os.path import join, dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

markets = {
    "donedeal": {
        "result": "card-item",
        "resultImg": "src",
        "resultUrl": "card-item",
        "resultPrice": "card__price",
        "json_identifier": "window.adDetails",
        "result_css": ".card__body",
        "wait_for_car": ".cad-header",
        'next_page_xpath': "//*[@id]",
        "next_button_text": "next",
        "result_stub": "https://www.donedeal.co.uk/cars-for-sale/",
        "sortString": "publishdate%20desc",
        "result_exclude": ["Compare", 'compare', 'insurance', "Insurance"],
        "home": "https://donedeal.co.uk/cars",

        "browser_port": 4444,
        "browser_host": "localhost",
        "mongo_host": "localhost",
        "mongo_port": 27017,
    }
}

results = {
    "donedeal": {
        "url": {
            "nodes": ["card-item"],
            "single": True,
            "attr": "href",
            "nodeType": "a"
        },
        "price": {
            "nodes": ["card-item"],
            "single": True,
            "last_nodeType": "name"
        },
        "attrs": {
            "nodes": ["card-item", "src"]
        }
    }
}