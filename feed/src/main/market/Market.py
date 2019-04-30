import logging as log
import os
import sys
import traceback
from time import time

import numpy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.main.car.Domain import make_id, MarketDetails
from src.main.mapping.ResultParser import ResultParser
from src.main.market.Worker import Worker
from src.main.market.browser.Browser import Browser
from src.main.market.crawling.Exceptions import ExcludedResultNotifier, EndOfQueueNotification, ResultCollectionFailure
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.persistence.Persistence import Persistence
from src.main.market.utils.BrowserConstants import BrowserConstants
from src.main.market.utils.IgnoredExceptions import IgnoredExceptions
from src.main.market.utils.MongoServiceConstants import MongoServiceConstants
from src.main.market.utils.WebCrawlerConstants import WebCrawlerConstants
from src.main.service.mongo_service.MongoService import MongoService
from src.main.utils.LogGenerator import LogGenerator, write_log

LOG = LogGenerator(log, name='market')


class Market:

    def __init__(self, marketDetails: MarketDetails,
                 mapper,
                 router, browser_port, mongo_port=os.getenv('MONGO_PORT', 27017), remote=True):
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
        # TODO extract fields into params
        """


        self.mongo_port = mongo_port
        self.port = browser_port
        self.browsers = []
        self.workers = []
        self.result_stub = marketDetails.result_stub
        self.results = None
        self.results_batched = None

        self.sortString=marketDetails.sort

        self.name = marketDetails.name
        self.next_button_text = marketDetails.next_button_text
        self.next_page_xpath = marketDetails.next_page_xpath
        self.result_css = marketDetails.result_css
        self.result_exclude = marketDetails.result_exclude
        self.wait_for_car = marketDetails.wait_for_car
        self.json_identifier = marketDetails.json_identifier

        self.mapper = mapper
        self.router = router
        self.resultParser = ResultParser(self.name)
        self.home = self.router(make=os.getenv('CAR_MAKE', None),
                                model=os.getenv('CAR_MODEL', None),
                                sort=self.sortString)

        self.mongoConstants = MongoServiceConstants()
        self.mongo_host = '{}:{}'.format(os.getenv('MONGO_HOST', '0.0.0.0'), self.mongo_port)
        self.mongoService = MongoService(self.mongo_host)
        self.busy = False

        if remote is False:
            self.webCrawler = WebCrawler(self)
            return
        # starting dedicated browser containercf
        self.browser = Browser(self.name, batch_number='main', port=self.port)
        self.browser_host='http://{}:{}/wd/hub'.format(BrowserConstants().host, self.port)
        self.webCrawler = WebCrawler(self, self.browser_host)

        self.persistence = Persistence(self, marketDetails)
        self.persistence.save_market_details()
        self.webCrawler.driver.get(self.home)

    def specifyMakeModel(self, make, model):
        """
        Changes the focus of the market.

        :param make: The make of car
        :param model: The model of car
        :return:
        """
        self.home = self.router(make, model, sort=self.sortString)
        self.webCrawler.driver.get(self.home)

    def goHome(self):
        """
        navigate back to the base url
        :return:
        """
        self.webCrawler.driver.get(self.home)

    def collect_cars(self, single=None):
        """
        Routine for brunt force collecting cars. Runs whilst self.market.busy is true. It handles exceptions defined in
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
                            self.mongoService.insert_or_update_car(car)
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

    def getListOfResults(self):
        results = self.resultParser.parseResults(self.webCrawler.driver.page_source)

        return results

    def selectResult(self, id):



    def getResults(self):
        """
        get cars from current page of results

        :return:  a list of cars
        """
        out = []
        threadStart=time()
        write_log(LOG.debug, msg="workers have started")
        all_results = self.webCrawler.get_result_array()
        results = [x for x in [self.verify_batch(result) for result in all_results] if x is not None]
        self.results=results
        batches = numpy.array_split(results, len(self.workers))
        for (w, b) in zip(self.workers, batches):
            w.prepare_batch(b, out)
        self.webCrawler.next_page()

        write_log(LOG.info, msg="starting_threads")
        for t in self.workers:
            t.thread.start()
        for t in self.workers:
            t.thread.join()

        write_log(LOG.debug, msg="all_threads_returned", time=time()-threadStart)
        return out

    def makeWorkers(self, max_containers):
        """
        initiate workers and their containers.
        TODO Add a part which checks for containers which have same name and handle accordingly
        :param max_containers: The maximum number of containers to start
        :return: Updates the workers list
        """
        latest_results = self.webCrawler.get_result_array()
        self.workers = [Worker(i, self, True) for i in range(min(max_containers, len(latest_results)))]

    def start_parrallel(self, max_containers, remote=True):
        """
        Start collecting cars with the workers
        :param max_containers:
        :param remote:
        :return:
        """
        self.busy = True
        Persistence(self).return_to_previous()
        self.makeWorkers(max_containers)
        page = 1
        try:
            total=0
            while self.busy:
                threadStart=time()
                write_log(LOG.debug, msg="workers have started", page=page)
                all_results = self.webCrawler.get_result_array()
                results = [x for x in [self.verify_batch(result) for result in all_results] if x is not None]
                self.results=results

                batches = numpy.array_split(results, min(max_containers, len(results)))
                write_log(LOG.info, msg="preparing_new_batch", page_number=str(page), size=len(results))
                for (w, b) in zip(self.workers, batches):
                    w.prepare_batch(b)
                self.webCrawler.next_page()

                write_log(LOG.info, msg="starting_threads")
                for t in self.workers:
                    t.thread.start()
                for t in self.workers:
                    t.thread.join()

                write_log(LOG.debug, msg="all_threads_returned")
                self.webCrawler.update_latest_page()
                page += 1
                this_batch = self.get_cars_collected() - total
                total = self.get_cars_collected()
                write_log(LOG.info, msg='threads_finished', collected=this_batch, total_collected=total, page=str(page),
                          time=time()-threadStart)
                self.persistence.save_progress()
        except KeyboardInterrupt:
            self.browser.quit()
            self.tear_down_workers()
            sys.exit(1)
        except Exception as e:
            self.browser.quit()
            traceback.print_exc()

    def tear_down_workers(self):
        """
        Stop resources allocated to the workers

        :return:
        """
        self.busy = False
        w: Worker
        for w in self.workers:
            write_log(LOG.info, "tearing down worker {}".format(w.batch_number))
            w.stop = True
        for w in self.workers:
            w.browser.quit()

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
            if worker.health.exception == 'None':
                pass
            elif any(isinstance(ignore, type(worker.health.exception)) for ignore in IgnoredExceptions().ignore):
                pass
            else:
                worker.clean_up()
                worker.regenerate()

    def verify_batch(self, result):
        """
        Check that members of the current queue have not been persisted to the database.
        :param result:
        :return:
        """
        id = make_id(result)
        x = self.mongoService.cars.find_one(dict(_id=id))
        if x is None:
            y = self.mongoService.db['{}_rawCar'.format(self.name)].find_one(dict(_id=id))
            if y is None:
                return result
            else:
                pass
        else:
            pass


