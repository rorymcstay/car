from flask import request, Blueprint, Flask
from json import dumps as to_json
from flask_classy import FlaskView
from flask_classy import route
from car.market.src.mapping.DoneDeal import DoneDeal

from car.market.src.market import market
from car.market.src.persisting.mongoservice import MongoService

service = MongoService()
markets = {}
mappings = {'DoneDeal': DoneDeal}

for market_definition in service.return_all_markets():
    markets[market_definition.name] = market(name=market_definition.name,
                                             url_stub_1=str(market_definition['url_stub_1']),
                                             url_stub_2=str(market_definition['url_stub_2']),
                                             result_stub=str(market_definition['result_stub']),
                                             wait_for=str(market_definition['wait_for']),
                                             wait_for_car=str(market_definition['wait_for_car']),
                                             n_page=str(market_definition['n_page']),
                                             json_identifier=str(market_definition['json_identifier']),
                                             mapping=mappings[str(market_definition['mapping'])],
                                             browser=str(market_definition['browser']))


class Command(FlaskView):

    def hello(self):
        return 'hello'

    @route('/add_market/<string:name>', methods=['PUT'])
    def make_market(self, name):
        market_definition = request.get_json()
        service.save_market_details(market_definition)
        for uni in market_definition:
            uni = str(uni)
        markets[name] = market(name=name,
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
