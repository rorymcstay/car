import json

from flask_classy import FlaskView, route

from src.main.market.Market import Market
from src.main.service.mongo_service.MongoService import MongoService

service = MongoService('{}:{}'.format('0.0.0.0', 27017))


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
        newWorker = Market.instance().addWorker()
        return json.dumps(newWorker)

    @route('/removeWorker', methods=['DELETE'])
    def removeWorker(self):
        Market.instance().removeWorker()
        return 'ok'

    @route('/makeWorkers/<int:max_containers>', methods=['GET'])
    def makeWorkers(self, number):
        """
        create workers for a market. Client specifies the number of containers to use

        :param name: market name
        :param max_containers: max containers
        :return: ok
        """
        Market.instance().makeWorkers(number)
        returnString = [{w.batch_number: w.healthCheck()} for w in Market.instance().workers]

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
        Market.instance().setHome(make, model)
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
        Market.instance().setHome(sort)
        return 'ok'


    @route('/cleanUpResources', methods=['GET'])
    def cleanUpResources(self):
        """
        Destroy Workers' resources
        :param name:
        :return:
        """
        Market.instance().tearDownWorkers()
        return 'ok'

    @route('/goHome/<string:name>', methods=['GET'])
    def goHome(self, name):
        """
        go back to the home page

        :param name:
        :return:
        """
        Market.instance().goHome()
        return 'ok'
