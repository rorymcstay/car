from flask_classy import FlaskView, route

from src.main.container import ContainerManager


class ContainerController(FlaskView):
    containerManager = ContainerManager()

    @route("getContainer/<int:port>", methods=["GET"])
    def getContainer(self, port):
        return self.containerManager.getContainer(port)

    @route("freeContainer/<int:port>", methods=["GET"])
    def freeContainer(self, port):
        return self.containerManager.freeContainer(port)
