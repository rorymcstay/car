import os
import threading
import logging as LOG
import time
import traceback
import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from car.src.main.market.crawling.WebCrawler import WebCrawler
from car.src.main.market.crawling.Exceptions import ExcludedResultNotifier, EndOfQueueNotification, ResultCollectionFailure
from car.src.main.service.mongo_service.MongoService import MongoService
from car.src.main.market.browser.Browser import BrowserService


class Market:

    def __init__(self, name,
                 result_css,
                 result_exclude,
                 wait_for_car,
                 json_identifier,
                 next_page_xpath, result_stub, mapper, router, next_button_text, remote=False):

        self.threads = []
        self.result_stub = result_stub
        self.results = None
        logging.getLogger('Market: %s' % name)
        """
        :type remote: BrowserService
        """
        self.name = name
        self.next_button_text = next_button_text

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



    def collect_cars(self, single= None):
        """
        Routine for collecting cars. Runs whilst self.market.busy is true. It handles exceptions defined in
        crawling.Exceptions. It uses MongoService to  persist cars to the mongo database in a docker container.
        """
        x = 0
        while self.busy:
            LOG.info("Page:%s", str(x))
            LOG.debug("Queue length %s", self.crawler)
            if single is None:
                queue = self.crawler.get_queue_length()
            else:
                queue = [single]
            for i in queue: # TODO Handle webdriver exceptions within this block
                rawCars = False
                try:
                    result = self.crawler.get_queue_member(i, self.result_exclude)
                    rawCars = self.crawler.get_result(result)

                except ExcludedResultNotifier:
                    LOG.warn("Skipped excluded result")
                    pass
                except EndOfQueueNotification:
                    LOG.warn("End of queue")
                    break
                except ResultCollectionFailure, QueueServicingError:
                    LOG.warn("Result collection error")
                    pass
                except NoSuchElementException:
                    LOG.error("Could not find car")
                    self.crawler.latest_page()
                    pass
                try:
                    self.crawler.driver.get(self.crawler.last_result)
                    element_present = EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.result_css))
                    WebDriverWait(self.crawler.driver, int(os.environ['RETURN_TIMEOUT'])).until(element_present)
                except TimeoutException:
                    LOG.warn("timeout exception")
                if rawCars is not False:
                    LOG.debug('Got raw car from %s', self.crawler.driver.current_url)
                    for rawCar in rawCars['result']:
                        try:
                            car = self.mapper(rawCar, rawCar['url'])
                            LOG.debug('Saving result from %s', self.crawler.driver.current_url)
                            self.service.insert(car)
                            # TODO handle fails when saving to the database in MongoService
                            LOG.info('Saved result from %s', self.crawler.driver.current_url)
                        except Exception, e:
                            # TODO move error handling to respective services
                            LOG.warn('failed result from %s \n %s', self.crawler.driver.current_url, e.message)
                            traceback.print_exc()
                            pass
            next = self.crawler.next_page()
            if not next:
                self.crawler.retrace_steps(x)
            x = x + 1

    def start_worker(self, queue_member, timeout):
        """
        Starts collect_cars routine by setting car busy to true. It starts it in a new thread.
        :return:
        """
        browser = BrowserService(os.environ['HUB'], os.environ['BROWSER']).new_service("donedeal_%s" % queue_member)
        mongo = MongoService()
        worker = WebCrawler(self, remote=browser)
        worker.driver.get(self.home)
        while self.busy:
            url = self.get_result(queue_member)
            worker.driver.get(url)
            time.sleep(timeout)
            rawCar = worker.get_raw_car()
            if rawCar is False:
                LOG.warn("%s_%s missed their car - %s", self.name, queue_member, url)
            else:
                mongo.insert(rawCar)
                LOG.info("%s_%s saved their car - %s", self.name, queue_member, url)

        browser['hub'].kill()
        browser['browser'].kill()
        return

    def start(self):
        self.busy = True
        thread = threading.Thread(target=self.collect_cars, args=(), name='%s_simple' % self.name)
        thread.daemon = True
        thread.start()
        return "ok"

    def set_results(self, list):
        self.results = list

    def get_result(self, item):
        return self.results[item]

    def start_parrallel(self):
        self.busy = True
        self.threads = []
        self.crawler.driver.get(self.home)
        queue = self.crawler.get_queue_length()
        self.set_results(self.crawler.get_result_array())
        for i in queue:
            thread = threading.Thread(target=self.start_worker, args=(i, 3), name='%s_%s' % (self.name, i))
            thread.daemon = True
            self.threads.append(thread)

        for thread in self.threads:
            thread.start()

        self.crawler.driver.get(self.home)
        while self.busy:
            time.sleep(1)
            self.set_results(self.crawler.get_result_array())
            time.sleep(5)
            self.crawler.next_page()

    def resume(self):
        self.busy = True
        thread = threading.Thread(target=self.collect_cars(), args=())
        thread.daemon = True
        thread.start()
        return "resumed"

    def stop(self):
        self.busy = False
        return "paused"
