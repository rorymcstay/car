import logging
from datetime import datetime

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
        history: List = self.hz.get_list("{}-history-{}".format(name, datetime.now().strftime("dd_mm_YY")))
        history.add(value)
        logging.info("history updated for {}".format(name))
        return "added one item to the cache"

    def getLastPage(self, name):
        history: List = self.hz.get_list("{}-history".format(name))
        size = history.size().result()
        return history.get(size-1).result()




