import logging
import time

from hazelcast import HazelcastClient, ClientConfig
from hazelcast.proxy import List

from settings import home_config, hazelcast_params


class RoutingManager(object):
    config = ClientConfig()
    config.network_config.addresses.append("{host}:{port}".format(**hazelcast_params))
    hz = HazelcastClient(config)

    def getBaseUrl(self, name, make, model, sort="newest"):
        url=""
        for substring in home_config[name]["skeleton"]:
            url = url + substring
        url = url.format(make=make, model=model, sort=home_config[name].get("sort_first")[sort])
        return url

    def updateHistory(self, name, value):
        histName = "{}-history-{}".format(name,  time.strftime("%d_%m"))
        history: List = self.hz.get_list(histName)
        history.add(value)
        logging.info("history updated for {}".format(histName))
        return "added one item to the cache"

    def getLastPage(self, name):
        histName = "{}-history-{}".format(name, time.strftime("%d_%m"))
        history: List = self.hz.get_list(histName)
        num = history.size().result()
        if num < 1:
            return False
        size = history.size().result()
        return history.get(size-1).result()




