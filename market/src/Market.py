import threading
import logging as LOG
import traceback
from telnetlib import EC

from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from car.market.src.crawling.WebCrawler import WebCrawler, ExcludedResultNotifier, EndOfQueueNotification
from car.market.src.mongo_service.MongoService import MongoService
import logging


class Market:

    def __init__(self, name,
                 result_css,
                 result_exclude,
                 wait_for_car,
                 json_identifier,
                 next_page_xpath, mapper, router, remote=False):
        logging.getLogger('Market: %s' % name)
        """
        :type remote: BrowserService
        """
        self.name = name

        self.next_page_xpath = next_page_xpath
        self.result_css = result_css
        self.result_exclude = result_exclude
        self.wait_for_car = wait_for_car
        self.json_identifier = json_identifier

        self.mapper = mapper
        self.home = router

        self.service = MongoService()
        self.busy = False

        if remote is False:
            # starting dedicated browser container
            self.crawler = WebCrawler(self)
            return

        self.browser = remote
        self.crawler = WebCrawler(self, remote)

    def collect_cars(self):
        """
        Loads up the market's cache preparing it for mapping
        :param order:
        :param n:
        :return fills market.:
        """

        x = 0
        while self.busy:
            LOG.info("Page:%s", str(x))
            LOG.debug("Queue length %s", self.crawler)

            for i in self.crawler.get_queue_length():
                rawCars = False
                # Check if any of exclusion items are contained within the next attempt

                try:
                    result = self.crawler.get_queue_member(i, self.result_exclude)
                    rawCars = self.crawler.get_result(result, 120)
                except ExcludedResultNotifier:
                    pass
                except EndOfQueueNotification:
                    break
                except StaleElementReferenceException:
                    self.crawler.return_to_last_page()
                    pass
                except NoSuchElementException:
                    LOG.error("Could not find element")
                    self.crawler.return_to_last_page()
                    pass
                if rawCars is not False:
                    LOG.debug('Got raw car from %s', self.crawler.driver.current_url)
                    for rawCar in rawCars:
                        try:
                            car = self.mapper(rawCar)
                            LOG.debug('Saving result from %s', self.crawler.driver.current_url)
                            self.service.insert(car)
                            # TODO handle fails when saving to the database in MongoService
                            LOG.info('Saved result from %s', self.crawler.driver.current_url)
                        except Exception, e:
                            # TODO move error handling to respective services
                            LOG.warn('failed result from %s \n %s', self.crawler.driver.current_url, e.message)
                            traceback.print_exc()
                            pass
            self.crawler.next_page(200)

            x = x + 1

    def start(self):
        self.crawler.driver.get(self.home)
        self.busy = True
        thread = threading.Thread(target=self.collect_cars(), args=())
        thread.daemon = True
        thread.start()
        return "started"

    def resume(self):
        self.busy = True
        thread = threading.Thread(target=self.collect_cars(), args=())
        thread.daemon = True
        thread.start()
        return "resumed"

    def stop(self):
        self.busy = False
        return "paused"
