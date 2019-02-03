from unittest import TestCase
import unittest

from market.Worker import Worker
from resources.donedeal_market import market


class TestWorker(TestCase):

    def test_clean_up(self):
        """Test the creation of a worker and that it can be closed succesfully"""

        '''setup: create a market worker and verify that the webcrawler and browser are running:'''
        worker = Worker(1, market=market, remote=True)
        worker.webCrawler.driver.get("https://www.google.com")
        worker.health_check()
        self.assertEqual(worker.health.browser, 'running')
        self.assertEqual(worker.health.webcrawler, "https://www.google.com/")

        '''then: cleanup the worker and verify everything has closed'''
        worker.clean_up()
        worker.health_check()
        self.assertEqual(worker.health.browser, 'Removed')
        self.assertEqual(worker.health.webcrawler, 'Unhealthy')
