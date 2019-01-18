from unittest import TestCase
import unittest
from car.tools.DoneDealFeed import market as DoneDeal
from car.src.test import next_page_expectation as DoneDealExpectation
from car.src.test import raw_car_expectation as DoneDealRawCar
from car.src.test import test_next_page, test_result_page, test_get_raw_car


class TestWebCrawler(TestCase):

    def test_markets_next_page(self):
        test_next_page(DoneDeal, DoneDealExpectation)

    def test_markets_result_page(self):
        test_result_page(market=DoneDeal,
                         url_result=DoneDealExpectation[2],
                         url_car="https://www.donedeal.co.uk/cars-for-sale/toyota-corolla/20804176")

    def test_markets_get_raw_car(self):
        test_get_raw_car(market=DoneDeal,
                         url="https://www.donedeal.co.uk/cars-for-sale/toyota-corolla/20804176",
                         expectation=DoneDealRawCar)


if __name__ == '__main__':
    unittest.main()
