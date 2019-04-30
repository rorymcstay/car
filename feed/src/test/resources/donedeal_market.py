import os

import docker.client
from resources.TestConstants import TestConstants

from src.main.mapping.Mappers import mappers
from src.main.market.Market import Market
from src.main.market.crawling.Routers import routes
from src.main.market.utils.BrowserConstants import get_open_port

mongo_port = get_open_port()
client=docker.client.from_env()
browser_port=get_open_port()
client.containers.run(TestConstants(mongo_port).mongo_image, detach=True,
                      name=TestConstants(mongo_port).mongo_name,
                      ports={'27017/tcp': mongo_port},
                      environment=['MONGO_INITDB_ROOT_USERNAME=root',
                                   'MONGO_INITDB_ROOT_PASSWORD=root'])
market = Market(name='test_donedeal',
                result_css=".card__body",
                result_exclude="Compare, compare, insurance, Insurance".split(','),
                wait_for_car=".cad-header",
                json_identifier="window.adDetails",
                next_page_xpath="//*[@id]",
                router=routes['_donedeal_router'](make=None,
                                                  model=None,
                                                  sort="publishdate%20desc"),
                mapper=mappers['_donedeal_mapper'],
                next_button_text="Next",
                result_stub='https://www.donedeal.co.uk/cars-for-sale/',
                remote='http://{}:{}/wd/hub'.format(os.getenv('BROWSER_CONTAINER_HOST', 'localhost'),
                                                    os.getenv('BROWSER_BASE_PORT'), browser_port),
                mongo_port=mongo_port,
                browser_port=browser_port, )

next_page_expectation = [
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc"
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc&start=28",
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc&start=56",
    "https://www.donedeal.co.uk/cars?sort=publishdate%20desc&start=84"
]
