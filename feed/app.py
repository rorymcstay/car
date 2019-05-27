import logging
import os
import signal
import traceback
from time import time, sleep

import requests
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from settings import nanny_params, feed_params, routing_params
from src.main.exceptions import NextPageException
from src.main.manager import FeedManager
from src.main.market.utils.WebCrawlerConstants import WebCrawlerConstants

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.FileHandler('/var/tmp/myapp.log')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("kafka").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


market: FeedManager = FeedManager()
market.setHome(make="BMW", model="3-Series", sort="newest")
if __name__ == '__main__':
    killer = GracefulKiller()
    while True:
        timeStart = time()
        try:
            market.publishListOfResults()
            try:
                market.webCrawler.nextPage()
            except NextPageException as e:
                nextPage = "http://{host}:{port}/{api_prefix}/getResultPageUrl/{name}".format(**routing_params,
                                                                                              **feed_params)
                nextPage = requests.get(nextPage, json=dict(make=market.make,
                                                            model=market.model,
                                                            sort=market.sort,
                                                            page=market.webCrawler.page))

                market.webCrawler.driver.get(nextPage.text)
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, feed_params['wait_for']))
                WebDriverWait(market.webCrawler.driver, WebCrawlerConstants().click_timeout).until(element_present)
        except WebDriverException as e:
            logging.warning("webdriver error, renewing webcrawler")
            traceback.print_exc()
            market.renewWebCrawler()
        except TypeError as e:
            traceback.print_exc()
            logging.warning("type error - {}".format(e.args[0]))
            market.webCrawler.driver.refresh()
        logging.info(msg="published page to kafka results in {}".format(time() - timeStart))
        sleep(1)
        if killer.kill_now:
            market.webCrawler.driver.close()
            requests.get(
                "https://{host}:{port}/{api_prefix}/freeContainer/{free_port}".format(free_port=market.webCrawler.port,
                                                                                      **nanny_params))
