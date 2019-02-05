import os

from resources.TestConstants import TestConstants
from src.main.market.Market import Market
from src.main.market.mapping.Mappers import mappers
from src.main.market.crawling.Routers import routes

os.environ["MAX_CLICK_ATTEMPTS"] = "5"
os.environ["MAX_GET_RESULT_ATTEMPT"] = "5"
os.environ["RETURN_TIMEOUT"] = "3"
os.environ["BROWSER_IMAGE"] = "selenium/node-chrome:latest"
os.environ["DRIVER_PORT"] = "4444"
os.environ["HUB"] = "/Users/rorymcstay/IdeaProjects/Car/car/service/src/browser/.hub"
os.environ["BROWSER"] = "/Users/rorymcstay/IdeaProjects/Car/car/service/src/browser/.browser"
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
os.environ["PASSWORD"] = "20"

market = Market(name='test_donedeal',
                result_css=".card__body",
                result_exclude="Compare, compare, insurance, Insurance".split(','),
                wait_for_car=".cad-header",
                json_identifier="window.adDetails",
                next_page_xpath="//*[@id=\"pageBtn11\"]",
                router=routes['_donedeal_router'](make=None,
                                                  model=None,
                                                  sort="publishdate%20desc"),
                mapper=mappers['_donedeal_mapper'],
                next_button_text="Next",
                result_stub='https://www.donedeal.co.uk/cars-for-sale/',
                remote='http://{}:{}/wd/hub'.format(TestConstants().browser_host,
                                                    TestConstants().browser_port))

next_page_expectation = [
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc&start=28",
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc&start=56",
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc&start=84"
]
