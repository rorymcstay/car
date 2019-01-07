import json
import logging as LOG
import os
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver as remotewebdriver
import selenium.webdriver as webdriver
from selenium.common.exceptions import (TimeoutException,
                                        StaleElementReferenceException,
                                        ElementClickInterceptedException,
                                        NoSuchElementException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class WebCrawler:

    def __init__(self, market, remote=False):
        """
        :type remote: Container
        :type market: Market
        """

        self.Market = market
        self.number_of_pages = None
        self.queue = None
        # determining location of driver
        if remote is False:
            # local driver
            self.driver = webdriver.Chrome()

            # adding options to driver
            arguments = ['--headless']
            self.chrome_options = Options()
            self.chrome_options.add_argument(arguments)
            LOG.info('Local driver initiated for %s', self.Market.name)
        else:
            # Getting driver location
            hub_host = remote.name
            port = os.environ['DRIVER_PORT']

            options = Options()
            options.add_argument("--headless")
            self.driver = remotewebdriver(command_executor="http://%s:%s/wd/hub" % (hub_host, port),
                                          desired_capabilities=DesiredCapabilities.CHROME,
                                          options=options)
            # TODO Cant establish connection
            LOG.info('Remote driver initiated for %s running on %s', self.Market.name, remote.name)

    def get_raw_car(self):
        """
        attempts to get car from current page source, returns to the previous set of results in which it came
        :return:
        """
        source = self.driver.page_source
        soup = BeautifulSoup(source, 'html.parser')

        out = []
        for script in soup.find_all('script'):
            if self.Market.json_identifier in script.text:
                tree = JavascriptParser().parse(script.text)
                script_objects = next(node.right for node in nodevisitor.visit(tree)
                                      if (isinstance(node, ast.Assign) and
                                          node.left.to_ecma() == self.Market.json_identifier))
                raw_car = json.loads(script_objects.to_ecma())
                LOG.debug("Found raw car json object %s ", self.Market.json_identifier)
                out.append(raw_car)

        if len(out) == 0:
            LOG.error("Could not find json_identifier = %s at %s",
                      self.Market.json_identifier,
                      self.driver.current_url)
            return False
        return out

    def safely_go_back(self, wait_for, selector, timeout):
        """
        This navigates back to the previous page and ensures the presence of an element

        :param selector: eg. By.CSS_SELECTOR
        :param wait_for: the element to be present.
        :param timeout:
        :return:
        """
        if all(partial in self.driver.current_url for partial in self.Market.home.split('/')):
            return
        else:
            try:
                self.driver.back()
                LOG.debug('Navigating back to results at: %s', self.driver.current_url)
                element_present = EC.presence_of_all_elements_located((selector, wait_for))
                WebDriverWait(self.driver, 10).until(element_present)

            except NoSuchElementException:
                LOG.warn("Expected element not found, refreshing page in %s seconds", timeout)
                WebDriverWait(timeout)
                self.driver.refresh()
            except TimeoutException:
                LOG.warn("Expected element not found, refreshing page in %s seconds")
                self.driver.refresh()

    def safely_click(self, item, wait_for, selector, timeout, attempt):
        """
        identifies xpath and css path to button. Attempts
        :param selector:
        :param wait_for:
        :param timeout:
        :param item:
        :return:
        """
        if attempt < int(os.environ['MAX_CLICK_ATTEMPTS']):
            try:
                item.click()
                element_present = EC.presence_of_all_elements_located((selector, wait_for))
                WebDriverWait(self.driver, 10).until(element_present)
                return True

            except ElementClickInterceptedException:
                attempt = attempt + 1
                # click unsuccesful waiting to refresh and try agin
                LOG.error("%s click on button was intercepted, waiting %s s \n Message was : %s",
                          self.Market.name,
                          str(timeout),
                          ElementClickInterceptedException.message)
                WebDriverWait(self.driver, timeout)
                LOG.warn("Refreshing page")
                self.driver.refresh()
                LOG.warn("trying button again")
                self.safely_click(item, wait_for, selector, timeout, attempt)

            except StaleElementReferenceException:
                attempt = attempt + 1
                # click unsuccesful waiting to refresh and try agin
                LOG.error("Failed to click on the button waiting %s s, refreshing page and trying again", str(timeout))
                WebDriverWait(self.driver, timeout)
                LOG.warn("Refreshing page")
                self.driver.refresh()
                LOG.warn("trying button again")
                self.safely_click(item, wait_for, selector, timeout, attempt)

            except NoSuchElementException:
                # click succesful but element to wait for is not found. refreshing page and ending.
                LOG.warn("Expected element not found, refreshing")
                WebDriverWait(timeout)
                self.driver.refresh()
            except TimeoutException:
                LOG.warn("%s did not load as expected", self.driver.current_url)
                return True
        return False

    def next_page(self, timeout):
        wait_for = self.Market.result_css
        try:
            next_button = self.driver.find_element_by_xpath(self.Market.next_page_xpath)
            LOG.debug("Have next button")
            self.safely_click(next_button, wait_for, By.CSS_SELECTOR, 120)
        except TimeoutException:
            LOG.error("Could not get next page of results: %s ", TimeoutException.message)
            WebDriverWait(timeout)
            self.driver.refresh()

    def load_queue(self):
        """
        creates an array of web elements to process
        :return:
        """
        try:
            self.queue = self.driver.find_elements_by_css_selector(self.Market.result_css)
        except Exception:
            LOG.error('Failed to load queue\n Message was: %s',Exception.message)
            return

    def get_result(self, result, timeout):
        """
        This clicks on a web element and gets raw car then exits back to the page it was once on.
        :param timeout:
        :param result:
        :return:
        """
        click = self.safely_click(result, self.Market.wait_for_car, By.CSS_SELECTOR, timeout, 0)
        if click:
            result = self.get_raw_car()
            self.safely_go_back(self.Market.result_css, By.CSS_SELECTOR, timeout)
            return result
        return False
