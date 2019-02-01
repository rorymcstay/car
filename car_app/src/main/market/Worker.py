import logging as LOG
import os
import threading
import traceback
from time import sleep

from docker.errors import APIError
from selenium.common.exceptions import WebDriverException

from market.browser.Browser import Browser
from market.crawling.WebCrawler import WebCrawler
from market.utils.BrowserConstants import BrowserConstants
from market.utils.HealthStatus import HealthStatus
from service.mongo_service.MongoService import MongoService


class Worker:
    def __init__(self, batch_number, market, remote=False):
        self.cars_collected = 0
        self.thread = None
        self.mongo = MongoService()
        self.batch_number = batch_number
        self.port = BrowserConstants().base_port + batch_number
        self.market = market
        self.remote = remote
        self.browser = Browser(market.name, batch_number, remote)
        self.webCrawler = WebCrawler(self.market, remote=self.make_url())

    def get_results(self, results, timeout):
        """
        Starts collect_cars routine by setting car busy to true. It starts it in a new thread.
        :return:
        """
        try:
            self.health_check(level=LOG.debug)
            for url in results:
                self.webCrawler.driver.get(url)
                sleep(timeout)
                rawCar = self.webCrawler.get_raw_car()
                if rawCar is False:
                    LOG.warning("thread %s missed their car - %s", self.batch_number, url)
                else:
                    self.cars_collected += 1
                    self.mongo.insert(self.market.mapper(rawCar[0], url))
                    LOG.info("thread %s saved their car - %s", self.batch_number, url)
            LOG.info("Thread %s has finished there batch", self.batch_number)
        except KeyboardInterrupt as stop:
            self.health_check(stop.args[0])
            self.browser.quit()
            LOG.info("Killing browser %s", self.batch_number)
            raise stop
        except WebDriverException as e:
            try:
                self.health_check(e.msg)
                LOG.error("Webcrawler in thread %s had a WebDriver exception: ", self.batch_number, e.msg)
                traceback.print_exc()
                self.webCrawler.driver.quit()
                self.webCrawler = WebCrawler(self.market, remote=self.make_url())
                LOG.info("Webcrawler in thread %s restarted", self.batch_number)
            except Exception as e:
                self.health_check(e.args[0])
                traceback.print_exc()
                LOG.error("Thread %s failed to restart", self.batch_number)
        except APIError as e:
            try:
                self.health_check(e.status_code)
                LOG.error("DockerClient in thread %s had an APIError: %s", self.batch_number, e.explanation)
                traceback.print_exc()
                self.webCrawler.driver.quit()
                self.browser.restart()
                traceback.print_exc()
                self.webCrawler = WebCrawler(self.market, remote=self.make_url())
                LOG.info("Webcrawler in thread %s restarted", self.batch_number)
            except Exception as e:
                self.health_check(e.args[0])
                traceback.print_exc()
                LOG.error("Thread %s failed to restart: %s", self.batch_number, e.args)
        except KeyError as e:
            self.health_check(e.args[0])
            LOG.error('Thread %s KeyError: %s', self.batch_number, e)
            pass

    def prepare_batch(self, results=None):
        self.health_check()
        self.thread = threading.Thread(target=self.get_results, args=(results, int(os.environ['WORKER_TIMEOUT'])),
                                       name='Thread %s' % str(self.batch_number))

    def make_url(self):
        if self.remote is False:
            return False
        port = self.batch_number + BrowserConstants().base_port
        host = BrowserConstants().host
        post_fix = BrowserConstants().client_connect
        return "http://%s:%s/%s" % (host, port, post_fix)

    def health_check(self, exception='None', level=LOG.info):
        health = HealthStatus(exception,
                              browser=self.browser.health_indicator(),
                              webcrawler=self.webCrawler.health_indicator())
        level(
            """
            Thread {0}: |exception |browser |webCrawler
                        |{1}       |{2}     |{3}
                        _______________________________
            """.format(str(self.batch_number),
                       exception,
                       health.browser,
                       health.webcrawler))
