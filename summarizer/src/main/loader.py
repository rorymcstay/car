import json
import os

from time import sleep

from kafka import KafkaConsumer, KafkaProducer

from settings import kafka_params
from src.main.manager import CacheManager
from src.main.parser import ResultParser


class ResultLoader():

    markets = ["{feed}-results".format(feed=name) for name in os.getenv("FEEDS", "donedeal;pistonheads").split(";")]
    cacheManager = CacheManager()
    kafkaConsumer = KafkaConsumer(**kafka_params)
    producer = KafkaProducer(**kafka_params, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def consumeResults(self):
        self.kafkaConsumer.subscribe(self.markets)
        for message in self.kafkaConsumer:
            feed = message.topic.split("-")[0]
            value = ResultParser(feedName=feed, source=message.value).parseResult()
            item = {"url": value["url"], "type": feed}
            self.producer.send(topic="worker-queue", value=item)
            self.cacheManager.insertResult(name="{}-results".format(feed), result=value, key=message.key)
            sleep(10)
