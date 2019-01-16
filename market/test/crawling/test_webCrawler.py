from unittest import TestCase, skip
from selenium.webdriver.support.wait import WebDriverWait
from car.tools.DoneDealFeed import market as DoneDeal
from car.market.test.crawling.resources.donedeal_market import next_page_expectation as DoneDealExpectation
from car.market.test.crawling.resources.donedeal_car_raw import raw_car_expectation as DoneDealRawCar

class TestWebCrawler(TestCase):
    @skip
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

    @skip
    def test_result_page(self, market, url_result, url_car):
        market.crawler.driver.get(url_car)
        assert market.crawler.result_page() is False
        market.crawler.driver.get(url_result)
        assert market.crawler.result_page() is True

    @skip
    def test_get_raw_car(self, market, url, expectation):
        market.crawler.driver.get(url)
        car = market.crawler.get_raw_car()
        assert expectation == car

    def test_markets_next_page(self):
        self.test_next_page(DoneDeal, DoneDealExpectation)

    def test_markets_result_page(self):
        self.test_result_page(DoneDeal, DoneDealExpectation[2], "https://www.donedeal.co.uk/cars-for-sale/toyota-corolla/20804176")

    def test_markets_get_raw_car(self):
        self.test_get_raw_car(DoneDeal, "https://www.donedeal.co.uk/cars-for-sale/toyota-corolla/20804176", DoneDealRawCar)



