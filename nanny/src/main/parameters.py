import os
from datetime import datetime

import bson.json_util as json
import pymongo
from pymongo.database import Database

from settings import mongo_params, feeds, stream_params, summary_feeds, objects, home_config


class ParameterManager:
    """
    The ParameterManager controls the parameters. It delivers them to the client upon start up for use in
    settings.py

    """
    client = pymongo.MongoClient(**mongo_params)
    feed_params: Database = client[os.getenv("PARAMETER_DATABASE", "params")]

    def getParameter(self, feed_type, name=None):
        if name is not None:
            feed_type = self.feed_params[feed_type].find_one(filter={"name": name})
        else:
            feed_type = self.feed_params[feed_type].find_one(filter={"name": "stream_params"})
        return feed_type["value"]

    def setParameter(self, feed_type, value, name=None):
        if name is not None:
            param = self.feed_params[feed_type].find_one({"name": value["name"]})
            if param is not None:
                param["value"] = value
                self.feed_params[feed_type].replace_one(filter={"name": name}, replacement={"name": name, "value": value})
            else:
                param = {"name": name, "value": value}
                self.feed_params[feed_type].insert_one(param)
        else:
            self.feed_params[feed_type].insert_one({"name": "stream_params", "value": value})


    def loadParams(self):
        for feed_name in feeds:
            self.setParameter(feed_type="results", value=feeds[feed_name], name=feed_name)
        self.setParameter(value=stream_params, feed_type="stream_params")
        self.setParameter(value=summary_feeds, feed_type="summary_feeds")
        self.setParameter(value=objects, feed_type="mapper")
        self.setParameter(value=home_config, feed_type="home_config")

    def exportParameters(self, notes):

        collections = self.feed_params.list_collection_names()
        if os.path.exists("./config/params"):
            os.rename("./config/params", "config/params_{}".format(datetime.now().strftime("%d%m%y-%H%M")))
        os.makedirs("./config/params/", exist_ok=True)
        for collection in collections:
            cursor = self.feed_params[collection].find({})
            with open("./config/params/{}.json".format(collection), "w") as file:
                file.write('[')
                for document in cursor:
                    file.write(json.dumps(document))
                    file.write(',')
                file.write(']')

        with open("./config/params/notes.txt", "w") as file:
            file.write(notes)
        return os.listdir("./config/params")




