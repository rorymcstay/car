import unittest
from unittest import TestCase
from src.test.resources.donedeal_market import next_page_expectation as DoneDealExpectation
from src.test.resources.donedeal_car_raw import raw_car_expectation as DoneDealRawCar
from selenium.webdriver.support.wait import WebDriverWait
from src.test.resources.donedeal_market import market as DoneDeal


class TestWebCrawler(TestCase):
    def test_next_page(self, market=DoneDeal, urls=DoneDealExpectation):
        market.webCrawler.driver.get(market.home)
        WebDriverWait(market.webCrawler.driver, 5)
        visits = []
        market.webCrawler.next_page()
        market.webCrawler.update_latest_page()
        visits.append(market.webCrawler.driver.current_url)
        market.webCrawler.next_page()
        market.webCrawler.update_latest_page()
        visits.append(market.webCrawler.driver.current_url)
        market.webCrawler.update_latest_page()
        market.webCrawler.next_page()
        visits.append(market.webCrawler.driver.current_url)
        self.assertEqual(visits, urls, market.webCrawler.history)

    def test_result_page(self, market = DoneDeal, url_result=DoneDealExpectation[2], url_car="https://www.donedeal.co.uk/cars-for-sale/toyota-corolla/20804176"):
        market.webCrawler.driver.get(url_car)
        WebDriverWait(market.webCrawler.driver, 5)
        self.assertTrue(market.webCrawler.result_page())
        market.webCrawler.driver.get(url_result)
        WebDriverWait(market.webCrawler.driver, 5)
        self.assertTrue(market.webCrawler.result_page())

    def test_get_raw_car(self, url="https://www.donedeal.co.uk/cars-for-sale/toyota-corolla/20804176", market=DoneDeal):
        market.webCrawler.driver.get(url)
        WebDriverWait(market.webCrawler.driver, 5)
        car = market.webCrawler.get_raw_car()
        self.assertEqual(car, DoneDealRawCar)

    def doCleanups(self, market=DoneDeal):
        market.browser.quit()
        for w in market.workers:
            w.clean_up()


if __name__ == '__main__':
    unittest.main()

