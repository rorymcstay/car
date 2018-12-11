import re
import sys
from telnetlib import EC
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from crawling.webCrawler import get_results, get_cars

class Market:
    """
    This is the market class. You must specify the CSS identifier/selector
    to ensure the browser waits for that item before moving onto the next set of
    results.This. You must also provide the stub of the expected url of a results page.
    The market class is called by get_results() to fetch a specified number of pages
    in order, determined by the partial url strings.
    """

    def __init__(self,
                 name,
                 url_stub_1,
                 url_stub_2,
                 wait_for,
                 n_page,
                 result_stub,
                 wait_for_car,
                 json_identifier,
                 mapping,
                 browser):
        """

        :type name: object
        :param url_stub_1: This is the start of results page url ie. https://donedeal.ie/cars
        :param url_stub_2: This is the remainder of the url, it may be empty string or /desc/start=28 etc
        :param wait_for: This is the CSS item which must be loaded so that there are results on the page
        :param n_page: This is the number of cars per page. This may depend on the urls stub
        :param result_stub: This is the expected url stub of a car ie https://donedeal.ie/cars-for-sale
        :param wait_for_car: This is the CSS item which must be loaded for an individual car to be loaded
        :param json_identifier: What the JSON
        :param mapping: The string of the file defining the mapping from source json to generic car object
        :param browser: url of selenium container hosting browser
        """
        self.name = name
        self.url_stub_1 = url_stub_1
        self.url_stub_2 = url_stub_2
        self.wait_for = wait_for
        self.n_page = n_page
        self.result_stub = result_stub
        self.wait_for_car = wait_for_car
        self.latest_urls = []  # This is where the urls are stored to be processed next
        self.latest_source = []
        self.json_identifier = json_identifier
        self.cars = []
        self.mapping = mapping
        self.key = {}

        # Headless Remote driver

        # self.options = webdriver.ChromeOptions()
        # # self.options.add_argument("--lang=en")
        # # self.options.add_argument("--headless")
        # self.driver = webdriver.Remote(command_executor=browser,
        #                                desired_capabilities=webdriver.DesiredCapabilities.CHROME)

        # local driver
        self.driver = webdriver.Chrome()
        arguments=['--headless']
        self.chrome_options = Options()
        self.chrome_options.add_argument(arguments)

    def collect_cars(self, n):
        """
        Loads up the market's cache preparing it for mapping
        :param n:
        :return fills market.:
        """
        get_results(self, page_number=n)
        get_cars(self)
        return

    def initialise(self, n, service):
        for i in range(n):
            self.collect_cars(i)
            default_car = []
            for car in self.cars:
                try:
                    default_car.append(self.mapping(car))
                except:
                    print 'Parsing error'
            for car in default_car:
                service.insert(car)

    def watch(self):
        while True:
            driver = self.driver
            cars = []
            print("Gathering results from market")
            for x in 2:
                driver.get(self.url_stub_1 + str(x * self.n_page) + self.url_stub_2)
                try:
                    element_present = EC.presence_of_element_located((By.ID, self.wait_for))
                    WebDriverWait(driver, 10).until(element_present)
                except TimeoutException:
                    print("Timed out waiting for page to load")
                content = driver.page_source
                cars.extend(re.findall(r'' + self.result_stub + '[^\"]+', content))
                sys.stdout.flush()
            cars = list(set(cars))
            latest_cars = []
            for i in cars:
                if i in self.latest_urls:
                    print("Already have it")
                else:
                    latest_cars.append(i)
            self.latest_urls = []
            self.latest_source = []
            get_cars(self)
            sleep(600)

    def quit_browser(self):
        self.driver.quit()

    # TODO Make the watch method. When started, it will monitor a market place and repeatedly check for new cars