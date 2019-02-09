from src.main.market.Market import Market
from src.main.market.crawling.Routers import routes
from src.main.market.mapping.Mappers import mappers

from pyfiglet import Figlet
custom_fig = Figlet(font='graffiti')
print(custom_fig.renderText('DoneDealPumper'))

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
                remote='http://34.214.147.39:4444/wd/hub', mongo_port=27017, browser_port=4444)

if __name__ == '__main__':
    market.webCrawler.driver.get(market.home)
    market.start_parrallel(5)
