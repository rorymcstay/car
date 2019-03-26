import json
import os
from typing import Dict

from flask import request
from flask_classy import FlaskView, route

from src.main.car.Domain import MarketDetails
from src.main.market.Market import Market
from src.main.market.crawling.Routers import routes
from src.main.market.mapping.Mappers import mappers
from src.main.service.mongo_service.MongoService import MongoService
from src.main.service.rest.flask_helper.headers import JSON

service = MongoService('{}:{}'.format('0.0.0.0', 27017))

marketSet: Dict[str, Market] = {}


class Command(FlaskView):
    """
    Flask Classy object which contains a dictionary of Markets. On start up it loads market definitions from the
    database and creates Market objects.

    """
    markets = service.market_details_collection.find()

    for market_definition in markets:
        marketDetails = MarketDetails(name=market_definition['name'],
                                      result_css=market_definition['result_css'],
                                      result_exclude=market_definition['result_exclude'],
                                      wait_for_car=market_definition['wait_for_car'],
                                      json_identifier=market_definition['json_identifier'],
                                      next_page_xpath=market_definition['next_page_xpath'],
                                      next_button_text='Next',
                                      result_stub=market_definition['result_stub'],
                                      sort=market_definition['sort'])
        name = market_definition['name']
        marketSet[name] = Market(marketDetails=marketDetails,
                                 mapper=mappers["_" + name + "_mapper"],
                                 router=routes["_" + name + "_router"],
                                 mongo_port=int(os.getenv('MONGO_PORT', 27017)),
                                 browser_port=int(os.getenv('BROWSER_BASE_PORT', 4444)))

    @route('/add_market/<string:name>', methods=['PUT'])
    def addMarket(self, name):
        """
        create a new Market Object and save to database

        :param name:
        :return:
        """
        market_definition = request.get_json()
        exclude = str(market_definition['result_exclude']).split(',')
        marketDetails = MarketDetails(name=name,
                                      result_css=market_definition['result_css'],
                                      result_exclude=exclude,
                                      wait_for_car=market_definition['wait_for_car'],
                                      json_identifier=market_definition['json_identifier'],
                                      next_page_xpath=market_definition['next_page_xpath'],
                                      next_button_text='Next',
                                      result_stub=market_definition['result_stub'],
                                      sort=market_definition['sort'])
        if name in marketSet.keys():
            returnString = [worker.health_check() for worker in marketSet[name].workers]
            return json.dumps(returnString)
        service.save_market_details(name=marketDetails.name, market_definition=marketDetails)
        marketSet[name] = Market(marketDetails=marketDetails,
                                 mapper=mappers["_" + name + "_mapper"],
                                 router=routes["_" + name + "_router"],
                                 mongo_port=int(os.getenv('MONGO_PORT', 27017)),
                                 browser_port=int(os.getenv('BROWSER_BASE_PORT', 4444)))
        marketSet[name].webCrawler.driver.get(marketSet[name].home)
        return 'ok'

    @JSON
    @route('/initialise/<string:name>/<int:max_containers>', methods=['GET'])
    def initialise(self, name, max_containers):
        """
        create workers for a market. Client specifies the number of containers to use

        :param name: market name
        :param max_containers: max containers
        :return: ok
        """
        marketSet[name].makeWorkers(max_containers)
        returnString = [{w.batch_number: w.health_check()} for w in marketSet[name].workers]

        return json.dumps(returnString), 200, 'application/json'

    @JSON
    @route('/get_results/<string:name>', methods=['GET'])
    def getResults(self, name):
        """
        return current page of results

        :param name:
        :return:
        """
        returnString = marketSet[name].getResults()
        marketSet[name].webCrawler.next_page()
        return json.dumps(returnString), 200, 'application/json'

    @route('/reset/<string:name>/<string:make>/<string:model>', methods=['GET'])
    def specifyMakeModel(self, make, model, name):
        """
        Change the make and model to be collected

        :param make:
        :param model:
        :param name:
        :return:
        """
        marketSet[name].specifyMakeModel(make, model)
        return 'ok'

    @route('/clean_up_resources/name', methods=['GET'])
    def cleanUpResources(self, name):
        """
        Destroy Workers' resources
        :param name:
        :return:
        """
        marketSet[name].tear_down_workers()
        return 'ok'

    @route('/reset/<string:name>', methods=['GET'])
    def reset(self, name):
        """
        go back to the home page

        :param name:
        :return:
        """
        marketSet[name].goHome()
        return 'ok'
