from unittest import TestCase

from main.dataframe.api import CarManager

from src.test.resources import test_car


class TestCarManager(TestCase):

    def setUpClass(cls):

        cls.carObservationManager = CarManager()

    def test_returnCarObservations(self):

        self.carObservationManager.returnCarObservation(test_car)
        pass
