from pyfiglet import Figlet

from src.main.mapping.Mappers import mappers
from src.main.market.Market import Market
from src.main.market.crawling.Routers import routes

custom_fig = Figlet()
print(custom_fig.renderText('DataPumper'))


market = Market(name='donedeal',
                router=routes['donedeal_router'],
                mapper=mappers['donedeal_mapper'])

# if __name__ == '__main__':
#     with TerminateProtected(market):
#         market.webCrawler.driver.get(market.home)
#         market.start_parrallel(int(os.getenv('THREADS', 5)))

market.makeWorkers(2)
