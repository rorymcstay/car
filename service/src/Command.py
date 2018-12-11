from flask import request
from flask_classy import FlaskView, route
from car.market.src.mapping.DoneDeal import DoneDeal

from car.market.src.Market import Market
from car.market.src.mongo_service.MongoService import MongoService

service = MongoService()
markets = {}
mappings = {'DoneDeal': DoneDeal}

class Command(FlaskView):

    def hello(self):
        return 'hello'

    @route('/add_market/<string:name>', methods=['PUT'])
    def make_market(self, name):
        market_definition = request.get_json()
        service.save_market_details(market_definition)
        markets[name] = Market(name=name,
                               url_stub_1=str(market_definition['url_stub_1']),
                               url_stub_2=str(market_definition['url_stub_2']),
                               result_stub=str(market_definition['result_stub']),
                               wait_for=str(market_definition['wait_for']),
                               wait_for_car=str(market_definition['wait_for_car']),
                               n_page=str(market_definition['n_page']),
                               json_identifier=str(market_definition['json_identifier']),
                               mapping=mappings[str(market_definition['mapping'])],
                               browser=str(market_definition['browser']))
        return 'ok'

    @route('markets', methods=['GET'])
    def get_markets(self):
        return

    @route('/initialise/<string:name>/<int:pages>', methods=['PUT'])
    def initialise(self, pages, name):
        markets[str(name)].initialise(pages, service)
        return 'done'
