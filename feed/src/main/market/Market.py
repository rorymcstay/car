import logging as log

import bs4
import numpy
import requests as r
from kafka import KafkaProducer
from time import time
from typing import List

from settings import kafka_params, routing_params, mongo_params, market
from src.main.car.Domain import make_id
from src.main.market.Worker import Worker
from src.main.market.browser.Browser import Browser
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.persistence.Persistence import Persistence
from src.main.market.utils.IgnoredExceptions import IgnoredExceptions
from src.main.service.mongo_service.MongoService import MongoService
from src.main.utils.LogGenerator import LogGenerator, write_log
from src.main.utils.Singleton import Singleton

LOG = LogGenerator(log, name='market')

@Singleton
class Market:

    workers: List[Worker] = []
    make = None
    model = None
    sort = None

    results = None
    results_batched = None
    busy = False
    browsers = []

    kafkaProducer = KafkaProducer(**kafka_params)
    mongoService = MongoService('{host}:{port}'.format(**mongo_params))

    def __init__(self):
        self.browser = Browser()
        self.webCrawler = WebCrawler()
        self.goHome()

    def goHome(self):
        """
        navigate back to the base url
        :return:
        """
        routingEndpoint = "http://{host}:{port}/getBaseUrl/{name}/{make}/{model}/{sort}".format(make=self.make,
                                                                                                model=self.model,
                                                                                                sort=self.sort,
                                                                                                **routing_params)
        request = r.get(routingEndpoint)
        self.webCrawler.driver.get(request.text)

    def setHome(self, make=None, model=None, sort=None):
        self.make = make
        self.model = model
        self.sort = sort

    def publishListOfResults(self):
        parser = bs4.BeautifulSoup(self.webCrawler.driver.page_source)
        results = parser.findAll(attrs={"class": market['result_stream'].get("class")})
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
        all_results = self.webCrawler.getResultList()
        results = [x for x in [self.verifyBatch(result) for result in all_results] if x is not None]
        self.results=results
        batches = numpy.array_split(results, len(self.workers))
        for (w, b) in zip(self.workers, batches):
            w.prepareBatch(b, out)
        self.webCrawler.nextPage()

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
        self.workers = [Worker(i, self) for i in range(max_containers)]

    def startParallel(self, max_containers):
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
        while self.busy:
            threadStart = time()
            write_log(LOG.debug, msg="workers have started", page=page)
            all_results = self.webCrawler.getResultList()
            results = [x for x in [self.verifyBatch(result) for result in all_results] if x is not None]
            self.results = results
            batches = numpy.array_split(results, min(max_containers, len(results)))
            write_log(LOG.info, msg="preparing_new_batch", page_number=str(page), size=len(results))
            for (w, b) in zip(self.workers, batches):
                w.prepareBatch(b)
            self.webCrawler.nextPage()
            r.put("http://{host}:{port}/updateHistory/{name}".format(name=market["name"], **routing_params), data=self.webCrawler.driver.current_url)
            write_log(LOG.info, msg="starting_threads")
            for t in self.workers:
                t.thread.start()
            for t in self.workers:
                t.thread.join()

            page += 1
            write_log(LOG.info, msg='threads_finished', time=time()-threadStart)

    def tearDownWorkers(self):
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

    def garbageCollection(self):
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
                worker.cleanUp()
                worker.regenerate()

    def verifyBatch(self, result):
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
        return self.workers[-1].healthCheck()


    def removeWorker(self):
        del self.workers[0]


