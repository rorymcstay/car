import json

from flask import request
from flask_classy import FlaskView, route
from car.market.src.Market import Market
from car.market.src.mapping.Mappers import Mappers
from car.market.src.mongo_service.MongoService import MongoService
from car.market.src.crawling.Routers import Routers

service = MongoService()

markets = {}
routes = Routers()
mappers = Mappers()


class Command(FlaskView):

    @route('/add_market/<string:name>/<string:make>/<string:model>', methods=['PUT'])
    def make_market_specific(self, name, make, model):
        market_definition = request.get_json()
        service.save_market_details(json.loads(market_definition))
        markets[name] = Market(name=str(market_definition['name']),
                               result_css=str(market_definition['result_body_class']),
                               wait_for_car=str(market_definition['wait_for_car']),
                               json_identifier=str(market_definition['json_identifier']),
                               next_page_xpath=str(market_definition['next_page_css']),
                               mapper=mappers["_"+name+"_mapper"],
                               router=routes["_"+name+"_router"](make=make, model=model, sort=str(market_definition["sort"])),
                               remote=str(market_definition['remote']))
        return 'ok'

    @route('/add_market/<string:name>', methods=['PUT'])
    def make_market(self, name):
        market_definition = request.get_json()
        exclude = str(market_definition['result_exclude']).split(',')
        # service.save_market_details(json.loads(str(market_definition)))
        markets[name] = Market(name=name,
                               result_css=str(market_definition['result_css']),
                               result_exclude=exclude,
                               wait_for_car=str(market_definition['wait_for_car']),
                               json_identifier=str(market_definition['json_identifier']),
                               next_page_xpath=str(market_definition['next_page_xpath']),
                               mapper=mappers["_"+name+"_mapper"],
                               router=routes["_"+name+"_router"](make=None, model=None, sort=str(market_definition["sort"])),
                               remote=str(market_definition['remote']))
        return 'ok'

    @route('/start/<string:name>', methods=['PUT'])
    def start(self, name):
        market = markets[str(name)]
        market.start()
        return "started"

    @route('/resume/<string:name>', methods=['PUT'])
    def resume(self, name):
        market = markets[str(name)]
        market.resume()
        return "resumed"

    @route('/stop/<string:name>', methods=['PUT'])
    def stop(self, name):
        market = markets[str(name)]
        market.stop()
        return "stopeed"

