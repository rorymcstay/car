import json
import re

from bs4 import BeautifulSoup
from selenium.webdriver.chrome import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor



class WebCrawler(webdriver):
    
    def __init__(self, market, make = None, model = None, remote = None  ):
        self.market = market
        self.base = None
        self.number_of_pages = None
        self.make = make
        self.model = model
        self.queue = None
        if remote is None:
            self.driver = webdriver.Chrome()
            arguments=['--headless']
            self.chrome_options = Options()
            self.chrome_options.add_argument(arguments)
        else:
            self.options = webdriver.Chrome().create_options()

            # adding options to driver
            self.options.add_argument("--lang=en")
            self.options.add_argument("--headless")

            # defining driver
            self.driver = webdriver.Remote(command_executor=remote,
                                           desired_capabilities=webdriver.DesiredCapabilities.CHROME)
            # self.driver = webdriver.RemoteWebDriver(command_executor=remote, desired_capabilities=)
        self.current_car = None

    def DoneDeal(self, sort):
        if self.make and self.model is not None:
            self.base =  "https://www.donedeal.co.uk/cars/"+self.make+"/"+self.model+"?sort="+sort
        elif self.make is not None and self.model is None:
            self.base = "https://www.donedeal.co.uk/cars/"+self.make+"?sort=publishdate%20asc"
        else:
            self.base = "https://www.donedeal.co.uk/cars?sort=publishdate%20asc"

    def PistonHeads(self, make, model):
        return "https://www.pistonheads.com/classifieds/used-cars/"+make+"/"+model
        
    def next_page(self):
        driver = self.market.driver
        try:
            driver.find_element_by_css_selector(self.market.next_page_css).click()
            results_loaded = EC.presence_of_element_located((By.CLASS_NAME, self.market.result_body_class))
            WebDriverWait(driver, 10).until(results_loaded)
        except TimeoutException:
            print("Could not get the next page of results: " + TimeoutException.message)
    
    def load_queue(self):
        try:
            self.queue = self.driver.find_elements_by_class_name(self.market.result_body_class)
        except:
            print Exception.message
            return

    def get_result(self, result):
        result.click()
        element_present = EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.market.wait_for_car))
        WebDriverWait(self.market.driver, 10).until(element_present)
        result = self.get_car()
        self.driver.back()
        element_present = EC.presence_of_all_elements_located((By.CLASS_NAME, self.market.result_body_class))
        WebDriverWait(self.driver, 10).until(element_present)
        return result

    def get_car(self):
        """
        attempts to get car from current page source, returns 
        :param mapping: 
        :return: 
        """
        source = self.driver.page_source
        soup = BeautifulSoup(source, 'html.parser')
        for script in soup.find_all('script'):
            if self.market.json_identifier in script.text:
                tree = JavascriptParser().parse(script.text)
                raw_car_details = next(node.right for node in nodevisitor.visit(tree)
                           if (isinstance(node, ast.Assign) and
                               node.left.to_ecma() == self.market.json_identifier))
                data = json.loads(raw_car_details.to_ecma())
                print ("Found " + self.market.json_identifier + ": doing mapping")
            else:
                self.driver.back()
                print("Could not find json_identifier = " + self.market.json_identifier)
                return
            try: 
                default_car = self.market.mapping(data)
                print "Succesfully mapped to default car"
                return default_car
            except:
                print "could not map raw car"
                self.driver.back()
                return  # data
    
    
