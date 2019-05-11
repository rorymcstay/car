import json
import logging

import hazelcast
from hazelcast import ClientConfig, HazelcastClient
from hazelcast.core import HazelcastJsonValue

from settings import hazelcast_params

config = hazelcast.ClientConfig()

config.network_config.addresses.append('127.0.0.1')
config.network_config.addresses.append('192.168.1.99')
config.network_config.addresses.append('localhost:5702')


class CacheManager:
    config = ClientConfig()
    config.network_config.addresses.append("{host}:{port}".format(**hazelcast_params))
    client = HazelcastClient(config)

    def insertResult(self, name, result, key):
        """
        request the next set of results

        :return:
        """

        map = self.client.get_map(name)
        map.put(key=key, value=HazelcastJsonValue(json.dumps(result)))

        logging.debug('inserted object result {}'.format(key))
