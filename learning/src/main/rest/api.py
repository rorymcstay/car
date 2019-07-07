from flask_classy import FlaskView, route

from src.main.dataframe.api import CarManager


class DataFrameController(FlaskView):
    carManager = CarManager('donedeal')

    @route("/<string:name>/get_cars", methods=["GET"])
    def getCarDataFrame(self):
        """
        return a json payload of dataframe.
        :return:
        """
        data = self.carManager.returnLatestCarObservations()
        payload = data.to_json()
        return payload
