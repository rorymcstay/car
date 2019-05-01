import json
from typing import Dict

from flask_classy import FlaskView, route

from src.main.car.Domain import Encoder
from src.main.mapping.Mappers import mappers
from src.main.market.Market import Market
from src.main.market.crawling.Routers import routes
from src.main.service.mongo_service.MongoService import MongoService

service = MongoService('{}:{}'.format('0.0.0.0', 27017))

marketSet: Dict[str, Market] = {}


class Command(FlaskView):
    """
    Flask Classy object which contains a dictionary of Markets. On start up it loads market definitions from the
    database and creates Market objects.

    """

    @route('/add_market/<string:name>', methods=['PUT'])
    def addMarket(self, name):
        """
        create a new Market Object and save to database

        :param name:
        :return:
        """
        if name in marketSet.keys():
            returnString = [worker.health_check() for worker in marketSet[name].workers]
            return json.dumps(returnString)
        marketSet[name] = Market(name=name,
                                 mapper=mappers["_" + name + "_mapper"],
                                 router=routes["_" + name + "_router"])
        marketSet[name].webCrawler.driver.get(marketSet[name].home)
        return 'ok'

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

        return json.dumps(returnString)

    @route('/get_results/<string:name>', methods=['GET'])
    def getResults(self, name):
        """
        return current page of results

        :param name:
        :return:
        """
        returnString = marketSet[name].getResults()
        marketSet[name].webCrawler.next_page()
        return json.dumps(returnString, cls=Encoder)

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
