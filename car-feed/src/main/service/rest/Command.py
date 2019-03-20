import json
import os

from flask import request
from flask_classy import FlaskView, route

from src.main.car.Domain import MarketDetails
from src.main.market.Market import Market
from src.main.market.crawling.Routers import routes
from src.main.market.mapping.Mappers import mappers
from src.main.service.mongo_service.MongoService import MongoService

markets = {}
service = MongoService('{}:{}'.format('0.0.0.0', 27017))

class Command(FlaskView):

    @route('/add_market/<string:name>', methods=['PUT'])
    def make_market_specific(self, name):
        market_definition = request.get_json()
        exclude = str(market_definition['result_exclude']).split(',')
        marketDetails = MarketDetails(name=name,
                                      result_css=market_definition['result_css'],
                                      result_exclude=exclude,
                                      wait_for_car=market_definition['wait_for_car'],
                                      json_identifier=market_definition['json_identifier'],
                                      next_page_xpath=market_definition['next_page_xpath'],
                                      next_button_text='Next',
                                      result_stub=market_definition['result_stub'])
        if name in markets.keys():
            return "Market name is taken"
        service.save_market_details(name=marketDetails.name, market_definition=marketDetails)
        markets[name] = Market(marketDetails=marketDetails,
                               mapper=mappers["_" + name + "_mapper"],
                               router=routes["_" + name + "_router"],
                               mongo_port=int(os.getenv('MONGO_PORT', 27017)),
                               browser_port=int(os.getenv('BROWSER_BASE_PORT', 4444)))
        markets[name].webCrawler.driver.get(markets[name].home)
        markets[name].makeWorkers(4)
        return 'ok'

    @route('/get_results/<string:name>', methods=['GET'])
    def getResults(self, name):
        results = markets[name].getResults()
        return json.dumps(results)

    @route('/reset/<string:name>/<string:make>/<string:model>', methods=['PUT'])
    def specifyMakeModel(self, make, model, name):
        markets[name].specifyMakeModel(make, model)
        return 'ok'

    @route('/reset/<string:name>', methods=['PUT'])
    def specifyMakeModel(self, name):
        markets[name].goHome()
        return 'ok'
