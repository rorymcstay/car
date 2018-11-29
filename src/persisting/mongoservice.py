import pymongo
import os
import json
from bson import json_util


class MongoService:
    """
    This is the mongo database client. The collection and database it uses are stored in the properties.env file
    To start a docker container do:

        docker exec -it nostalgic_murdock mongo mongo

    in a terminal
    """
    def __init__(self):
        self.client = pymongo.MongoClient(os.environ['MONGO_URL'], username=os.environ['USERNAME'], password=os.environ['PASSWORD'])
        self.db = self.client[os.environ['MONGO_DATABASE']]
        self.collection = self.db[os.environ["MONGO_COLLECTION"]]


    def insert(self, car):
        """
        Insert a car into the database
        :param car:
        :return:
        """
        x = self.collection.insert(car)
        return

    def read(self, query):
        x = self.collection.find(query)
        data = []
        for i in x:
            data.append(i)
        return data

    def queryToJSON(self, query, write=''):
        """
        This is the query to JSON method, it is used for querying the Mongo

        :param query: A dictionary object like {"hello": "world"}
        :param write: Should the query be written to an output file?
        :return: If no output file is given, then a JSON object is returned
        """
        page = self.collection.find(query)
        page_sanitized = json.loads(json_util.dumps(page))
        if len(write) != 0:
            with open(write, 'w') as outfile:
                json.dump(page_sanitized, outfile)
        else:
            return page_sanitized

