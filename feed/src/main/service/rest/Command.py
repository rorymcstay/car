import json
from time import time

from flask_classy import FlaskView, route

from src.main.market.Market import Market
from src.main.service.mongo_service.MongoService import MongoService

service = MongoService('{}:{}'.format('0.0.0.0', 27017))

market = Market()
class Command(FlaskView):
    """
    Flask Classy object which contains a dictionary of Markets. On start up it loads market definitions from the
    database and creates Market objects.

    """

    @route('/addWorker', methods=['PUT'])
    def addWorker(self):
        """
        create a new Market Object and save to database

        :param name:
        :return:
        """
        newWorker = market.addWorker()
        return json.dumps(newWorker)

    @route('/removeWorker', methods=['DELETE'])
    def removeWorker(self):
        market.removeWorker()
        return 'ok'

    @route('/makeWorkers/<int:max_containers>', methods=['GET'])
    def makeWorkers(self, number):
        """
        create workers for a market. Client specifies the number of containers to use

        :param name: market name
        :param max_containers: max containers
        :return: ok
        """
        market.makeWorkers(number)
        returnString = [{w.batch_number: w.healthCheck()} for w in market.workers]

        return json.dumps(returnString)


    @route('/specifyMakeModel/<string:make>/<string:model>', methods=['GET'])
    def specifyMakeModel(self, make, model):
        """
        Change the make and model to be collected

        :param make:
        :param model:
        :param name:
        :return:
        """
        market.setHome(make, model)
        return 'ok'

    @route("/sortResults/sort")
    def sortResults(self, sort):
        """
        Change the sort order - one of
            1. highest
            2. lowest
            3. old
            4. new

        :param make:
        :param model:
        :param name:
        :return:
        """
        market.setHome(sort)
        return 'ok'


    @route('/cleanUpResources', methods=['GET'])
    def cleanUpResources(self):
        """
        Destroy Workers' resources
        :param name:
        :return:
        """
        market.tearDownWorkers()
        return 'ok'

    @route('/goHome/<string:name>', methods=['GET'])
    def goHome(self):
        """
        go back to the home page

        :param name:
        :return:
        """
        market.goHome()
        return 'ok'

    @route("/publishListOfResults")
    def publishListOfResults(self):
        start = time()
        market.publishListOfResults()
        return "finished in {} seconds".format((time() - start))

    @route("/setHome/<string:make>/<string:model>/<string:sort>")
    def setHome(self, make, model, sort):
        home = market.setHome(make, model, sort)
        return home
