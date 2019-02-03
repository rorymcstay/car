import logging
import os

from src.main.market.Market import Market
from src.main.market.crawling.Routers import routes
from src.main.market.mapping.Mappers import mappers
from src.main.market.browser.Browser import Browser
os.environ["MAX_CLICK_ATTEMPTS"] = "5"
os.environ["MAX_GET_RESULT_ATTEMPT"] = "5"
os.environ["CLICK_TIMEOUT"] = "3"
os.environ["RETURN_TIMEOUT"] = "3"
os.environ["BROWSER_IMAGE"] = "selenium/node-chrome:latest"
os.environ["DRIVER_PORT"] = "4444"
os.environ["APP_NAME"] = "car_app"
os.environ["HUB_HOST"] = "0.0.0.0"
os.environ["HUB_PORT"] = "4444"
os.environ["SERVICE_HOST"] = "localhost"
os.environ["SERVICE_PORT"] = "5001"
os.environ["APP_PORT"] = "5000"
os.environ["APP_HOST"] = '0.0.0.0'
os.environ["MONGO_URL"] = "0.0.0.0:27017"
os.environ["MONGO_COLLECTION"] = "cars"
os.environ["MONGO_DATABASE"] = "mydatabase"
os.environ["USERNAME"] = "root"
os.environ["PASSWORD"] = "root"
os.environ["WORKER_TIMEOUT"] = '1'
hub = '/Users/rorymcstay/IdeaProjects/Car/car/car_app/src/main/market/browser/.hub'
browser = '/Users/rorymcstay/IdeaProjects/Car/car/car_app/src/main/market/browser/.browser'

APP_PORT = 5000
APP_HOST = '0.0.0.0'

logging.basicConfig(level=logging.INFO)

market = Market(name='donedeal',
                result_css=".card__body",
                result_exclude="Compare, compare, insurance, Insurance".split(','),
                wait_for_car=".cad-header",
                json_identifier="window.adDetails",
                next_page_xpath="//*[@id]",
                # next_page_xpath='/html/body/main/div[1]/div/div[2]/paging/nav/button[12]/span',
                router=routes['_donedeal_router'](make=None,
                                                  model=None,
                                                  sort="publishdate%20desc"),
                mapper=mappers['_donedeal_mapper'],
                next_button_text="Next",
                result_stub='https://www.donedeal.co.uk/cars-for-sale/',
                remote='http://127.0.0.1:5444/wd/hub')
market.crawler.retrace_steps(5)
market.start_parrallel(4)
#
