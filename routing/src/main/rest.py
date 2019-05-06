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

    @route("updateHistory/<string:name>")
    def updateHistory(self, name):
        """
        Add a history item to the cache of the caller
        :param name:
        :return:
        """
        self.routingManager.updateHistory(name, request.data)

    @route("assignNewPort/<int:port>", methods=["PUT"])
    def assignNewPort(self, name):
        """
        return a json payload of dataframe.
        :return:
        """
        return self.routingManager.assignPort(name)

    @route("freeContainer/<int:port>", methods=["PUT"])
    def freeContainer(self, port):
        return self.freeContainer(port)
