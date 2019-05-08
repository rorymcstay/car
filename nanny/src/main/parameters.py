import os

import pymongo

from settings import mongo_params

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

class ParameterManager:
    """
    The ParameterManager controls the parameters. It delivers them to the client upon start up for use in
    settings.py

    """
    client = pymongo.MongoClient(**mongo_params)
    feed_params = client[os.getenv("PARAMETER_DATABASE", "params")]

    def getParameter(self, name, type):
        feed = self.feed_params[type].find_one(filter={"name": name})
        params = feed["value"]
        return params

    def setParameter(self, name, type, value):
        param = self.feed_params[type].find_one({"name": name})
        if param is not None:
            param["value"] = value
            self.feed_params[type].replace_one(filter={"name": name}, replacement={"name":name, "value": value})
        else:
            param = {"name": name, "value": value}
            self.feed_params[type].insert_one(param)

    def loadParams(self):
        for feed in feeds:
            self.setParameter(feed, "feed", feeds[feed])
