import logging
import os

from flask import Flask
from pyfiglet import Figlet

from settings import market, logging_params
from src.main.market.Market import Market
from src.main.service.rest.Command import Command

logging.basicConfig(level=logging_params[os.getenv("LOG_LEVEL")])
logging.FileHandler('/var/tmp/myapp.log')

custom_fig = Figlet()
print(custom_fig.renderText('{name}-Pumper'.format(**market)))


market: Market = Market()
market.setHome(make="Porsche", model="Cayenne", sort="newest")
if __name__ == '__main__':
    while True:
        market.publishListOfResults()
        market.webCrawler.nextPage()

app = Flask(__name__)
Command.register(app)

if __name__ == '__main__':
    print(app.url_map)
    app.run(port=os.getenv("MANAGER_PORT", 5000))
