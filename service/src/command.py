from flask import request, Blueprint, Flask
from json import dumps as to_json
from flask_classy import FlaskView
from flask_classy import route

from car.market.src.market import market
from car.market.src.persisting.mongoservice import MongoService

service = MongoService()
markets = {}


class Command(FlaskView):

    def hello(self):
        return 'hello'

    @route('/add_market/<string:name>', methods=['PUT'])
    def make_market(self, name):
        market_definition = request.get_json()
        service.save_market_details(market_definition)
        markets[name] = market(name=name,
                               url_stub_1=market_definition.url_stub_1,
                               url_stub_2=market_definition.url_stub_2,
                               result_stub=market_definition.result_stub,
                               wait_for=market_definition.wait_for,
                               wait_for_car=market_definition.wait_for,
                               n_page=market_definition.n_page,
                               json_identifier=market_definition.json_identifier,
                               mapping=market_definition.mapping)
        return to_json(market_definition)

    @route('markets', methods=['GET'])
    def get_markets(self):
        return

    @route('/initialise/<string:name>/<int:pages>', methods=['PUT'])
    def initialise(self, pages, name):
        markets[name].initialise(pages, service)
        return 'done'
