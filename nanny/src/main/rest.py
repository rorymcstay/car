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


    @route("/getParameter/<string:name>/<string:feed>")
    def getParameter(self, name, feed):
        params = self.parameterManager.getParameter(name=name, feed=feed)
        return Response(json.dumps(params), mimetype="application/json")

    @route("/getParameter/<string:feed>")
    def getParameters(self, feed):
        params = self.parameterManager.getParameter(feed)
        return Response(json.dumps(params), mimetype="application/json")

    @route("/setParameter/<string:name>/<string:feed>", methods=["PUT"])
    def setParameter(self, name, feed):
        value=request.get_json()
        self.parameterManager.setParameter(name=name, feed=feed, value=value)
        return "ok"
#
# if __name__ == '__main__':
#     ParameterController().parameterManager.loadParams()


