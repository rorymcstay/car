from time import time

from flask_classy import FlaskView, route


class Command(FlaskView):
    """
    Flask Classy object which contains a dictionary of Markets. On start up it loads market definitions from the
    database and creates Market objects.

    """


    @route('/specifyMakeModel/<string:make>/<string:model>', methods=['GET'])
    def specifyMakeModel(self, make, model):
        """
        Change the make and model to be collected

        :param make:
        :param model:
        :param name:
        :return:
        """
        market.setHome(make, model)
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
        market.setHome(sort)
        return 'ok'

    @route('/goHome/<string:name>', methods=['GET'])
    def goHome(self):
        """
        go back to the home page

        :param name:
        :return:
        """
        market.goHome()
        return 'ok'

    @route("/publishListOfResults")
    def publishListOfResults(self):
        start = time()
        market.publishListOfResults()
        return "finished in {} seconds".format((time() - start))

    @route("/setHome/<string:make>/<string:model>/<string:sort>")
    def setHome(self, make, model, sort):
        home = market.setHome(make, model, sort)
        return home
