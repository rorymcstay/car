import hashlib
import logging as LOG

import pymongo
import os
import json
from bson import json_util, ObjectId

from src.main.market.utils.MongoServiceConstants import MongoServiceConstants


class MongoService:
    """
    This is the mongo database client. The collection and database it uses are stored in the properties.env file
    To start a docker container do:

        `docker exec -it nostalgic_murdock mongo mongo`

    in a terminal
    """

    def __init__(self):
        max_delay = MongoServiceConstants().TIMEOUT
        host = MongoServiceConstants().HOST
        username = MongoServiceConstants().USERNAME
        password = MongoServiceConstants().PASSWORD
        self.client = pymongo.MongoClient(host=host,
                                          username=username,
                                          password=password,
                                          serverSelectionTimeoutMS=max_delay)
        self.db = self.client[MongoServiceConstants().DATABASE_NAME]
        self.cars = self.db[MongoServiceConstants().COLLECTION_NAME]
        self.market_details_collection = self.db[MongoServiceConstants().MARKETS]

        # self.market_details_collection.create_index('adDetails.url', pymongo.ALL)

    def save_market_details(self, market_definition):
        operation = self.market_details_collection.insert(market_definition)
        x = self.cars.insert_many(market_definition)

    def insert(self, car, batch_number='Main'):
        """
        Insert a car into the database after generating an oid from the url. This ensures uniqueness of items in collection
        :param car:
        :return:
        """
        id = hashlib.sha224(car['adDetails']['url'].encode('utf-8')).hexdigest()
        id = id[:24]
        car['_id'] = ObjectId(id)
        car_search = self.cars.find({"_id": car['_id']})
        if car_search.count() == 0:
            x = self.cars.insert_one(car)
        else:
            car_before_list = []
            for i in car_search:
                car_before_list.append(i)
            car_before = car_before_list[0]
            try:
                car['adDetails']['previousPrices'] = car_before['adDetails']['previousPrices'].append(
                    car_before['adDetails']['price'])
            except KeyError:
                car['adDetails']['previousPrices'] = [car_before['adDetails']['price']]
            x = self.cars.replace_one({'_id': car['_id']}, car)
        LOG.info("Thread-%s: Request to write %s to database returned %s",
                 batch_number,
                 car['adDetails']['url'],
                 x.acknowledged)
        return

    def read(self, query):
        x = self.cars.find(query)
        data = []
        for i in x:
            data.append(i)
        return data

    def query(self, query, write=''):
        """
        This is the query to JSON method, it is used for querying the Mongo

        :param query: A dictionary object like {"hello": "world"}
        :param write: Should the query be written to an output file?
        :return: If no output file is given, then a JSON object is returned
        """
        page = self.cars.find(query)
        page_sanitized = json.loads(json_util.dumps(page))
        if len(write) != 0:
            with open(write, 'w') as outfile:
                json.dump(page_sanitized, outfile)
        else:
            return page_sanitized


service = MongoService()
