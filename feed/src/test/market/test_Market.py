import unittest
from unittest import TestCase

from src.main.market.Worker import Worker
from src.main.market.utils.HealthConstants import HealthConstants
from src.test.resources.donedeal_market import market as DoneDeal


class TestMarket(TestCase):

    def test_garbage_collection(self, market=DoneDeal):
        """This test when an exception is thrown, the resources are stopped"""

        '''When we run three threads'''
        market.workers = [Worker(i, market) for i in range(1)]

        for worker in market.workers:
            worker.healthCheck()
            self.assertEqual(worker.health.browser, HealthConstants().browser)
            self.assertEqual(worker.health.browser, HealthConstants().browser)

        '''And mock throw an exception'''
        market.workers[0].cleanUp()
        market.workers[0].healthCheck(Exception('Oh no an exception'))

        '''call garbage collection'''
        market.garbageCollection()

        '''check that the worker has regenerated have started'''
        market.workers[0].healthCheck()
        self.assertEqual(market.workers[0].health.browser, HealthConstants().browser)
        self.assertEqual(market.workers[0].health.webcrawler, HealthConstants().webCrawler)

    def doCleanups(self, market=DoneDeal):
        market.browser.quit()
        for w in market.workers:
            w.cleanUp()


if __name__ == '__main__':
    unittest.main()

