import logging as log
import os
import threading
import traceback
from time import time

import bs4
from docker.errors import APIError
from kafka import KafkaProducer
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from settings import markets
from src.main.car.Domain import make_id
from src.main.market.browser.Browser import Browser
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.utils.BrowserConstants import BrowserConstants, get_open_port
from src.main.market.utils.HealthStatus import HealthStatus
from src.main.service.mongo_service.MongoService import MongoService
from src.main.utils.LogGenerator import LogGenerator, write_log

LOG = LogGenerator(log, name='worker')


class Worker:
    mongoService: MongoService
    producer: KafkaProducer

    def __init__(self, batch_number, market):
        """
        Worker class has a browser container and selenium driver which it uses to collect cars in a seperate thread.

        :param batch_number:
        :param market:
        :param remote:
        """
        self.params = markets[market.name]
        self.error = True
        self.stop = True
        self.cars_collected = 0
        self.thread = None
        self.mongoService = MongoService('{mongo_host}:{mongo_port}'.format(**self.params))
        self.batch_number = batch_number
        self.port = get_open_port()
        self.market = market
        self.browser = Browser(market.name, batch_number=self.batch_number, port=self.port)
        self.webCrawler = WebCrawler(self.market.name, self.port)
        self.producer = KafkaProducer()

    def prepare_batch(self, results, out):
        """
        prepare worker threads and distribute results amongst workers

        :param results:
        :param out:
        :return:
        """
        start = time()
        self.thread = threading.Thread(target=self.getCars, args=(results, out),
                                       name='Thread {}'.format(str(self.batch_number)))
        write_log(LOG.info, msg="batch_prepared", thread=self.batch_number, time=start, size=len(results))

    #   TODO the worker should write to Mongo in batches

    def getCars(self, results: list):
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
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, self.params['wait_for_car']))
                WebDriverWait(self.webCrawler.driver, BrowserConstants().worker_timeout).until(element_present)
                if self.params.get("worker_stream") is not None:
                    parser = bs4.BeautifulSoup(self.webCrawler.driver.page_source)
                    if self.params.get("worker_stream").get("single"):
                        self.producer.send(topic="{name}_{type}".format(name=self.market.name, type="car"),
                                           value=str(parser.find(self.params.get("worker_stream").get("class"))),
                                           key=self.webCrawler.driver.current_url,
                                           headers={"type": self.market.name})
                    else:
                        items = parser.findAll(self.params.get("worker_stream").get("class"))
                        i = 0
                        for item in items:
                            i += 1
                            self.producer.send(topic="{name}_{type}".format(name=self.market.name, type="car"),
                                               value=str(item),
                                               key="{}_{}".format(self.webCrawler.driver.current_url, i),
                                               headers={"type": self.market.name})
                else:
                    self.producer.send(topic="{name}_{type}".format(name=self.market.name, type="car"),
                                       value=self.webCrawler.driver.page_source,
                                       key=self.webCrawler.driver.current_url,
                                       headers={"type": self.market.name})

        except WebDriverException as e:
            write_log(LOG.error, msg="webdriver_exception", thread=self.batch_number)
            traceback.print_exc()
            self.webCrawler = WebCrawler(self.market, get_open_port())
            write_log(LOG.info, thread=self.batch_number, msg="restarted_webCrawler")
        except APIError as e:
            write_log(LOG.error, msg="docker_api_error", thread=self.batch_number)
            traceback.print_exc()
            self.clean_up()
            traceback.print_exc()
            self.browser = Browser(self.market.name, self.port, self.batch_number)
            self.webCrawler = WebCrawler(self.market, self.port)


    def health_check(self, exception: Exception = Exception('None')) -> dict:
        """
        Conduct a health check of resources

        :param exception:
        :return:
        """
        try:
            write_log(LOG.info, thread=self.batch_number, msg="doing_health_check")
            health = HealthStatus(exception,
                                  browser=self.browser.health_indicator(),
                                  webCrawler=self.webCrawler.health_indicator())
            write_log(log=LOG.debug, msg='health_check', browser=health.browser,
                      exception=health.exception_message,
                      webCrawler=health.webCrawler, collected=str(self.cars_collected))
            self.health = health
            return health.__dict__()
        except Exception as e:
            write_log(LOG.error, thread=self.batch_number,
                      msg="error taking health check for because {}".format(e.args[0]))

    def clean_up(self):
        """
        kill resources

        :return:
        """
        self.browser.quit()
        write_log(LOG.info, thread=self.batch_number, msg="cleaning up")

    def regenerate(self):
        self.port = get_open_port()
        self.browser = Browser(self.market.name, self.port, self.batch_number)
        self.webCrawler = WebCrawler(self.market, port=get_open_port())
        write_log(LOG.info, thread=self.batch_number, msg="restarted resources")

    def get_results(self, results):
        """
        Starts collect_cars routine by setting car busy to true. It starts it in a new thread.

        :return:
        """

        try:
            batchTime = time()
            scanned = 0
            scraped = 0
            for url in results:
                start = time()
                if self.stop is False:
                    return
                webTime = time()
                self.webCrawler.driver.get(url)
                write_log(LOG.debug, msg="page_loaded", time_elapsed=time() - webTime)
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, self.params['wait_for_car']))
                WebDriverWait(self.webCrawler.driver, BrowserConstants().worker_timeout).until(element_present)
                rawCar = self.webCrawler.get_raw_car()
                scanned += 1
                if rawCar is False:
                    write_log(LOG.warning, msg="no_car_found", thread=self.batch_number, time=time() - start,
                              scraped=scraped,
                              scanned=scanned, collected=self.cars_collected)
                    continue
                else:
                    scraped += 1
                    write_log(LOG.info, msg='car_found', thread=self.batch_number, time=time() - start, scraped=scraped,
                              scanned=scanned, collected=self.cars_collected)
                    try:
                        car = self.market.mapper(rawCar[0], url)
                        self.mongoService.insert_car(car=car, batch_number=self.batch_number)
                        # TODO check if any car._keys is None
                    except (KeyError, AttributeError) as e:
                        write_log(LOG.warning, "mapping_error", thread=self.batch_number, time=time() - start,
                                  scraped=scraped,
                                  scanned=scanned, collected=self.cars_collected)
                        if os.getenv("SAVE_RAWCAR", "False") == "False":
                            continue
                        failedRaw = rawCar[0]
                        failedRaw['_id'] = make_id(url)
                        try:
                            self.mongoService.db['{}_rawCar'.format(self.market.name)].insert_one(failedRaw)
                            write_log(LOG.info, thread=self.batch_number, msg="saved_raw_car")
                        except Exception:
                            write_log(LOG.warning, "saving_error", thread=self.batch_number, time=time() - start,
                                      scraped=scraped,
                                      scanned=scanned, collected=self.cars_collected)
                            traceback.print_exc()
                        continue
                    self.cars_collected += 1
                    write_log(LOG.info, msg="processed_car", thread=self.batch_number, time=time() - start,
                              scraped=scraped,
                              scanned=scanned, collected=self.cars_collected)
            write_log(LOG.info, msg="finished_batch", thread=self.batch_number, time=time() - batchTime,
                      scraped=scraped,
                      scanned=scanned, collected=self.cars_collected)

        except WebDriverException as e:
            write_log(LOG.error, msg="webdriver_exception", thread=self.batch_number)
            traceback.print_exc()
            self.webCrawler = WebCrawler(self.market.name, port=get_open_port())
            write_log(LOG.info, thread=self.batch_number, msg="restarted_webCrawler")
        except APIError as e:
            write_log(LOG.error, msg="docker_api_error", thread=self.batch_number)
            traceback.print_exc()
            self.clean_up()
            traceback.print_exc()
            self.browser = Browser(self.market.name, self.port, self.batch_number)
            self.webCrawler = WebCrawler(self.market, port=get_open_port())
