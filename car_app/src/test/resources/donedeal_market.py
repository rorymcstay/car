from market.utils.BrowserConstants import get_open_port
from resources.TestConstants import TestConstants
from src.main.market.Market import Market
from src.main.market.mapping.Mappers import mappers
from src.main.market.crawling.Routers import routes

import docker.client

client=docker.client.from_env()
client.containers.run(TestConstants().mongo_image, detach=True,
                      name='test_mongo',
                      ports={'27017/tcp' : TestConstants().mongo_port})

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
                remote=True, port=get_open_port())

next_page_expectation = [
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc"
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc&start=28",
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc&start=56",
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc&start=84"
]
