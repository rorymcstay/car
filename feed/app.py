import logging
import os
import signal
import traceback
from time import time, sleep

import requests
from flask import Flask
from selenium.common.exceptions import WebDriverException

from settings import nanny_params
from src.main.market.Market import Market

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.FileHandler('/var/tmp/myapp.log')

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True

market: Market = Market()
market.setHome(make="BMW", model="3-Series", sort="newest")
if __name__ == '__main__':
    killer = GracefulKiller()
    while True:
        timeStart = time()
        try:
            market.publishListOfResults()
            market.webCrawler.nextPage()
        except WebDriverException as e:
            logging.warning("webdriver error, renewing webcrawler")
            market.renewWebCrawler()
        except TypeError as e:
            traceback.print_exc()
            logging.warning("type error - {}".format(e.args[0]))
            market.webCrawler.driver.refresh()
        logging.info(msg="published page to kafka results in {}".format(time() - timeStart))
        sleep(1)
        if killer.kill_now:
            market.webCrawler.driver.close()
            requests.get("https://{host}:{port}/{api_prefix}/freeContainer/{free_port}".format(free_port=market.webCrawler.port,
                                                                                               **nanny_params))

app = Flask(__name__)

if __name__ == '__main__':
    print(app.url_map)
    app.run(port=os.getenv("MANAGER_PORT", 5000))
