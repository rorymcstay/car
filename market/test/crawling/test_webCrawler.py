from unittest import TestCase
from car.market.src.crawling.WebCrawler import WebCrawler

class TestWebCrawler(TestCase):

    def test_next_page(self, market):
        market.driver.get(market.url_mapping)


    def test_get_results(self):
        self.fail()

    def test_load_page(self):
        self.fail()
