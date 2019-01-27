from unittest import TestCase
import unittest
from src.test.resources.donedeal_market import market as DoneDeal
from src.test.resources.donedeal_market import next_page_expectation as DoneDealExpectation
from src.test.resources.donedeal_car_raw import raw_car_expectation as DoneDealRawCar
from src.test.market.crawling.helper_webCrawler import test_next_page, test_result_page, test_get_raw_car, test_order_history


class TestWebCrawler(TestCase):

    def test_markets_next_page(self):
        result = test_next_page(DoneDeal)
        self.assertEqual(result, DoneDealExpectation)

    def test_markets_result_page(self):
        result = test_result_page(market=DoneDeal,
                                  url_result=DoneDealExpectation[2],
                                  url_car="https://www.donedeal.co.uk/cars-for-sale/toyota-corolla/20804176")
        self.assertTrue(result)

    def test_markets_get_raw_car(self):
        result = test_get_raw_car(market=DoneDeal,
                                  url="https://www.donedeal.co.uk/cars-for-sale/toyota-corolla/20804176")
        self.assertEqual(result, DoneDealRawCar)

    def test_markets_order_history(self):
        result = test_order_history(DoneDeal, urls=DoneDealExpectation)



if __name__ == '__main__':
    unittest.main()