import requests
from flask import jsonify
from flask import request
from flask_classy import FlaskView, route

from settings import nanny_params
from src.main.manager import RoutingManager


class RoutingController(FlaskView):
    routingManager = RoutingManager()

    @route("getResultPageUrl/<string:name>")
    def getResultPageUrl(self, name):
        """
        return the home adress of market to the client
        :return:
        """
        options = request.json
        return self.routingManager.getResultPageUrl(name=name, **options)

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
        lastPage = self.routingManager.getLastPage(name)
        if lastPage:
            resp = jsonify(lastPage)
            resp.status_code = 200
            return resp
        else:
            return "none"

    @route("clearHistory/<string:name>", methods=["DELETE"])
    def clearHistory(self, name):
        self.routingManager.clearHistory(name)
        return "ok"

