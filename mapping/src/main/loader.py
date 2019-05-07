from kafka import KafkaConsumer

from settings import kafka_params
from settings import result_mapping
from src.main.manager import CacheManager


class ResultLoader():

    markets = ["{market}-results".format(market=market) for market in result_mapping.keys()]
    cacheManager = CacheManager()
    kafkaConsumer = KafkaConsumer(**kafka_params)

    def consumeResults(self):
        self.kafkaConsumer.subscribe(self.markets)
        for message in self.kafkaConsumer:
            print(message)

if __name__ == '__main__':
    rl = ResultLoader()