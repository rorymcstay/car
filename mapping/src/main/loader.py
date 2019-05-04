from kafka import KafkaConsumer
from settings import kafka_params
from src.main.manager import CacheManager
from kafka import KafkaConsumer

from settings import kafka_params
from src.main.manager import CacheManager

markets = ['donedeal_results']
cacheManager = CacheManager()
kafkaConsumer = KafkaConsumer(**kafka_params)

def getAllResults():
    kafkaConsumer.subscribe(markets)
    for message in kafkaConsumer:
        print(message)

if __name__ == '__main__':
    getAllResults()