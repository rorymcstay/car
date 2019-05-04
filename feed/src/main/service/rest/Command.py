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

    @route('/add_market', methods=['PUT'])
    def addWorker(self):
        """
        create a new Market Object and save to database

        :param name:
        :return:
        """
        newWorker = Market.instance().addWorker()
        return json.dumps(newWorker)

    @route('/remove_worker', methods=['DELETE'])
    def removeWorker(self):
        Market.instance().removeWorker()
        return 'ok'

    @route('/initialise/<int:max_containers>', methods=['GET'])
    def initialise(self, name, max_containers):
        """
        create workers for a market. Client specifies the number of containers to use

        :param name: market name
        :param max_containers: max containers
        :return: ok
        """
        Market.instance().makeWorkers(max_containers)
        returnString = [{w.batch_number: w.health_check()} for w in marketSet[name].workers]

        return json.dumps(returnString)


    @route('/reset/<string:make>/<string:model>', methods=['GET'])
    def specifyMakeModel(self, make, model, name):
        """
        Change the make and model to be collected

        :param make:
        :param model:
        :param name:
        :return:
        """
        Market.instance().specifyMakeModel(make, model)
        return 'ok'

    @route('/clean_up_resources', methods=['GET'])
    def cleanUpResources(self):
        """
        Destroy Workers' resources
        :param name:
        :return:
        """
        Market.instance().tear_down_workers()
        return 'ok'

    @route('/reset/<string:name>', methods=['GET'])
    def reset(self, name):
        """
        go back to the home page

        :param name:
        :return:
        """
        Market.instance().goHome()
        return 'ok'
