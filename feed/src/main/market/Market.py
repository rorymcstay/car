import logging as log
import os
import sys
import traceback
from time import time
from typing import List

import bs4
import numpy
from kafka import KafkaProducer
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from settings import markets, kafka_params
from src.main.car.Domain import make_id
from src.main.market.Worker import Worker
from src.main.market.browser.Browser import Browser
from src.main.market.crawling.Exceptions import ExcludedResultNotifier, EndOfQueueNotification, ResultCollectionFailure
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.persistence.Persistence import Persistence
from src.main.market.utils.IgnoredExceptions import IgnoredExceptions
from src.main.market.utils.MongoServiceConstants import MongoServiceConstants
from src.main.market.utils.WebCrawlerConstants import WebCrawlerConstants
from src.main.service.mongo_service.MongoService import MongoService
from src.main.utils.LogGenerator import LogGenerator, write_log
from src.main.utils.Singleton import Singleton

LOG = LogGenerator(log, name='market')

@Singleton
class Market:

    workers: List[Worker]

    def __init__(self, name, mapper, router):
        self.params = markets[name]
        self.browsers = []
        self.workers = []
        self.results = None
        self.results_batched = None
        self.name = name
        self.mapper = mapper
        self.router = router
        self.home = self.router(make=os.getenv('CAR_MAKE', None),
                                model=os.getenv('CAR_MODEL', None),
                                sort=self.params['sortString'])
        self.mongoConstants = MongoServiceConstants()
        self.mongoService = MongoService('{mongo_host}:{mongo_port}'.format(**self.params))
        self.busy = False

        self.browser = Browser(name=name, port=self.params['browser_port'])
        self.webCrawler = WebCrawler(self.name, self.params['browser_port'])

        self.persistence = Persistence(self)
        self.goHome()
        self.kafkaProducer = KafkaProducer(**kafka_params)
        self.__instance = self

    def specifyMakeModel(self, make, model):
        """
        Changes the focus of the market.

        :param make: The make of car
        :param model: The model of car
        :return:
        """
        self.home = self.router(make, model, sort=self.params['sortString'])
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
                    result = self.webCrawler.get_queue_member(i, self.params['result_exclude'])
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
                        element_present = EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.params['result_css']))
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

    def publishListOfResults(self):
        parser = bs4.BeautifulSoup(self.webCrawler.driver.page_source)
        results = parser.findAll(self.params['result_stream'])
        i = 0
        for result in results:
            self.kafkaProducer.send(topic="{}_results".format(self.name), value=str(result), key="{}_{}".format(self.webCrawler.driver.current_url, i), headers={"type": "result"})
            i=+1
        write_log(LOG.info, msg="published to kafka", results=i)

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
        self.workers = [Worker(i, self) for i in range(min(max_containers, len(latest_results)))]

    def start_parrallel(self, max_containers):
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

    def addWorker(self):
        """
        increase the number of workers by one

        :return:
        """
        numWorker = len(self.workers)
        worker = Worker(numWorker + 1, self.name)
        self.workers.append(worker)
        return self.workers[-1].health_check()


    def removeWorker(self):
        del self.workers[0]


