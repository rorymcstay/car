import threading
import logging as LOG
from car.market.src.crawling.WebCrawler import WebCrawler
from car.market.src.mongo_service.MongoService import MongoService


class Market:

    LOG = LOG.getLogger('WebCrawler')

    def __init__(self, name, result_css, result_exclude, wait_for_car, json_identifier, next_page_xpath, mapper, router, remote=None):

        self.name = name

        self.next_page_xpath = next_page_xpath
        self.result_css = result_css
        self.result_exclude = result_exclude
        self.wait_for_car = wait_for_car
        self.json_identifier = json_identifier

        self.crawler = WebCrawler(self, remote)
        self.mapper = mapper
        self.home = router

        self.service = MongoService()
        self.busy = False

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
            self.crawler.load_queue()
            for i in range(len(self.crawler.queue)):
                self.crawler.load_queue()
                result = self.crawler.queue[i]
                rawCars = False
                # Check if any of exclusion items are contained within the next attempt
                if all(exclude not in result.text for exclude in self.result_exclude):
                    rawCars = self.crawler.get_result(result, 120)
                if rawCars is not False:
                    for rawCar in rawCars:
                        try:
                            car = self.mapper(rawCar)
                            self.service.insert(car)
                            return
                        except:
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