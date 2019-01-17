import os
import threading
import logging as LOG
import traceback
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from car.src.market.crawling.WebCrawler import WebCrawler
from car.src.market.crawling.Exceptions import ExcludedResultNotifier, EndOfQueueNotification, ResultCollectionFailure
from car.src.service.mongo_service.MongoService import MongoService
import logging
from selenium.webdriver.support import expected_conditions as EC


class Market:

    def __init__(self, name,
                 result_css,
                 result_exclude,
                 wait_for_car,
                 json_identifier,
                 next_page_xpath, mapper, router, next_button_text, remote=False):
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



    def collect_cars(self):
        """
        Routine for collecting cars. Runs whilst self.market.busy is true. It handles exceptions defined in
        crawling.Exceptions. It uses MongoService to  persist cars to the mongo database in a docker container.
        """
        x = 0
        while self.busy:
            LOG.info("Page:%s", str(x))
            LOG.debug("Queue length %s", self.crawler)

            for i in self.crawler.get_queue_length(): # TODO Handle webdriver exceptions within this block
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

    def start(self):
        """
        Starts collect_cars routine by setting car busy to true. It starts it in a new thread.
        :return:
        """
        self.crawler.driver.get(self.home)
        self.crawler.latest_page = self.home
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
