import logging as log
import sys
import threading
import traceback
from time import time

from docker.errors import APIError
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.main.market.browser.Browser import Browser
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.utils.BrowserConstants import BrowserConstants, get_open_port
from src.main.market.utils.HealthStatus import HealthStatus
from src.main.service.mongo_service.MongoService import MongoService
from src.main.utils.LogGenerator import LogGenerator, write_log

LOG = LogGenerator(log, name='worker')


class Worker:
    def __init__(self, batch_number, market, remote=False):
        self.stop = True
        self.cars_collected = 0
        self.scanned=0
        self.scraped=0
        self.thread = None
        self.mongo = MongoService(market.mongo_host)
        self.batch_number = batch_number
        self.port = get_open_port()
        self.market = market
        self.remote = remote
        self.browser = Browser(market.name, batch_number=self.batch_number, port=self.port)
        self.webCrawler = WebCrawler(self.market, remote=self.make_url())

    def prepare_batch(self, results=None):
        self.thread = threading.Thread(target=self.get_results, args=([results]),
                                       name='Thread %s' % str(self.batch_number))

    #   TODO the worker should write to Mongo in batches
    def get_results(self, results):
        """
        Starts collect_cars routine by setting car busy to true. It starts it in a new thread.
        :return:
        """
        try:
            self.health_check()
            for url in results:
                start = time()
                if self.stop is False:
                    return
                self.webCrawler.driver.get(url)
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, self.market.wait_for_car))
                WebDriverWait(self.webCrawler.driver, BrowserConstants().worker_timeout).until(element_present)
                rawCar = self.webCrawler.get_raw_car()
                self.scanned=self.scanned+1
                write_log(LOG.info, msg='', thread=self.batch_number, scanned=self.scanned)
                if rawCar is False:
                    write_log(LOG.warning, msg="failed", thread=self.batch_number, url=url)
                    continue
                else:
                    self.scraped += 1
                    write_log(LOG.info, msg='have_raw_car', thread=self.batch_number, scraped=self.scraped)
                    try:
                        car=self.market.mapper(rawCar[0], url)
                        self.mongo.insert_car(car=car, batch_number=self.batch_number)
                    except (KeyError, AttributeError) as e:
                        write_log(LOG.warning, "saving_error", thread=self.batch_number)
                        traceback.print_exc()
                        self.health_check(e)
                        continue
                    self.cars_collected += 1
                    elapsed = time() - start
                    write_log(LOG.info, msg="saved_car", thread=self.batch_number, time=elapsed)
            write_log(LOG.info, msg="finished_batch", thread=self.batch_number)
            self.health_check()
        except WebDriverException as e:
            try:
                self.health_check(e.msg)
                traceback.print_exc()
                self.webCrawler = WebCrawler(self.market, remote=self.make_url())
                write_log(LOG.info, thread=self.batch_number, msg="restarted_webCrawler")
            except Exception as e:
                self.health_check(e.args[0])
                traceback.print_exc()
                self.clean_up()
                write_log(LOG.error, thread=self.batch_number, msg="failed to restart webCrawler")
                sys.exit(1)
        except APIError as e:
            try:
                self.health_check(e.status_code)
                traceback.print_exc()
                self.clean_up()
                traceback.print_exc()
                self.browser = Browser(self.market.name, self.port, self.batch_number)
                self.webCrawler = WebCrawler(self.market, remote=self.make_url())
            except Exception as e:
                self.health_check(e)
                traceback.print_exc()
                self.clean_up()
                write_log(LOG.error, msg="failed to restart resources - killing thread", thread=self.batch_number)
                sys.exit(1)



    def make_url(self):
        if self.remote is False:
            return False
        host = BrowserConstants().host
        # host = self.browser.browser.name
        post_fix = BrowserConstants().client_connect
        return "http://{}:{}/{}".format(host, self.port, post_fix)

    def health_check(self, exception=Exception('None')):
        try:
            self.health = HealthStatus(exception,
                                       browser=self.browser.health_indicator(),
                                       webcrawler=self.webCrawler.health_indicator())
            write_log(log=LOG.debug, msg='health_check', browser=self.health.browser,exception=self.health.exception_message,
                      webCrawler=self.health.webcrawler, collected=str(self.cars_collected))
        except Exception as e:
            write_log(LOG.error, thread=self.batch_number, msg="error taking health check for because {}".format(e.args[0]))

    def clean_up(self):
        self.browser.quit()
        write_log(LOG.info, thread=self.batch_number, msg="cleaning up")

    def regenerate(self):
        self.browser = Browser(self.market.name, self.batch_number)
        self.webCrawler = WebCrawler(self.market, remote=self.make_url())
        write_log(LOG.info, thread=self.batch_number, msg="restarted resources")
