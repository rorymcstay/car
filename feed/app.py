import logging
import os
import signal
from time import time, sleep

import requests
from flask import Flask
from pyfiglet import Figlet
from selenium.common.exceptions import WebDriverException

from settings import feed_params, nanny_params
from src.main.market.Market import Market
from src.main.service.rest.Command import Command

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
market.setHome(make="Porsche", model="Cayenne", sort="newest")
if __name__ == '__main__':
    killer = GracefulKiller()
    custom_fig = Figlet()
    print(custom_fig.renderText('{name}-feed'.format(**feed_params)))
    while True:
        timeStart = time()
        try:
            market.publishListOfResults()
            market.webCrawler.nextPage()
        except WebDriverException as e:
            logging.warning("webdriver error, renewing webcrawler")
            market.renewWebCrawler()

        logging.info(msg="published page to kafka results in {}".format(time() - timeStart))
        sleep(1)
        if killer.kill_now:
            market.webCrawler.driver.close()
            requests.get("https://{host}:{port}/{api_prefix}/freeContainer/{free_port}".format(free_port=market.webCrawler.port,
                                                                                               **nanny_params))

app = Flask(__name__)
Command.register(app)

if __name__ == '__main__':
    print(app.url_map)
    app.run(port=os.getenv("MANAGER_PORT", 5000))
