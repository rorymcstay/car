import unittest
from unittest import TestCase

from market.Worker import Worker
from market.utils.HealthConstants import HealthConstants
from resources.donedeal_market import market


class TestMarket(TestCase):

    def test_garbage_collection(self):
        """This test when an exception is thrown, the resources are stopped"""

        '''When we run three threads'''
        market.workers = [Worker(i, market) for i in range(1)]

        for worker in market.workers:
            worker.health_check()
            self.assertEqual(worker.health.browser, HealthConstants().browser)
            self.assertEqual(worker.health.browser, HealthConstants().browser)

        '''And mock throw an exception'''
        market.workers[0].clean_up()
        market.workers[0].health_check(Exception('Oh no an exception'))

        '''call garbage collection'''
        market.garbage_collection()

        '''check that the worker has regenerated have started'''
        market.workers[0].health_check()
        self.assertEqual(market.workers[0].health.browser, HealthConstants().browser)
        self.assertEqual(market.workers[0].health.webcrawler, HealthConstants().webCrawler)


if __name__ == '__main__':
    unittest.main()

