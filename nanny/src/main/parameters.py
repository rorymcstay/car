import os
from datetime import datetime

import bson.json_util as json
import checksumdir
import pymongo
from pymongo.database import Database

from settings import mongo_params


class ParameterManager:
    """
    The ParameterManager controls the parameters. It delivers them to the client.

    """
    client = pymongo.MongoClient(**mongo_params)
    feed_params: Database = client[os.getenv("PARAMETER_DATABASE", "params")]

    def getParameter(self, collection, name=None):
        param = self.feed_params[collection].find_one(filter={"name": name})
        return param

    def setParameter(self, collection, value, name=None):
        param = self.feed_params[collection].find_one({"name": name})
        value.update({"name": name})
        old = param
        if param is not None:
            self.feed_params[collection].replace_one(filter={"name": name}, replacement=value)
            old["name"] = "{}_{}".format(name, datetime.now().strftime("%d%m%Y"))
            self.feed_params[collection].insert(old)
        else:
            self.feed_params[collection].insert_one(value)


    def loadParams(self):
        files = os.listdir("./params")
        for file in files:
            with open(file) as f:
                params = json.loads(f.read())
            for param in params:
                self.setParameter(name=param.get("name"), collection=file.split(".")[0], value=param)

    def exportParameters(self, notes):
        collections = self.feed_params.list_collection_names()
        if os.path.exists("./config/params"):
            old = "config/params_{}".format(datetime.now().strftime("%d%m%y-%H%M"))
            os.rename("./config/params", old)
            verOld = checksumdir.dirhash(old)
        os.makedirs("./config/params/", exist_ok=True)
        for collection in collections:
            cursor = self.feed_params[collection].find({})
            with open("./config/params/{}.json".format(collection), "w") as file:
                file.write('[')
                for document in cursor:
                    file.write(json.dumps(document))
                    file.write(',')
                file.write(']')
        verNew = checksumdir.dirhash("./config/params")
        if verOld and old is not None:
            if verNew == verOld:
                os.rmdir(old)
        with open("./config/params/notes.txt", "w") as file:
            file.write(notes)
        return os.listdir("./config/params")
