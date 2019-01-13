import json
import logging as LOG
import os
import traceback

from bs4 import BeautifulSoup
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


class ExcludedResultNotifier(Exception):
    pass

class PageOutOfRange(Exception):
    pass

class EndOfQueueNotification(Exception):
    pass

class PageLoadedError(Exception):
    pass

class WebCrawler:

    def __init__(self, market, remote=False):
        """
        :type remote: Container
        :type market: Market
        """
        LOG.getLogger('WebCrawler %s' % market.name)
        self.Market = market
        self.number_of_pages = None
        self.latest_page = self.Market.home
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
            url = market.browser
            LOG.debug("Starting remote driver for %s", market.name)
            options = Options()
            options.add_argument("--headless")
            self.driver = webdriver.Remote(command_executor=url,
                                           desired_capabilities=DesiredCapabilities.CHROME,
                                           options=options)

            # TODO Cant establish connection - parse loggs for connection
            # Connection timingi out
            LOG.info('Remote driver initiated for %s running on %s', self.Market.name, url)

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
        if self.driver.current_url == self.latest_page:
            return
        else:
            try:
                self.return_to_last_page()
            except NoSuchElementException:
                LOG.warn("Expected element not found, refreshing page in %s seconds", timeout)
                WebDriverWait(timeout)
                self.driver.refresh()
            except TimeoutException:
                if self.driver.current_url == u'data':
                    self.driver.get(self.latest_page)
                    return
                LOG.warn("Expected element not found, refreshing page in %s seconds")
                self.driver.refresh()
    #     check to see if were on a results page
        if self.driver.current_url is None:
            self.driver.forward()

    def safely_click(self, item, wait_for, selector, timeout, attempt=0):
        """
        identifies xpath and css path to button. Attempts
        This function handles cases where the click is intercepted or the webpage did not load as expected
        :param attempt:
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
                WebDriverWait(self.driver, int(os.environ['CLICK_TIMEOUT'])).until(element_present)
                return True

            except ElementClickInterceptedException:
                attempt = attempt + 1
                LOG.error("%s click on button was intercepted, waiting %s s \n Message was : %s",
                          self.Market.name,
                          str(timeout),
                          ElementClickInterceptedException.message)
                WebDriverWait(self.driver, timeout)
                LOG.warn("Refreshing page")
                self.driver.refresh()
                LOG.warn("trying button again")
                self.safely_click(item, wait_for, selector, timeout, attempt)
            except TimeoutException:
                LOG.warn("%s did not load as expected", self.driver.current_url)
                return True
        return False

    def next_page(self, timeout):
        try:
            wait_for = self.Market.result_css
            LOG.debug("Have next button")
            button = self.get_button(self.Market.next_page_xpath, self.driver.find_element_by_xpath)
            self.safely_click(button,
                              wait_for,
                              By.CSS_SELECTOR,
                              timeout)
            self.latest_page = self.driver.current_url
        except NoSuchElementException, e:
            LOG.error("Error going to the next page: \n  %s", e.message)
            traceback.print_exc()
            self.return_to_last_page()
            self.next_page(timeout)

    def get_queue_length(self):
        """
        creates an array of web elements to process
        :return:
        """
        try:
            queue = self.driver.find_elements_by_css_selector(self.Market.result_css)
        except Exception:
            LOG.error('Failed to find result items at %s: \n    %s', self.driver.current_url, Exception.message)
            return range(0)
        return range(len(queue))

    def get_queue_member(self, i, ignore, attempt=0):
        while attempt < int(os.environ['MAX_GET_RESULT_ATTEMPT']):
            attempt = attempt + 1
            if self.latest_page is not self.driver.current_url:
                self.return_to_last_page()
            try:
                queue = self.driver.find_elements_by_css_selector(self.Market.result_css)
                item = queue[i]
            except IndexError:
                raise EndOfQueueNotification()
            except NoSuchElementException, e:
                item = self.get_queue_member(i, ignore, attempt)
            if all(exclude not in item.text for exclude in ignore):
                return item
            else:
                raise ExcludedResultNotifier()
        LOG.error("Couldn't get queue member")
        raise NoSuchElementException

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

    def result_page(self):
        if all(chunk in self.driver.current_url for chunk in self.Market.home):
            return True
        else:
            return False

    def get_button(self, path, selector_method):
        return selector_method(path)

    def return_to_last_page(self):
        try:
            self.driver.get(self.latest_page)
            element_present = EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.Market.result_css))
            WebDriverWait(self.driver, int(os.environ['RETURN_TIMEOUT'])).until(element_present)
        except TimeoutException:
            LOG.warn("returning to latest page - %s did not load as expected or unusually slowly- Could not find %s"
                     % (self.driver.current_url, self.Market.result_css))
