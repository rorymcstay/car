from unittest import TestCase
import unittest
from selenium.webdriver.support.wait import WebDriverWait
from car.tools.DoneDealFeed import market as DoneDeal
from car.test.resources.donedeal_market import next_page_expectation as DoneDealExpectation
from car.test.resources.donedeal_car_raw import raw_car_expectation as DoneDealRawCar


class TestWebCrawler(TestCase):

    def test_next_page(self, market, expectation):
        market.crawler.driver.get(market.home)
        WebDriverWait(market.crawler.driver, 5)
        visits = []
        market.crawler.next_page()
        visits.append(market.crawler.driver.current_url)
        market.crawler.next_page()
        visits.append(market.crawler.driver.current_url)
        market.crawler.next_page()
        visits.append(market.crawler.driver.current_url)
        assert visits == expectation

    def test_result_page(self, market, url_result, url_car):
        market.crawler.driver.get(url_car)
        WebDriverWait(market.crawler.driver, 5)
        self.assertTrue(market.crawler.result_page())
        market.crawler.driver.get(url_result)
        WebDriverWait(market.crawler.driver, 5)
        self.assertTrue(market.crawler.result_page())

    def test_get_raw_car(self, market, url, expectation):
        market.crawler.driver.get(url)
        WebDriverWait(market.crawler.driver, 5)
        car = market.crawler.get_raw_car()
        assert expectation == car

    def test_markets_next_page(self):
        self.test_next_page(DoneDeal, DoneDealExpectation)

    def test_markets_result_page(self):
        self.test_result_page(market=DoneDeal,
                              url_result=DoneDealExpectation[2],
                              url_car="https://www.donedeal.co.uk/cars-for-sale/toyota-corolla/20804176")

    def test_markets_get_raw_car(self):
        self.test_get_raw_car(market=DoneDeal,
                              url="https://www.donedeal.co.uk/cars-for-sale/toyota-corolla/20804176",
                              expectation=DoneDealRawCar)

    def tearDownClass(cls):
        cls.addCleanup(DoneDeal.crawler.driver.quit())


if __name__ == '__main__':
    unittest.main()
