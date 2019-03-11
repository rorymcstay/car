import os

from pyfiglet import Figlet

from src.main.car.Domain import MarketDetails
from src.main.market.Market import Market
from src.main.market.crawling.Routers import routes
from src.main.market.mapping.Mappers import mappers
from src.main.utils.TerminateProtected import TerminateProtected

custom_fig = Figlet(font='graffiti')
print(custom_fig.renderText('DoneDealPumper'))

marketDetails = MarketDetails(name='donedeal',
              result_css=".card__body",
              result_exclude="Compare, compare, insurance, Insurance".split(','),
              wait_for_car=".cad-header",
              json_identifier="window.adDetails",
              next_page_xpath="//*[@id]",
              result_stub='https://www.donedeal.co.uk/cars-for-sale/',
              next_button_text="Next")

market = Market(marketDetails=marketDetails,
                router=routes['_donedeal_router'](make=os.getenv('CAR_MAKE', None),
                                                  model=os.getenv('CAR_MODEL', None),
                                                  sort="publishdate%20desc"),
                mapper=mappers['_donedeal_mapper'],
                remote='http://{}:{}/wd/hub'.format(os.getenv('BROWSER_CONTAINER_HOST', 'localhost'),
                                                    os.getenv('BROWSER_BASE_PORT'), 4444),
                mongo_port=int(os.getenv('MONGO_PORT', 27017)),
                browser_port=int(os.getenv('BROWSER_BASE_PORT', 4444)))

if __name__ == '__main__':
    with TerminateProtected(market):
        market.webCrawler.driver.get(market.home)
        market.start_parrallel(int(os.getenv('THREADS', 5)))


