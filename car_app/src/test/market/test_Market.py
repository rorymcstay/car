from unittest import TestCase
from resources.donedeal_market import market


class TestMarket(TestCase):

    def test_garbage_collection(self):
        """This test when an exception is thrown, the resources are stopped"""

