import json
from typing import Optional, Any

from flask import request, Response
from flask_classy import FlaskView, route

from src.main.container import ContainerManager
from src.main.parameters import ParameterManager


class ContainerController(FlaskView):
    containerManager = ContainerManager()

    @route("getContainer", methods=["GET"])
    def getContainer(self):
        return self.containerManager.getContainer()

    @route("getMainContainer/<int:port>", methods=["GET"])
    def getMainContainer(self, port):
        return self.containerManager.getMainContainer(port)

    @route("freeContainer/<int:port>", methods=["GET"])
    def freeContainer(self, port):
        return self.containerManager.freeContainer(port)

    @route("resetCache", methods=['GET'])
    def resetCache(self):
        return json.dumps(self.containerManager.resetContainers())

    @route("cleanUpContainer/<int:port>", methods=["GET"])
    def cleanUpContainer(self, port):
        return self.containerManager.cleanUpContainer(port)

    @route("getContainerStatus", methods=["GET"])
    def getContainerStatus(self):
        status = self.containerManager.getContainerStatus()
        return json.dumps(status)


class ParameterController(FlaskView):
    parameterManager = ParameterManager()

    @route("/getParameter/<string:collection>/<string:name>")
    def getParameter(self, collection, name):
        params: dict = self.parameterManager.getParameter(name=name, collection=collection)
        if params is None:
            return Response(status=404)
        params.pop("_id")
        return Response(json.dumps(params), mimetype="application/json")

    @route("/reportParameter/<string:collection>/<string:name>")
    def reportParameter(self, collection, name):
        r = request.data
        return self.parameterManager.reportParam(collection, name, r)
