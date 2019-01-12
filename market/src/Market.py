import threading
import logging as LOG
from car.market.src.crawling.WebCrawler import WebCrawler
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
            self.crawler.load_queue()
            LOG.debug("Queue length %s", self.crawler)
            for i in range(len(self.crawler.queue)):
                try:
                    self.crawler.load_queue()
                    if self.crawler.queue == 0:
                        self.crawler.driver.forward()
                        self.crawler.load_queue()
                    result = self.crawler.queue[i]
                except IndexError:
                    LOG.error("Couldn't load queue properly")
                    self.crawler.driver.forward()
                    try:
                        self.crawler.load_queue()
                        result = self.crawler.queue[i]
                    except:
                        self.crawler.return_to_last_page()
                        self.crawler.load_queue()
                rawCars = False
                # Check if any of exclusion items are contained within the next attempt
                if all(exclude not in result.text for exclude in self.result_exclude):
                    rawCars = self.crawler.get_result(result, 120)
                if rawCars is not False:
                    LOG.debug('Got raw car from %s', self.crawler.driver.current_url)
                    for rawCar in rawCars:
                        try:
                            car = self.mapper(rawCar)
                            LOG.debug('Saving result from %s', self.crawler.driver.current_url)
                            self.service.insert(car)
                            # TODO handle fails when saving to the database in MongoService
                            LOG.info('Saved result from %s', self.crawler.driver.current_url)
                            return
                        except Exception, e:
                            # TODO move error handling to respective services
                            LOG.warn('failed result from %s \n %s', self.crawler.driver.current_url, e.message)
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