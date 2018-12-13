import re
from car.market.src.Market import Market
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC



class WebCrawler:
    def __init__(self, market):
        self.market = market
        self.base = None
        self.number_of_pages = None
        self.driver = self.market.driver

    def DoneDeal(self, make, model):
        self.base =  "https://www.donedeal.co.uk/cars/"+make+"/"+model+"?sort=publishdate%20asc"

    def PistonHeads(self, make, model):
        self.base = "https://www.pistonheads.com/classifieds/used-cars/"+make+"/"+model

    def next_page(self):
        driver = self.market.driver
        driver.find_element_by_css_selector(self.market.next_page).click()
        try:
            element_present = EC.presence_of_element_located((By.ID, self.market.wait_for))
            WebDriverWait(driver, 10).until(element_present)
            return driver.page_source
        except TimeoutException:
            print("Could not get the next page of results: " + TimeoutException.message)

    def get_results(self, source):
        self.market.extend(re.findall(r'' + self.market.result_stub + '[^\"]+', source))

    def load_page(self):

    def get_pages(self):
        driver



