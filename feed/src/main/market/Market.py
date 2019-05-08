import logging as log
from typing import List

import bs4
import requests as r
from kafka import KafkaProducer

from settings import kafka_params, routing_params, market_params
from src.main.market.Worker import Worker
from src.main.market.crawling.crawling import WebCrawler
from src.main.utils.LogGenerator import LogGenerator, write_log

LOG = LogGenerator(log, name='market')


class Market:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Market, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    workers: List[Worker] = []
    make = None
    model = None
    sort = None

    results = None
    results_batched = None
    busy = False
    browsers = []

    kafkaProducer = KafkaProducer(**kafka_params)

    def __init__(self):
        self.webCrawler = WebCrawler()

    def goHome(self):
        """
        navigate back to the base url
        :return:
        """

        routingEndpoint = "http://{host}:{port}/{api_prefix}/getBaseUrl/{name}/{make}/{model}/{sort}".format(make=self.make,
                                                                                                             model=self.model,
                                                                                                             sort=self.sort,
                                                                                                             **routing_params, **market_params)
        request = r.get(routingEndpoint)
        self.webCrawler.driver.get(request.text)
        return routingEndpoint

    def setHome(self, make=None, model=None, sort=None):
        self.make = make
        self.model = model
        self.sort = sort
        return self.goHome()

    def publishListOfResults(self):
        parser = bs4.BeautifulSoup(self.webCrawler.driver.page_source, features="html.parser")
        results = parser.findAll(attrs={"class": market_params['result_stream'].get("class")})
        i = 0
        for result in results:
            data = dict(value=bytes(str(result), 'utf-8'),
                        key=bytes("{}_{}".format(self.webCrawler.driver.current_url, i), 'utf-8'))
            self.kafkaProducer.send(topic="{name}-results".format(**market_params), **data)
            i += 1
        write_log(LOG.info, msg="published to kafka", results=i)
