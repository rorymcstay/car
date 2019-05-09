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

stream_params = {
    "donedeal":{
        "class": "result-contain",
        "single": False,
        "page_ready": "img"
    }
}

class ParameterManager:
    """
    The ParameterManager controls the parameters. It delivers them to the client upon start up for use in
    settings.py

    """
    client = pymongo.MongoClient(**mongo_params)
    feed_params = client[os.getenv("PARAMETER_DATABASE", "params")]

    def getParameter(self, feed, name=None):
        if name is not None:
            feed = self.feed_params[feed].find_one(filter={"name": name})
        else:
            feed = self.feed_params[feed].find_one(filter={"name": "stream_params"})
        return feed["value"]

    def setParameter(self, feed, value, name=None):
        param = self.feed_params[feed].find_one({"name": name})
        if param is not None:
            param["value"] = value
            self.feed_params[feed].replace_one(filter={"name": name}, replacement={"name": name, "value": value})
        else:
            param = {"name": name, "value": value}
            self.feed_params[feed].insert_one(param)

    def loadParams(self):
        for feed in feeds:
            self.setParameter(feed, "feed", feeds[feed])
        self.setParameter(name="stream_params", value=stream_params, feed="stream_params")