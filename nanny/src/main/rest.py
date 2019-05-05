from flask import request
from flask_classy import FlaskView, route

from src.main.delegator import Delegator


class RoutingController(FlaskView):
    routingManager = Delegator()

    @route("getBaseUrl/<string:name>/<string:make>/<string:model>/<string:sort>", methods=["GET"])
    def getBaseUrl(self, name, make, model, sort):
        """
        return a json payload of dataframe.
        :return:
        """
        return self.routingManager.getBaseUrl(name, make, model, sort)

    @route("getBaseUrl/<string:name>/<string:make>/<string:model>/<string:sort>", methods=["GET"])
    def getBaseUrl(self, name, make, model, sort):
        """
        return a json payload of dataframe.
        :return:
        """
        return self.routingManager.getBaseUrl(name, make, model, sort)


    @route("updateHistory/name")
    def updateHistory(self, name):
        self.routingManager.updateHistory(name, request.data)
