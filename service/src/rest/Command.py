import json
import os

from flask import request
from flask_classy import FlaskView, route
from car.market.src.Market import Market
from car.market.src.mapping.Mappers import Mappers
from car.market.src.mongo_service.MongoService import MongoService
from car.market.src.crawling.Routers import Routers
from car.service.src.browser.BrowserService import browser_service

service = MongoService()

markets = {}
routes = Routers()
mappers = Mappers()


class Command(FlaskView):

    @route('/add_market/<string:name>/<int:remote>/<string:make>/<string:model>', methods=['PUT'])
    def make_market_specific(self, name, make, model, remote):
        if remote == 1:
            remote = browser_service.new_service(name)
        else:
            remote = False
        market_definition = request.get_json()
        exclude = str(market_definition['result_exclude']).split(',')
        service.save_market_details(json.loads(market_definition))
        markets[name] = Market(name=str(market_definition['name']),
                               result_css=str(market_definition['result_body_class']),
                               result_exclude=exclude,
                               wait_for_car=str(market_definition['wait_for_car']),
                               json_identifier=str(market_definition['json_identifier']),
                               next_page_xpath=str(market_definition['next_page_css']),
                               mapper=mappers["_" + name + "_mapper"],
                               router=routes["_" + name + "_router"](make=make, model=model,
                                                                     sort=str(market_definition["sort"])),
                               remote=remote)
        return 'ok'

    @route('/add_market/<string:name>/<int:remote>', methods=['PUT'])
    def make_market(self, name, remote):
        if remote == 1:
            remote = browser_service.new_service(name=name)
        else:
            remote = False
        market_definition = request.get_json()
        exclude = str(market_definition['result_exclude']).split(',')
        # service.save_market_details(json.loads(str(market_definition)))
        markets[name] = Market(name=str(name),
                               result_css=str(market_definition['result_css']),
                               result_exclude=exclude,
                               wait_for_car=str(market_definition['wait_for_car']),
                               json_identifier=str(market_definition['json_identifier']),
                               next_page_xpath=str(market_definition['next_page_xpath']),
                               mapper=mappers["_" + name + "_mapper"],
                               router=routes["_" + name + "_router"](make=None,
                                                                     model=None,
                                                                     sort=str(market_definition["sort"])),
                               remote=remote)
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
