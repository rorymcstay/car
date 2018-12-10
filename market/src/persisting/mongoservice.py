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
        self.client = pymongo.MongoClient(os.getenv('MONGO_URL', '0.0.0.0:27017'), username=os.getenv('USERNAME', 'root'), password=os.getenv('PASSWORD', 'root'))
        self.db = self.client[os.getenv('MONGO_DATABASE', 'my_database')]
        self.collection = self.db[os.getenv("MONGO_COLLECTION", 'cars')]
        self.market_details_collection = self.db['marketDetails']

    def save_market_details(self, market_definition):
        x = self.market_details_collection.insert(market_definition)

    def return_all_markets(self):
        x = self.market_details_collection.find()
        page_sanitized = json.loads(json_util.dumps(x))
        data = []
        for i in x:
            data.append(i)
        return data


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

