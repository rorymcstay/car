import logging

from datetime import datetime
from hazelcast import HazelcastClient, ClientConfig

from settings import home_config, hazelcast_params


class RoutingManager(object):
    config = ClientConfig()
    config.network_config.addresses.append("{host}:{port}".format(**hazelcast_params))
    hz = HazelcastClient(config)

    def getBaseUrl(self, name, make, model, sort="newest"):
        for substring in home_config[name]["skeleton"]:
            url = "".format(substring).format(make=make, model=model, sort=home_config[name].get("sort_first")[sort])
            return url

    def updateHistory(self, name, value):
        logging.debug("history updated for {}".format(name))
        self.hz.get_map("{}_history".format(name)).put(value=value,key=datetime.now())
