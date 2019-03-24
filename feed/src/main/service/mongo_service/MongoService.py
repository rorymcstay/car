import json
import logging as log
from time import time

import pymongo
from bson import json_util

from src.main.car.Domain import Car, make_id
from src.main.market.utils.MongoServiceConstants import MongoServiceConstants
from src.main.utils.LogGenerator import LogGenerator, write_log

LOG = LogGenerator(log, name='mongo')


class MongoService:
    """
    This is the mongo database client. The collection and database it uses are stored in the properties.env file

    """

    def __init__(self, host):

        max_delay = MongoServiceConstants().TIMEOUT
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

    def save_market_details(self, name, market_definition):
        id = make_id(name)
        x = self.market_details_collection.find_one({'_id': id})
        if x is None:
            self.market_details_collection.insert_one(market_definition.__dict__)
        else:
            self.market_details_collection.replace_one({'_id': id}, market_definition.__dict__)

    def insert_or_update_car(self, car: Car, batch_number='Main'):
        """
        Insert a car into the database after generating an oid from the url. This ensures uniqueness of items in collection
        :param batch_number: who called
        :param car: car to insert
        :return:
        """
        start = time()
        car_search = self.cars.find_one(dict(_id=car.getId()))
        if car_search is None:
            x = self.cars.insert_one(car.__dict__())
        else:
            write_log(LOG.info, msg="rewriting car")
            x = car_search['adDetails']['previousPrices'].append(car.getAdDetails().previousPrices)
            self.cars.update_one(dict(_id=car.getId()), x)

        write_log(LOG.info, msg="inserted_car",
                  thread=batch_number,
                  url=car.getAdDetails().url,
                  time=time()-start,
                  result=x.acknowledged)
        return

    def insert_car(self, car: Car, batch_number='Main'):
        start = time()
        x = self.cars.insert_one(car.__dict__())
        write_log(LOG.info, msg="inserted_car",
                  thread=batch_number,
                  url=car.getAdDetails().url,
                  time=time()-start,
                  result=x.acknowledged)
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
