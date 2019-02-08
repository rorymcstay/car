import os
import traceback

import numpy
import threading
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.main.market.utils.MongoServiceConstants import MongoServiceConstants
from src.main.market.utils.WebCrawlerConstants import WebCrawlerConstants
from src.main.market.persistence.Persistence import Persistence
from src.main.market.utils.BrowserConstants import BrowserConstants, get_open_port
from src.main.market.Worker import Worker
from src.main.market.browser.Browser import Browser
from src.main.market.utils.IgnoredExceptions import IgnoredExceptions
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.crawling.Exceptions import ExcludedResultNotifier, EndOfQueueNotification, ResultCollectionFailure
from src.main.service.mongo_service.MongoService import MongoService
from src.main.utils.LogGenerator import LogGenerator, write_log
import logging as log

LOG = LogGenerator(log, name='market')

class Market:

    def __init__(self, name,
                 result_css,
                 result_exclude,
                 wait_for_car,
                 json_identifier,
                 next_page_xpath, result_stub, mapper, router, next_button_text, browser_port, mongo_port=os.getenv('MONGO_PORT', 27017), remote=False):
        """
        Market object has control over a :class: Browser object and a :class: WebCrawler and Workers It also contains
        the specific details of the webpage source.

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
        self.mongo_port = mongo_port
        self.port = browser_port
        self.browsers = []
        self.workers = []
        self.result_stub = result_stub
        self.results = None
        self.results_batched = None
        self.name = name
        self.next_button_text = next_button_text
        self.next_page_xpath = next_page_xpath
        self.result_css = result_css
        self.result_exclude = result_exclude
        self.wait_for_car = wait_for_car
        self.json_identifier = json_identifier

        self.mapper = mapper
        self.home = router

        self.mongoConstants = MongoServiceConstants()
        self.mongo_host = '{}:{}'.format(os.getenv('MONGO_HOST', '0.0.0.0'), self.mongo_port)
        self.service = MongoService(self.mongo_host)
        self.busy = False

        if remote is False:
            self.webCrawler = WebCrawler(self)
            return
        # starting dedicated browser container
        self.browser = Browser(self.name, batch_number='main', port=self.port)
        self.browser_host='http://{}:{}/wd/hub'.format(BrowserConstants().host, self.port)
        self.webCrawler = WebCrawler(self, self.browser_host)

        self.persistence = Persistence(self)
        self.persistence.save_market_details()

    def collect_cars(self, single=None):
        """
        Routine for collecting cars. Runs whilst self.market.busy is true. It handles exceptions defined in
        crawling.Exceptions. It uses MongoService to  persist cars to the mongo database in a docker container.
        """
        x = 0
        while self.busy:
            write_log(LOG.info, msg='new_page', page=x)
            if single is None:
                queue = self.webCrawler.get_queue_range()
            else:
                queue = [single]
            for i in queue:  # TODO Handle webdriver exceptions within this block
                raw_cars = False
                try:
                    result = self.webCrawler.get_queue_member(i, self.result_exclude)
                    raw_cars = self.webCrawler.get_result(result)
                except ExcludedResultNotifier:
                    write_log(LOG.warning, thread='main', msg="skipped excluded result")
                    pass
                except EndOfQueueNotification:
                    write_log(LOG.warning, thread='main', msg="end of Queue")
                    break
                except ResultCollectionFailure:
                    write_log(LOG.warning, thread='main', msg="result collection error")
                    pass
                except NoSuchElementException:
                    write_log(LOG.warning, thread='main', msg="could not find car")
                    self.webCrawler.latest_page()
                    pass
                    try:
                        self.webCrawler.driver.get(self.webCrawler.last_result)
                        element_present = EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.result_css))
                        WebDriverWait(self.webCrawler.driver, WebCrawlerConstants().click_timeout).until(element_present)
                    except TimeoutException:
                        write_log(LOG.warning, msg='timeout_exception')
                if raw_cars is not False:
                    write_log(LOG.debug, msg='raw_car', url=self.webCrawler.driver.current_url)
                    for rawCar in raw_cars['result']:
                        try:
                            car = self.mapper(rawCar, raw_cars['url'])
                            write_log(LOG.debug, msg='saving_result', url=self.webCrawler.driver.current_url)
                            self.service.insert(car)
                            # TODO handle fails when saving to the database in MongoService
                            write_log(LOG.debug, msg='saved_result', url=self.webCrawler.driver.current_url)
                        except Exception as e:
                            write_log(LOG.warning, msg='failed_result', url=self.webCrawler.driver.current_url, exception=e.args[0])
                            traceback.print_exc()
                            pass
            go_next = self.webCrawler.next_page()
            if not go_next:
                self.webCrawler.retrace_steps(x)
            x = x + 1

    def start_single(self):
        """
        Starts collect_cars routine by setting car busy to true. It starts it in a new thread.
        :return:
        """
        self.webCrawler.latest_page = self.home
        self.busy = True
        thread = threading.Thread(target=self.collect_cars, args=())
        thread.start()
        return "started"

    def start_parrallel(self, max_containers, remote=True):
        self.busy = True
        Persistence(self).return_to_previous()
        latest_results = self.webCrawler.get_result_array()
        self.workers = [Worker(i, self, remote) for i in range(min(max_containers, len(latest_results)))]
        page = 1
        while self.busy:
            write_log(LOG.debug, msg="workers have started", page=page)
            results = self.webCrawler.get_result_array()
            batches = numpy.array_split(results, min(max_containers, len(results)))
            write_log(LOG.info, msg="preparing_new_batch", page_number=str(page), page_size=len(results))
            for (w, b) in zip(self.workers, batches):
                w.prepare_batch(b)
            self.webCrawler.next_page()

            write_log(LOG.info, msg="starting_threads")
            [t.thread.start() for t in self.workers]
            [t.thread.join() for t in self.workers]

            write_log(LOG.debug, msg="all_threads_returned")
            self.webCrawler.update_latest_page()
            page += 1
            write_log(LOG.info, msg='threads_finished', collected=self.get_cars_collected(), page=str(page))
            self.persistence.save_progress()
            self.garbage_collection()

    def get_cars_collected(self):
        """ returns the number of cars collected """
        return sum([w.cars_collected for w in self.workers])

    def garbage_collection(self):
        """
        does a health check and restarts those with exceptions
        :return:
        """
        write_log(log=LOG.debug, msg='starting_garbage_collection')
        for worker in self.workers:
            worker.health_check()
            if worker.health.exception == 'None':
                pass
            elif any(isinstance(ignore, type(worker.health.exception)) for ignore in IgnoredExceptions().ignore):
                pass
            else:
                worker.clean_up()
                worker.regenerate()
