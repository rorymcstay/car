import logging
import time

from hazelcast import HazelcastClient, ClientConfig
from hazelcast.proxy import List

from settings import home_config, hazelcast_params


class RoutingManager(object):
    config = ClientConfig()
    config.network_config.addresses.append("{host}:{port}".format(**hazelcast_params))
    hz = HazelcastClient(config)

    def getResultPageUrl(self, name, make=None, model=None, page=None, sort="newest"):
        if page is not None:
            page = home_config[name]["page"]["increment"]*page
        url = ""
        for substring in home_config[name]["skeleton"]:
            if "MAKE" in substring.upper() and make is None:
                continue
            if "MODEL" in substring.upper() and model is None:
                continue
            if "PAGE" in substring.upper() and page is None:
                continue
            url = url + substring
        url = url.format(make=make, model=model, page=page, sort=home_config[name].get("sort_first")[sort])
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
        last = history.get(size-1).result()
        return str(last, "utf-8")

    def clearHistory(self, name):
        histName = "{}-history-{}".format(name, time.strftime("%d_%m"))
        history: List = self.hz.get_list(histName)
        history.clear()

        




