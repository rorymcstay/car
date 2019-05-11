from flask import request
from flask_classy import FlaskView, route

from src.main.manager import RoutingManager


class RoutingController(FlaskView):
    routingManager = RoutingManager()

    @route("getBaseUrl/<string:name>/<string:make>/<string:model>/<string:sort>", methods=["GET"])
    def getBaseUrl(self, name, make, model, sort):
        """
        return the home adress of market to the client
        :return:
        """
        return self.routingManager.getBaseUrl(name, make, model, sort)

    @route("updateHistory/<string:name>", methods=["PUT"])
    def updateHistory(self, name):
        """
        Add a history item to the cache of the caller
        :param name:
        :return:
        """
        return self.routingManager.updateHistory(name, request.data)

    @route("getLastPage/<string:name>", methods=["GET"])
    def getLastPage(self, name):
        """
        get the last page of the caller

        :param name:
        :return:
        """
        return self.routingManager.getLastPage(name)
