import json

from flask import request, Response
from flask_classy import FlaskView, route

from src.main.container import ContainerManager
from src.main.parameters import ParameterManager


class ContainerController(FlaskView):
    containerManager = ContainerManager()

    @route("getContainer/<int:port>", methods=["GET"])
    def getContainer(self, port):
        return self.containerManager.getContainer(port)

    @route("freeContainer/<int:port>", methods=["GET"])
    def freeContainer(self, port):
        return self.containerManager.freeContainer(port)

class ParameterController(FlaskView):
    parameterManager = ParameterManager()
    parameterManager.loadParams()

    @route("/getParameter/<string:name>/<string:feed>")
    def getParameter(self, name, feed):
        params = self.parameterManager.getParameter(name, feed)
        return Response(json.dumps(params), mimetype="application/json")

    @route("/setParameter/<string:name>/<string:feed>", methods=["PUT"])
    def setParameter(self, name, feed):
        value=request.get_json()
        self.parameterManager.setParameter(name, feed, value)
        return "ok"


