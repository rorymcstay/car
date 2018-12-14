from flask import request
from flask_classy import FlaskView, route

from car.market.src.crawling.WebCrawler import WebCrawler
from car.market.src.mapping.DoneDeal import DoneDeal

from car.market.src.Market import Market
from car.market.src.mongo_service.MongoService import MongoService

service = MongoService()
DoneDealCrawler = WebCrawler(Done)
markets = {}
mappings = {'DoneDeal': DoneDeal}
webcrawlers = {'DoneDeal': DoneDealCrawler}

class Command(FlaskView):

    def hello(self):
        return 'hello'

    @route('/add_market/<string:name>', methods=['PUT'])
    def make_market(self, name):
        market_definition = request.get_json()
        service.save_market_details(market_definition)
        markets[name] = Market(name=name,
                               wait_for_car=str(market_definition['wait_for_car']),
                               result_body_class=str(market_definition['result_body_class']),
                               mapping=mappings[str(market_definition['mapping'])],
                               json_identifier=str(market_definition['json_identifier']),
                               next_page_css=str(market_definition['next_page_css']),
                               webcrawler=webcrawlers[str(market_definition['webcrawler'])])
        return 'ok'

    @route('markets', methods=['GET'])
    def get_markets(self):
        return

    @route('/initialise/<string:name>/<int:pages>', methods=['PUT'])
    def initialise(self, pages, name):
        markets[str(name)].initialise(pages, service)
        return 'done'
