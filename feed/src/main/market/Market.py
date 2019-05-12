import logging
import logging as log

import bs4
import requests as r
from kafka import KafkaProducer

from settings import kafka_params, routing_params, feed_params
from src.main.market.crawling.crawling import WebCrawler
from src.main.utils.LogGenerator import LogGenerator

LOG = LogGenerator(log, name='market')


class Market:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Market, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

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

    def renewWebCrawler(self):
        self.webCrawler.quit()
        self.webCrawler = WebCrawler()
        last = r.get("http://{host}:{port}/{api_prefix}/getLastPage/{name}".format(**routing_params, **feed_params)).text
        logging.info("navigating to latest page {}".format(last))
        self.webCrawler.driver.get(last)

    def goHome(self):
        """
        navigate back to the base url
        :return:
        """

        routingEndpoint = "http://{host}:{port}/{api_prefix}/getBaseUrl/{name}/{make}/{model}/{sort}".format(make=self.make,
                                                                                                             model=self.model,
                                                                                                             sort=self.sort,
                                                                                                             **routing_params, **feed_params)
        request = r.get(routingEndpoint)
        self.webCrawler.driver.get(request.text)
        logging.info("navigated home")
        return routingEndpoint

    def setHome(self, make=None, model=None, sort=None):
        self.make = make
        self.model = model
        self.sort = sort
        return self.goHome()

    def publishListOfResults(self):
        parser = bs4.BeautifulSoup(self.webCrawler.driver.page_source, features="html.parser")
        results = parser.findAll(attrs={"class": feed_params['result_stream'].get("class")})
        logging.debug("parsed {} results from {}".format(len(results), self.webCrawler.driver.current_url))
        i = 0
        for result in results:
            data = dict(value=bytes(str(result), 'utf-8'),
                        key=bytes("{}_{}".format(self.webCrawler.driver.current_url, i), 'utf-8'))
            self.kafkaProducer.send(topic="{name}-results".format(**feed_params), **data)
            i += 1
            logging.debug("published {} results".format(i))
        logging.info("parsed {} results from {}".format(len(results), self.webCrawler.driver.current_url))
