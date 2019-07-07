import json
import logging
import os
from kafka import KafkaConsumer, KafkaProducer

from settings import kafka_params
from src.main.manager import CacheManager
from src.main.parser import ObjectParser


class ResultLoader:

    feeds = ["{feed}-items".format(feed=name) for name in os.getenv("FEEDS").split(";")]
    cacheManager = CacheManager()
    kafkaConsumer = KafkaConsumer(**kafka_params)
    producer = KafkaProducer(**kafka_params, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def consumeResults(self):
        self.kafkaConsumer.subscribe(self.feeds)
        for message in self.kafkaConsumer:
            feed = message.topic.split("-")[0]
            parser = ObjectParser(feedName=feed, source=message.value)
            raw = parser.getRawJson(message.key)
            value = parser.normalizeJson(raw)
            self.cacheManager.insertResult(mapName="{}-items".format(feed), result=value, key=str(message.key).split("/")[-1])
            logging.info("parsed car object from {} and inserted into cache with key {}".format(message.key, str(message.key).split("/")[-1]))
