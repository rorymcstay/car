import logging

import hazelcast

config = hazelcast.ClientConfig()
config.group_config.name = 'car-cluster'
config.group_config.password = 'password'

config.network_config.addresses.append('127.0.0.1')
config.network_config.addresses.append('192.168.1.99')
config.network_config.addresses.append('localhost:5702')


class CacheManager:

    client = hazelcast.client.HazelcastClient()

    def insertResult(self, name, result):
        """
        request the next set of results

        :return:
        """

        self.client.get_map(name).put(key=result['_id'], value=result)
        logging.debug('inserted car result {}'.format(result['_id']))
