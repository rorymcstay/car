"""
This module is a feed for car data from mongo db to tensorflow. It does three things:
    1. Access mongodb
    2. convert mongodb to tensors
    3. iterate over remote database to minimise in memory data.
"""
import json
import os
import traceback

import pandas as pd
import pymongo as mongo
import requests
import tensorflow as tf
from pandas import DataFrame
from requests import request

from src.main.encoding import Encoder


class CarManager:
    """
    Dataset importing functions. Training set function handles withr training data and the Test function feeds the test
    Each dataset importing function must return two objects:

        1.  a dictionary in which the keys are feature names and the values are Tensors (or SparseTensors) containing
            the corresponding feature data
        2.  a Tensor containing one or more labels
    """

    def __init__(self, name, query=None):
        self.carFeedApiPrefix = os.getenv('CAR_FEED_API_PREFIX')
        client = mongo.MongoClient(os.getenv("MONGO_HOST", "localhost:27017"),
                                   username=os.getenv("MONGO_USER", "root"),
                                   password=os.getenv("MONGO_PASS", "root"))

        db = client[os.getenv("DATABSE", "mydatabase")]
        self.cars = db[os.getenv("COLLECTION", "cars")]
        self.batch_size = 1000
        if query is None:
            self.all_cars = lambda x:  self.cars.find().skip(x).limit(self.batch_size)
        else:
            self.all_cars = lambda x:  self.cars.find(query).skip(x).limit(self.batch_size)
        self.exchange = self.getGbpExchange()
        self.range = range(round(self.cars.count_documents()/self.batch_size, ndigits = 0))
        self.page = 1

    def returnCarObservations(self, x) -> DataFrame:
        array = []
        for car in self.all_cars(x):
            key = car['_id']
            try:
                del car['adDetaisl']['carType']
                location = car['adDetaisl']['location']
                del car['adDetaisl']['location']
                obs = {'index': key, **car['carDetails'], **car["adDetaisl"], **location}
            except KeyError:
                del car['adDetails']['carType']
                location = car['adDetails']['location']
                del car['adDetails']['location']
                obs = {'index': key, **car['carDetails'], **car["adDetails"], **location}
            except Exception:
                continue
            obs = self.declareMissing(obs)
            obs = self.normalizeMileage(obs)
            obs = self.convertInteger(obs, 'owners', 'engineCapacity' )
            obs = self.normalizePrice(obs)
            array.append(obs)

        data = pd.read_json(json.dumps(array, cls=Encoder))
        return data

    def returnLatestCarObservations(self) -> pd.DataFrame:
        """
        Consume car_feed rest api to return dataframe of cars
        :return:
        """
        array = []
        r = requests.get("{}{}".format(self.carFeedApiPrefix, 'get_results'))
        cars = r.json()
        for car in cars:
            key = car['_id']
            try:
                del car['adDetails']['carType']
                location = car['adDetails']['location']
                del car['adDetails']['location']
                obs = {'index': key, **car['carDetails'], **car["adDetails"], **location}
            except Exception:
                continue
            obs = self.declareMissing(obs)
            obs = self.normalizeMileage(obs)
            obs = self.convertInteger(obs, 'owners', 'engineCapacity')
            obs = self.normalizePrice(obs)
            array.append(obs)
        df = pd.read_json(array)
        return df

    def normalizePrice(self, car):
        try:
            price = float(''.join(filter(lambda x: x.isdigit() or x.isdecimal(), car['price'])))
            if car['currency'] == "GBP":
                car['price'] = price*self.exchange
        except:
            traceback.print_exc()
            car['price'] = None
        return car

    @staticmethod
    def normalizeMileage(car):
        val = car['mileage']
        try:
            if all(symb not in val for symb in ['km', 'kms']):
                car['mileage'] = 1.60934*float(''.join(filter(lambda x: x.isdigit() or x.isdecimal(), val)))
            else:
                car['mileage'] = float(''.join(filter(lambda x: x.isdigit() or x.isdecimal(), val)))
        except:
            traceback.print_exc()
            car['mileage'] = None
        return car

    @staticmethod
    def convertInteger(car, *args):
        for key in args:
            raw = car[key]
            try:
                car[key] = float(''.join(filter(lambda x: x.isdigit() or x.isdecimal(), raw)))
            except:
                traceback.print_exc()
                car[key] = None
        return car

    @staticmethod
    def getGbpExchange():
        try:
            fx = request('GET', 'https://api.exchangeratesapi.io/latest')
            return 1/json.loads(fx.text)['rates']['GBP']
        except:
            return 1/0.85
    @staticmethod
    def declareMissing(car):
        for key in car:
            if key == 'engineType' and car['engineType'] == car['make']:
                car[key] = None
            elif isinstance(car[key], str):
                if car[key] == '':
                    car[key] = None
        return car

    @staticmethod
    def declareCategorical(df, *args):
        for key in args:
            df[key] = df[key].astype('category')

    def encodeFactors(self, df: DataFrame) -> DataFrame:
        """
        :param df: The raw dataframe
        :return: a dataframe with encoded factor matrices
        """
        df.set_index('index')
        self.declareCategorical(df, 'bodyStyle', 'color', 'country', 'county', 'currency', 'engineType', 'fuelType', 'make', 'model', 'special')
        encoded_factors = pd.get_dummies(df.select_dtypes(include='category'))
        integers = df.select_dtypes(include='number')
        out = pd.concat([integers, encoded_factors], sort=True)
        return out

    def addTensor(self, key, value):
        data = dict()
        df = self.getDataframe()
        return {key: tf.convert_to_tensor(value, tf.float32)}

    def getDataframe(self, page) -> pd.DataFrame:
        data = self.returnCarObservations(page*self.batch_size - 1)
        data = self.encodeFactors(data)
        return data
