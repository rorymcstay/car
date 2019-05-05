from pyfiglet import Figlet

from src.main.market.Market import Market

custom_fig = Figlet()
print(custom_fig.renderText('DataPumper'))


market: Market = Market.instance()

if __name__ == '__main__':
    while True:
        market.publishListOfResults()
        market.webCrawler.nextPage()

