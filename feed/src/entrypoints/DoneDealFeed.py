from pyfiglet import Figlet

from src.main.mapping.Mappers import mappers
from src.main.market.Market import Market
from src.main.market.crawling.Routers import routes

custom_fig = Figlet()
print(custom_fig.renderText('DataPumper'))

name = 'donedeal'
Market(name=name,
       router=routes['{}_router'.format(name)],
       mapper=mappers['{}_mapper'.format(name)])

market: Market = Market.instance()

if __name__ == '__main__':
    while True:
        market.publishListOfResults()
        market.webCrawler.next_page()

