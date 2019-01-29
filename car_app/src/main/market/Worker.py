import logging as LOG
import os
import threading
import traceback
from time import sleep

from market.browser.Browser import Browser
from market.crawling.WebCrawler import WebCrawler
from service.mongo_service.MongoService import MongoService
from utils.QuitBrowser import quit_browser


class Worker:
    def __init__(self, batch_number, market, remote=False):
        self.thread = None
        self.mongo = MongoService()
        self.batch_number = batch_number
        self.market = market
        self.remote = remote
        if remote:
            self.browser_service = Browser(os.environ['HUB'], os.environ['BROWSER']).new_service(
                "donedeal_%s" % batch_number)
            self.hub = self.browser_service.new_service()
            self.browser = WebCrawler(self, remote=self.hub['url'])
        else:
            self.hub = {'url': remote}
            self.browser = WebCrawler(market)

    def get_results(self, results, timeout):
        """
        Starts collect_cars routine by setting car busy to true. It starts it in a new thread.
        :return:
        """
        try:
            for url in results:
                self.browser.driver.get(url)
                sleep(timeout)
                rawCar = self.browser.get_raw_car()
                if rawCar is False:
                    LOG.warning("thread %s missed their car - %s", self.batch_number, url)
                else:
                    self.mongo.insert(self.market.mapper(rawCar[0], url))
                    LOG.info("thread %s saved their car - %s", self.batch_number, url)
        except KeyboardInterrupt as stop:
            quit_browser(browser=self.browser)
            raise stop
        except Exception as e:
            quit_browser(browser=self.browser)
            traceback.print_exc()
            LOG.error(e)
            self.browser = WebCrawler(self.market, self.hub['url'])

    def prepare_batch(self, results=None):
        self.thread = threading.Thread(target=self.get_results, args=(results, int(os.environ['WORKER_TIMEOUT'])))

        # browser['hub'].kill()
        # browser['browser'].kill()
        return
