import json
import logging

import hazelcast
import requests

config = hazelcast.ClientConfig()
config.group_config.name = 'car-cluster'
config.group_config.password = 'password'

config.network_config.addresses.append('127.0.0.1')
config.network_config.addresses.append('192.168.1.99')
config.network_config.addresses.append('localhost:5702')

class CacheManager:

    client = hazelcast.client.HazelcastClient()

    def __init__(self):
        """
        Create a CacheManager for a data source with name
        Cache managers purpose is to collect ahead of time results users are looking for and persist to a
        cache. This is to:

            1. improve user better by making the next page faster
            2. store results for future requests of same result, identified by its URL/ObjectId

        data is stored as a python dict python dict in a map named after the data source.

        :param name: the name of the data source

        """
        self.name = name
        self.map = self.client.get_map(self.name)

    def insertPage(self):
        """
        request the next set of results

        :return:
        """
        r = requests.get('http://127.0.0.1/get_results/{name}'.format(name=self.name))
        nextResults = r.json()
        results = json.loads(nextResults)
        for data in results:
            self.map.put(key=data['_id'], value=data)
            logging.debug('inserted car {}'.format(data['_id']))


