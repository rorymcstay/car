import json
import os

from time import sleep

from kafka import KafkaConsumer, KafkaProducer

from settings import kafka_params
from src.main.manager import CacheManager, ObjectManager
from src.main.parser import ResultParser
from sqlalchemy import create_engine

class ResultLoader():

    cacheManager = CacheManager()
    objectManager = ObjectManager()
    kafkaConsumer = KafkaConsumer(**kafka_params)
    markets = ".*-results"

    producer = KafkaProducer(**kafka_params, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def consumeResults(self):
        self.kafkaConsumer.subscribe(pattern=self.markets)
        for message in self.kafkaConsumer:
            feed = message.topic.split("-")[0]
            value = ResultParser(feedName=feed, source=message.value).parseResult()
            item = {"url": value["url"], "type": feed}
            self.producer.send(topic="worker-queue", value=item)
            self.cacheManager.insertResult(name="{}-results".format(feed), result=value, key=message.key)

    def produceObjects(self):

        self.kafkaConsumer.subscribe(pattern=self.markets)
        for message in self.kafkaConsumer:
            feed = message.topic.split("-")[0]
            row = ResultParser(feedName=feed, source=message.value).parseRow()
            self.objectManager.prepareRow(name=feed, row=row)

