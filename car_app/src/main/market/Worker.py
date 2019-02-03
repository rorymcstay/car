import os
import threading
import traceback
from time import sleep

from docker.errors import APIError
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.main.market.browser.Browser import Browser
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.utils.BrowserConstants import BrowserConstants
from src.main.market.utils.HealthStatus import HealthStatus
from src.main.utils.LogGenerator import create_log_handler
from src.main.service.mongo_service.MongoService import MongoService

LOG = create_log_handler('worker')


class Worker:
    def __init__(self, batch_number, market, remote=False):
        self.cars_collected = 0
        self.thread = None
        self.mongo = MongoService()
        self.batch_number = batch_number
        self.port = BrowserConstants().base_port + batch_number
        self.market = market
        self.remote = remote
        self.browser = Browser(market.name, batch_number)
        self.webCrawler = WebCrawler(self.market, remote=self.make_url())

    #   TODO the worker should write to Mongo in batches
    def get_results(self, results):
        """
        Starts collect_cars routine by setting car busy to true. It starts it in a new thread.
        :return:
        """
        try:
            self.health_check(level=LOG.debug)
            for url in results:
                self.webCrawler.driver.get(url)
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, self.market.wait_for_car))
                WebDriverWait(self.webCrawler.driver, BrowserConstants().worker_timeout).until(element_present)
                rawCar = self.webCrawler.get_raw_car()
                if rawCar is False:
                    LOG.warning("Thread-%s: Failed-%s", self.batch_number, url)
                else:
                    self.cars_collected += 1
                    self.mongo.insert(self.market.mapper(rawCar[0], url))
                    LOG.info("Thread %s saved their car - %s", self.batch_number, url)
            LOG.info("Thread %s has finished there batch", self.batch_number)
            self.health_check()
        except KeyboardInterrupt as stop:
            self.health_check(stop.args[0])
            self.clean_up()
            LOG.info("Killing browser %s", self.batch_number)
            raise stop
        except WebDriverException as e:
            try:
                self.health_check(e.msg)
                LOG.error("Thread {}: webdriver exception: {}".format(self.batch_number, e.msg))
                traceback.print_exc()
                self.webCrawler = WebCrawler(self.market, remote=self.make_url())
                LOG.info("Thread {}: restarted webCrawler".format(self.batch_number))
            except Exception as e:
                self.health_check(e.args[0])
                traceback.print_exc()
                self.clean_up()
                LOG.error("Thread {}: failed to restart webCrawler".format(self.batch_number))
        except APIError as e:
            try:
                self.health_check(e.status_code)
                LOG.error("Thread {}: docker APIError: {}".format(self.batch_number, e.explanation))
                traceback.print_exc()
                self.clean_up()
                traceback.print_exc()
                self.browser = Browser(self.market.name, self.batch_number)
                self.webCrawler = WebCrawler(self.market, remote=self.make_url())
                LOG.info("Thread {}: restarted resources".format(self.batch_number))
            except Exception as e:
                self.health_check(e)
                traceback.print_exc()
                self.clean_up()
                LOG.error("Thread {}: failed to restart resources: {}".format(self.batch_number, e.args))
        except (KeyError, AttributeError) as e:
            self.health_check(e)
            LOG.error('Thread {}: KeyError: {}'.format(self.batch_number, e.args[0]))
            pass

    def prepare_batch(self, results=None):
        self.thread = threading.Thread(target=self.get_results, args=([results]),
                                       name='Thread %s' % str(self.batch_number))

    def make_url(self):
        if self.remote is False:
            return False
        port = self.batch_number + BrowserConstants().base_port
        host = BrowserConstants().host
        # host = self.browser.browser.name
        post_fix = BrowserConstants().client_connect
        return "http://%s:%s/%s" % (host, port, post_fix)

    def health_check(self, exception=Exception('None'), level=LOG.info):
        try:
            self.health = HealthStatus(exception,
                                       browser=self.browser.health_indicator(),
                                       webcrawler=self.webCrawler.health_indicator())
            level("Thread {0}: |exception: {1}  |browser: {2} |webCrawler: {2}|collected: {4} "
                  .format(str(self.batch_number),
                          self.health.exception_message,
                          self.health.browser,
                          self.health.webcrawler, self.cars_collected))
        except Exception as e:
            LOG.error("Thread {0}: error taking health check for because {1}", self.batch_number, e.args[0])

    def clean_up(self):
        self.browser.quit()
        self.webCrawler.quit()

    def regenerate(self):
        self.browser = Browser(self.market.name, self.batch_number)
        self.webCrawler = WebCrawler(self.market, remote=self.make_url())
        LOG.info('Thread {}: resources regenerated'.format(self.batch_number))
