import logging
import os
import signal
import sys

from time import time, sleep

import requests
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from settings import nanny_params, feed_params, routing_params
from src.main.exceptions import NextPageException
from src.main.manager import FeedManager
from src.main.market.utils.WebCrawlerConstants import WebCrawlerConstants

start = logging.getLogger("startup")

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.FileHandler('/var/tmp/myapp.log')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("kafka").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("selenium").setLevel(logging.WARNING)


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


market: FeedManager = FeedManager()
market.setHome()
if __name__ == '__main__':
    killer = GracefulKiller()
    start.warning("leader has started")
    while True:
        timeStart = time()
        try:
            market.publishListOfResults()
            try:
                market.webCrawler.nextPage()
            except (NextPageException, WebDriverException) as e:
                logging.warning("{} raised whilst going to next page - using router".format(e))
                nextPage = "http://{host}:{port}/{api_prefix}/getResultPageUrl/{name}".format(**routing_params,
                                                                                              **feed_params)
                nextPage = requests.get(nextPage, json=dict(make=market.make,
                                                            model=market.model,
                                                            sort=market.sort,
                                                            page=market.webCrawler.page))

                try:
                    market.webCrawler.driver.get(nextPage.text)
                except TimeoutException:
                    market.webCrawler.driver.get(nextPage.text)
                try:
                    element_present = EC.presence_of_element_located((By.CSS_SELECTOR, feed_params['wait_for']))
                    WebDriverWait(market.webCrawler.driver, WebCrawlerConstants().click_timeout).until(element_present)
                except TimeoutException:
                    logging.info("page did not load as expected - timeout exception")
        except TypeError as e:
            logging.warning("type error - {}".format(e.args[0]))
            market.webCrawler.driver.refresh()
        except TimeoutException as e:
            logging.info("Webdriver timed out")

        logging.info(msg="published page to kafka results in {}".format(time() - timeStart))
        requests.put("http://{host}:{port}/{api_prefix}/updateHistory/{name}".format(name=feed_params["name"],
                                                                                     **routing_params),
                     data=market.webCrawler.driver.current_url)

        sleep(5)
        # verify then wait until page ready
        if killer.kill_now:
            market.webCrawler.driver.close()
            requests.get(
                "http://{host}:{port}/{api_prefix}/freeContainer/{free_port}".format(free_port=market.webCrawler.port,
                                                                                      **nanny_params))
            sys.exit()
