import json
from flask import request
from flask_classy import FlaskView, route
from src.main.market.Market import Market
from src.main.service.mongo_service.MongoService import service
from src.main.market.crawling.Routers import routes
from src.main.market.mapping.Mappers import mappers

markets = {}


class Command(FlaskView):

    @route('/add_market/<string:name>/<int:remote>/<string:make>/<string:model>', methods=['PUT'])
    def make_market_specific(self, name, make, model):
        if name in markets.keys():
            return "Market name is taken"
        market_definition = request.get_json()
        exclude = str(market_definition['result_exclude']).split(',')
        service.save_market_details(json.loads(market_definition))
        remote = {}
        remote.url = str(market_definition['remote'])
        markets[name] = Market(name=name,
                               result_css=market_definition['result_body_class'],
                               result_exclude=exclude,
                               wait_for_car=market_definition['wait_for_car'],
                               json_identifier=market_definition['json_identifier'],
                               next_page_xpath=market_definition['next_page_xpath'],
                               mapper=mappers["_" + name + "_mapper"],
                               router=routes["_" + name + "_router"](make=make,
                                                                     model=model,
                                                                     sort=market_definition["sort"]),
                               remote=market_definition['result_body_class'],
                               next_button_text='Next',
                               result_stub=market_definition['result_stub'])
        return 'ok'

    @route('/add_market/<string:name>/<int:remote>', methods=['PUT'])
    def make_market(self, name, remote):
        if name in markets.keys():
            return "Market name is taken"
        market_definition = request.get_json()
        if remote is 0:
            remote = False
        else:
            remote = market_definition['remote']
        exclude = market_definition['result_exclude'].split(',')
        markets[name] = Market(name=name,
                               result_css=market_definition['result_css'],
                               result_exclude=exclude,
                               wait_for_car=market_definition['wait_for_car'],
                               json_identifier=market_definition['json_identifier'],
                               next_page_xpath=market_definition['next_page_xpath'],
                               mapper=mappers["_" + name + "_mapper"],
                               router=routes["_" + name + "_router"](make=None,
                                                                     model=None,
                                                                     sort=market_definition["sort"]),
                               next_button_text=market_definition['next_button_text'],
                               remote=remote,
                               result_stub=market_definition['result_stub'])
        return "ok"

    @route('/start/<string:name>', methods=['PUT'])
    def start(self, name):
        market = markets[name]
        market.start()
        return "started"

    @route('/resume/<string:name>', methods=['PUT'])
    def resume(self, name):
        market = markets[name]
        market.resume()
        return "resumed"

    @route('/stop/<string:name>', methods=['PUT'])
    def stop(self, name):
        market = markets[name]
        market.stop()
        return "stopped"
