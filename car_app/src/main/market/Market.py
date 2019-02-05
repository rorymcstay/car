import numpy
import threading
from time import time
from selenium.common.exceptions import NoSuchElementException
from src.main.market.persistence.Persistence import Persistence
from src.main.market.utils.BrowserConstants import BrowserConstants
from src.main.market.Worker import Worker
from src.main.market.browser.Browser import Browser
from src.main.market.utils.IgnoredExceptions import IgnoredExceptions
from src.main.market.crawling.WebCrawler import WebCrawler
from src.main.market.crawling.Exceptions import ExcludedResultNotifier, EndOfQueueNotification, ResultCollectionFailure
from src.main.service.mongo_service.MongoService import MongoService
from src.main.utils.LogGenerator import create_log_handler

LOG = create_log_handler('market')


class Market:

    def __init__(self, name,
                 result_css,
                 result_exclude,
                 wait_for_car,
                 json_identifier,
                 next_page_xpath, result_stub, mapper, router, next_button_text, remote=False):
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

        self.service = MongoService()
        self.busy = False

        if remote is False:
            self.webCrawler = WebCrawler(self)
            return
        # starting dedicated browser container
        self.browser = Browser(self.name + '-main', 1000)
        self.webCrawler = WebCrawler(self, 'http://{}:5444/wd/hub'.format(BrowserConstants().host))

        self.persistence = Persistence(self)
        self.persistence.save_market_details()

    def collect_cars(self, single=None):
        """
        Routine for collecting cars. Runs whilst self.market.busy is true. It handles exceptions defined in
        crawling.Exceptions. It uses MongoService to  persist cars to the mongo database in a docker container.
        """
        x = 0
        while self.busy:
            LOG.info("Page:%s", str(x))
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
                    self.webCrawler.latest_page()
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
        start = time()
        while self.busy:
            LOG.info("Processing page %s", page)
            results = self.webCrawler.get_result_array()
            batches = numpy.array_split(results, min(max_containers, len(results)))
            LOG.debug("Thread-Main: n_results: %s |page: %s", len(results), page)
            self.garbage_collection()
            for (w, b) in zip(self.workers, batches):
                w.prepare_batch(b)
            self.webCrawler.next_page()
            [t.thread.start() for t in self.workers]
            [t.thread.join() for t in self.workers]
            LOG.info("All threads have returned")
            self.webCrawler.update_latest_page(1)
            page += 1
            LOG.info("Cars Collected: %s \n"
                     "Page Number: %s \n"
                     "Running for: %s", str(self.get_cars_collected()), str(page), str(time() - start))
            self.persistence.save_progress()

    def get_cars_collected(self):
        """ returns the number of cars collected """
        return sum([w.cars_collected for w in self.workers])

    def garbage_collection(self):
        """
        does a health check and restarts those with exceptions
        :return:
        """
        for worker in self.workers:
            worker.health_check()
            if worker.health.exception == 'None':
                pass
            elif any(isinstance(ignore, type(worker.health.exception)) for ignore in IgnoredExceptions().ignore):
                pass
            else:
                LOG.warning("Doing garbage collection on thread: {}".format(self.name))
                worker.clean_up()
                worker.regenerate()
