import logging as log
import threading
import traceback
from time import time

import bs4
import requests
from docker.errors import APIError
from kafka import KafkaProducer
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from settings import market_params, mongo_params, nanny_params
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.utils.BrowserConstants import BrowserConstants, getOpenPort
from src.main.market.utils.HealthStatus import HealthStatus
from src.main.service.mongo_service.MongoService import MongoService
from src.main.utils.LogGenerator import LogGenerator, write_log

LOG = LogGenerator(log, name='worker')


class Worker:
    mongoService: MongoService
    producer: KafkaProducer
    error = True
    stop = True
    thread = None

    def __init__(self):
        """
        Worker class has a browser container and selenium driver which it uses to collect cars in a seperate thread.

        :param batch_number:
        :param market:
        :param remote:
        """

        self.mongoService = MongoService('{host}:{port}'.format(**mongo_params))
        self.port = getOpenPort()
        self.batch_number = self.port
        self.market = market_params
        self.webCrawler = WebCrawler(self.port)
        self.producer = KafkaProducer()

    def prepareBatch(self, results, out):
        """
        prepare worker threads and distribute results amongst workers

        :param results:
        :param out:
        :return:
        """
        start = time()
        self.thread = threading.Thread(target=self.publishObjects, args=(results, out),
                                       name='Thread {}'.format(str(self.batch_number)))
        write_log(LOG.info, msg="batch_prepared", thread=self.batch_number, time=start, size=len(results))

    #   TODO the worker should write to Mongo in batches

    def publishObjects(self, results: list):
        """
        Updates a list provided called out. Intended to be used in a different thread in conjunction with multiple
        workers

        :param results: the batch or urls
        """

        try:
            for url in results:
                webTime = time()
                self.webCrawler.driver.get(url)
                write_log(LOG.debug, msg="page_loaded", time_elapsed=time() - webTime)
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, market_params['wait_for_car']))
                WebDriverWait(self.webCrawler.driver, BrowserConstants().worker_timeout).until(element_present)
                if market_params.get("worker_stream") is not None:
                    parser = bs4.BeautifulSoup(self.webCrawler.driver.page_source)
                    if market_params.get("worker_stream").get("single"):
                        self.producer.send(topic="{name}-{type}".format(**market_params, type="items"),
                                           value=bytes(str(parser.find(market_params.get("worker_stream").get("class"))), 'utf-8'),
                                           key=bytes(self.webCrawler.driver.current_url, 'utf-8'))
                    else:
                        items = parser.findAll(market_params.get("worker_stream").get("class"))
                        i = 0
                        for item in items:
                            i += 1
                            self.producer.send(topic="{name}-{type}".format(name=self.market.name, type="items"),
                                               value=bytes(item, 'utf-8'),
                                               key=bytes("{}_{}".format(self.webCrawler.driver.current_url, i), 'utf-8'))
                else:
                    self.producer.send(topic="{name}-{type}".format(name=self.market.name, type="items"),
                                       value=bytes(self.webCrawler.driver.page_source, "utf-8"),
                                       key=bytes(self.webCrawler.driver.current_url, "utf-8"))

        except WebDriverException:
            write_log(LOG.error, msg="webdriver_exception", thread=self.batch_number)
            traceback.print_exc()
            self.webCrawler = WebCrawler(self.port)
            write_log(LOG.info, thread=self.batch_number, msg="restarted_webCrawler")
        except APIError as e:
            write_log(LOG.error, msg="docker_api_error", thread=self.batch_number)
            traceback.print_exc()
            requests.get("{host}:{port}/{api_prefix}/freeContainer/{port}".format(self.port, **nanny_params))
            traceback.print_exc()
            self.webCrawler = WebCrawler(self.port)

    def healthCheck(self, exception: Exception = Exception('None')) -> HealthStatus:
        """
        Conduct a health check of resources

        :param exception:
        :return:
        """
        try:
            write_log(LOG.info, thread=self.batch_number, msg="doing_health_check")
            health = HealthStatus(exception,
                                  webCrawler=self.webCrawler.healthIndicator())
            write_log(log=LOG.debug, msg='health_check', **health)
            self.health = health
            return health
        except Exception as e:
            write_log(LOG.error, thread=self.batch_number,
                      msg="error taking health check for because {}".format(e.args[0]))
