import time
import unittest
from unittest import TestCase

from market.Worker import Worker
from resources.donedeal_market import market


class TestPersistence(TestCase):
    def test_return_to_previous(self):
        '''go 8 pages deep and save the page'''
        market.webCrawler.retrace_steps(8)
        market.webCrawler.update_latest_page()
        latest = market.webCrawler.last_result
        market.workers = [Worker(i, market) for i in range(1)]
        market.workers[0].webCrawler.driver.get(market.webCrawler.get_result_array()[7])
        market.workers[1].webCrawler.driver.get(market.webCrawler.get_result_array()[9])

        '''Go back two pages before we save progress'''
        market.webCrawler.driver.back()
        time.sleep(1)
        market.webCrawler.driver.back()
        time.sleep(1)

        '''Save progress'''
        market.persistence.save_progress()

        '''Then lose progress'''
        market.webCrawler.driver.get('https://www.google.com')

        '''Then try to return'''
        market.persistence.return_to_previous()

        '''Check we returned succesfully'''
        self.assertEqual(market.webCrawler.driver.current_url, latest)


if __name__ == '__main__':
    unittest.main()

