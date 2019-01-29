import numpy
import os
import threading
import logging as LOG
import traceback
import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from market.Worker import Worker
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.crawling.Exceptions import ExcludedResultNotifier, EndOfQueueNotification, ResultCollectionFailure
from src.main.service.mongo_service.MongoService import MongoService


class Market:

    def __init__(self, name,
                 result_css,
                 result_exclude,
                 wait_for_car,
                 json_identifier,
                 next_page_xpath, result_stub, mapper, router, next_button_text, remote=False):
        """

        :param name: name of market place for reference
        :param result_css: the css path to the result item
        :param result_exclude: an array of strings to exclude from car result body text
        :param wait_for_car: item on page to wait for for car
        :param json_identifier:
        :param next_page_xpath:
        :param result_stub:
        :param mapper:
        :param router:
        :param next_button_text:
        :param remote:
        """
        self.browsers = []
        self.workers = []
        self.result_stub = result_stub
        self.results = None
        self.results_batched = None
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
            self.crawler = WebCrawler(self)
            return

        self.browser = remote
        # starting dedicated browser container
        self.crawler = WebCrawler(self, remote)

    def collect_cars(self, single=None):
        """
        Routine for collecting cars. Runs whilst self.market.busy is true. It handles exceptions defined in
        crawling.Exceptions. It uses MongoService to  persist cars to the mongo database in a docker container.
        """
        x = 0
        while self.busy:
            LOG.info("Page:%s", str(x))
            LOG.debug("Queue length %s", self.crawler)
            if single is None:
                queue = self.crawler.get_queue_range()
            else:
                queue = [single]
            for i in queue: # TODO Handle webdriver exceptions within this block
                raw_cars = False
                try:
                    result = self.crawler.get_queue_member(i, self.result_exclude)
                    raw_cars = self.crawler.get_result(result)

                except ExcludedResultNotifier:
                    LOG.warning("Skipped excluded result")
                    pass
                except EndOfQueueNotification:
                    LOG.warning("End of queue")
                    break
                except ResultCollectionFailure:
                    LOG.warning("Result collection error")
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
                    LOG.warning("timeout exception")
                if raw_cars is not False:
                    LOG.debug('Got raw car from %s', self.crawler.driver.current_url)
                    for rawCar in raw_cars['result']:
                        try:
                            car = self.mapper(rawCar, raw_cars['url'])
                            LOG.debug('Saving result from %s', self.crawler.driver.current_url)
                            self.service.insert(car)
                            # TODO handle fails when saving to the database in MongoService
                            LOG.info('Saved result from %s', self.crawler.driver.current_url)
                        except Exception as e:
                            # TODO move error handling to respective services
                            LOG.warning('failed result from %s \n %s', self.crawler.driver.current_url, e.msg)
                            traceback.print_exc()
                            pass
            go_next = self.crawler.next_page()
            if not go_next:
                self.crawler.retrace_steps(x)
            x = x + 1

    def start(self):
        """
        Starts collect_cars routine by setting car busy to true. It starts it in a new thread.
        :return:
        """
        self.crawler.driver.get(self.home)
        self.crawler.latest_page = self.home
        self.busy = True
        thread = threading.Thread(target=self.collect_cars, args=())
        thread.daemon = True
        thread.start()
        return "started"

    def start_parrallel(self, max_containers, remote=True):
        self.busy = True
        self.crawler.driver.get(self.home)
        latest_results = self.crawler.get_result_array()
        self.workers = [Worker(i, self) for i in range(min(max_containers, len(latest_results)))]
        while self.busy:
            results = self.crawler.get_result_array()
            batches = numpy.array_split(results, min(max_containers, len(results)))
            for (w, b) in zip(self.workers, batches):
                w.prepare_batch(b)
            self.crawler.next_page()
            [t.thread.start() for t in self.workers]
            [t.thread.join() for t in self.workers]
            self.crawler.update_latest_page(1)

    def resume(self):
        self.busy = True
        thread = threading.Thread(target=self.collect_cars, args=())
        thread.daemon = True
        thread.start()
        return "resumed"

    def stop(self):
        self.busy = False
        # for i in self.browsers:
        #     i.kill()
        # return "paused"


