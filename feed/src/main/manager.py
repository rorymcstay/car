import itertools
import json
import logging as log

import bs4
import requests as r
from kafka import KafkaProducer

from settings import kafka_params, routing_params, feed_params
from src.main.crawling import WebCrawler

logging = log.getLogger(__name__)


class FeedManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FeedManager, cls).__new__(
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
        logging.info("renewing webcrawler")
        self.webCrawler = WebCrawler()

    def goHome(self):
        """
        navigate back to the base url, router sends a string like "url,multiple"
        :return:
        """

        home = r.get("http://{host}:{port}/{api_prefix}/getLastPage/{name}".format(**routing_params, **feed_params))

        if home.text == "none":
            home = "http://{host}:{port}/{api_prefix}/getResultPageUrl/{name}".format(**routing_params, **feed_params)
            home = r.get(home, data=json.dumps(dict(make=self.make,
                                                    model=self.model,
                                                    sort=self.sort)),
                         headers={"content-type": "application/json"})
            url = home.text
        elif feed_params["page_url_param"].upper() in home.json()["url"].upper():
            data = home.json()
            url = str(data["url"])
            split = url.split("=")
            for (num, l) in enumerate(split):
                if feed_params["page_url_param"].lower() in l.lower():
                    parsed = "".join(itertools.takewhile(str.isdigit, split[num + 1]))
                    self.webCrawler.page = int(int(parsed)/int(data["increment"]))
                    break
        else:
            data = home.json()
            url = str(data["url"])
        logging.debug("navigating to starting point {}".format(url))
        self.webCrawler.driver.get(url)
        logging.info("navigated to {} ok".format(url))
        return home

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
