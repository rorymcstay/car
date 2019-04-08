import os
import threading

import requests

from src.main.mapper.manager import CacheManager

feedConnection = {
    'host': os.getenv('FEED_HOST', 'localhost'),
    'port': os.getenv('FEED_PORT', 5000)
}

feedHost = 'http://{host}:{port}'.format(**feedConnection)
loadNext = lambda market: '{feedHost}/command/get_results/{market}'.format(feedHost=feedHost, market=market)
cacheManager = CacheManager()
markets = ['donedeal']

def getAllResults():
    out = []
    threads = [threading.Thread(target=getResults, args=(market, out)) for market in markets]
    cacheManager.insert()

def getResults(market: str, out):
    """
    append results to list
    :param market: the market to get
    :param out: the list to add to
    :return:
    """
    r = requests.get(loadNext(market))
    out.append(r.json())