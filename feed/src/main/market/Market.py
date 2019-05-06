import logging as log
from time import time
from typing import List

import bs4
import requests as r
from kafka import KafkaProducer

from settings import kafka_params, routing_params, market_params
from src.main.car.Domain import make_id
from src.main.market.Worker import Worker
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.persistence.Persistence import Persistence
from src.main.utils.LogGenerator import LogGenerator, write_log

LOG = LogGenerator(log, name='market')


class Market:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Market, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    workers: List[Worker] = []
    make = None
    model = None
    sort = None

    results = None
    results_batched = None
    busy = False
    browsers = []

    kafkaProducer = KafkaProducer(**kafka_params)

    def __init__(self):
        self.webCrawler = WebCrawler()

    def goHome(self):
        """
        navigate back to the base url
        :return:
        """

        routingEndpoint = "http://{host}:{port}/{api_prefix}/getBaseUrl/{name}/{make}/{model}/{sort}".format(make=self.make,
                                                                                                             model=self.model,
                                                                                                             sort=self.sort,
                                                                                                             **routing_params, **market_params)
        request = r.get(routingEndpoint)
        self.webCrawler.driver.get(request.text)
        return routingEndpoint

    def setHome(self, make=None, model=None, sort=None):
        self.make = make
        self.model = model
        self.sort = sort
        return self.goHome()

    def publishListOfResults(self):
        parser = bs4.BeautifulSoup(self.webCrawler.driver.page_source, features="html.parser")
        results = parser.findAll(attrs={"class": market_params['result_stream'].get("class")})
        i = 0
        for result in results:
            data = dict(value=bytes(str(result), 'utf-8'),
                        key=bytes("{}_{}".format(self.webCrawler.driver.current_url, i), 'utf-8'))
            self.kafkaProducer.send(topic="{name}-results".format(**market_params), **data)
            i += 1
        write_log(LOG.info, msg="published to kafka", results=i)

    def getResults(self):
        """
        get cars from current page of results

        :return:  a list of cars
        """
        # TODO externalise the delegation of results to nanny service
        out = []
        threadStart = time()
        write_log(LOG.debug, msg="workers have started")
        all_results = self.webCrawler.getResultList()
        self.results = all_results
        batches = [all_results[i::len(self.workers)] for i in range(len(self.workers))]
        for (w, b) in zip(self.workers, batches):
            w.prepareBatch(b, out)
        self.webCrawler.nextPage()

        write_log(LOG.info, msg="starting_threads")
        for t in self.workers:
            t.thread.start()
        for t in self.workers:
            t.thread.join()

        write_log(LOG.debug, msg="all_threads_returned", time=time() - threadStart)
        return out

    def makeWorkers(self, max_containers):
        """
        initiate workers and their containers.
        TODO Add a part which checks for containers which have same name and handle accordingly
        :param max_containers: The maximum number of containers to start
        :return: Updates the workers list
        """
        self.workers = [Worker() for i in range(max_containers)]

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
            batches = [results[i::max_containers] for i in range(max_containers)]
            write_log(LOG.info, msg="preparing_new_batch", page_number=str(page), size=len(results))
            for (w, b) in zip(self.workers, batches):
                w.prepareBatch(b)
            self.webCrawler.nextPage()
            r.put("http://{host}:{port}/{api_prefix}/updateHistory/{name}".format(name=market_params["name"], **routing_params),
                  data=self.webCrawler.driver.current_url)
            write_log(LOG.info, msg="starting_threads")
            for t in self.workers:
                t.thread.start()
            for t in self.workers:
                t.thread.join()

            page += 1
            write_log(LOG.info, msg='threads_finished', time=time() - threadStart)

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

    def verifyBatch(self, result):
        """
        Check that members of the current queue have not been persisted to the database.
        :param result:
        :return:
        """
        id = make_id(result)
        x = self.mongoService.cars.find_one(dict(_id=id))
        if x is None:
            y = self.mongoService.db['{name}_rawCar'.format(**market_params)].find_one(dict(_id=id))
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
        worker = Worker()
        self.workers.append(worker)
        return self.workers[-1].healthCheck()

    def removeWorker(self):
        del self.workers[0]
