import json
import logging as LOG
import os
import re
from time import time, sleep
import traceback
import selenium.webdriver as webdriver
from selenium.common.exceptions import (TimeoutException,
                                        StaleElementReferenceException,
                                        NoSuchElementException, WebDriverException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup

from src.main.market.crawling.Exceptions import (ExcludedResultNotifier,
                                                 EndOfQueueNotification,
                                                 QueueServicingError,
                                                 ResultCollectionFailure,
                                                 MaxAttemptsReached)


class WebCrawler:

    def __init__(self, market, remote=False):
        """
        :type remote: Container
        :type market: Market
        """
        LOG.getLogger('WebCrawler %s' % market.name)
        self.Market = market
        self.number_of_pages = None
        self.last_result = self.Market.home
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
            url = remote
            LOG.debug("Starting remote driver for %s", market.name)
            options = Options()
            options.add_argument("--headless")
            self.driver = webdriver.Remote(command_executor=url,
                                           desired_capabilities=DesiredCapabilities.CHROME,
                                           options=options)

            LOG.info('Remote driver initiated for %s running on %s', self.Market.name, url)
        self.driver.set_window_size(1120, 900)
        self.history = []

    def get_raw_car(self, source=None):
        """
        attempts to get car from current page source, returns to the previous set of results in which it came
        :return:
        """
        if source is not None:
            source = source
        else:
            source = self.driver.page_source
        soup = BeautifulSoup(source, 'html.parser')

        out = []
        try:
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
                ResultCollectionFailure(self.driver.current_url, "Nothing found here")
                LOG.error("Could not find json_identifier = %s at %s",
                          self.Market.json_identifier,
                          self.driver.current_url)
                return False
        except Exception as e:
            raise ResultCollectionFailure(self.driver.current_url, None, e)
        return out

    def safely_click(self, item, wait_for, selector, timeout=3):
        """
        identifies xpath and css path to button. Attempts
        This function handles cases where the click is intercepted or the webpage did not load as expected
        :param selector:
        :param wait_for:
        :param item:
        :return:
        """

        try:
            item.click()
            element_present = EC.presence_of_all_elements_located((selector, wait_for))
            WebDriverWait(self.driver, timeout).until(element_present)
            return True
        except TimeoutException:
            LOG.warning("%s did not load as expected", self.driver.current_url)
            self.driver.get(self.Market.home)
            sleep(1)
        except StaleElementReferenceException as e:
            LOG.warning("couldn't click on %s: \n  %s", item.text, e.msg)
            traceback.print_exc()
            raise e
        except WebDriverException:
            return False

    def get_queue_range(self):
        """
        creates an array of web elements to process
        :return:
        """
        try:
            queue = self.driver.find_elements_by_css_selector(self.Market.result_css)
        except NoSuchElementException as e:
            LOG.error('Failed to find result items at %s: \n    %s', self.driver.current_url, e.msg)
            raise QueueServicingError(url=self.driver.current_url,
                                      reason="NoSuchElementException",
                                      exception=e,
                                      attempt="Queue length")
        return range(len(queue))

    def get_queue_member(self, i, ignore, attempt=0):
        if attempt < int(os.environ['MAX_GET_RESULT_ATTEMPT']):
            if self.result_page():
                try:
                    queue = self.driver.find_elements_by_css_selector(self.Market.result_css)
                    item = queue[i]
                    if all(exclude not in item.text for exclude in ignore):
                        return item
                    else:
                        raise ExcludedResultNotifier()
                except IndexError as e:
                    raise EndOfQueueNotification(i, e, attempt)
                except NoSuchElementException as e:
                    self.latest_page()
                    raise QueueServicingError(attempt=attempt,
                                              url=self.driver.current_url,
                                              reason="get_queue_member returned false",
                                              exception=e)
            else:
                LOG.error("Queue member called outside of context")
                raise QueueServicingError(attempt=attempt,
                                          url=self.driver.current_url,
                                          reason="Queue member called outside of context",
                                          exception="result_page() was false")
        else:
            raise QueueServicingError(attempt=attempt,
                                      url=self.driver.current_url,
                                      reason="Reached Maximum attempts",
                                      exception=None)

    def get_result(self, result):
        """
        This clicks on a web element and gets raw car then exits back to the page it was once on.
        :param result:
        :return:
        """
        click = self.safely_click(result, self.Market.wait_for_car, By.CSS_SELECTOR)
        if click:
            try:
                result = self.get_raw_car()
                url = self.driver.current_url
                return {'result': result, 'url': url}
            except ResultCollectionFailure as e:
                raise e
        else:
            raise ResultCollectionFailure(self.driver.current_url, "Error clicking on result", "click returned false")

    def result_page(self):
        if all(chunk in self.driver.current_url for chunk in self.Market.home):
            return True
        else:
            return False

    def latest_page(self):
        try:
            self.driver.get(self.last_result)
            element_present = EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.Market.result_css))
            WebDriverWait(self.driver, 5).until(element_present)
            return True
        except TimeoutException:
            LOG.warning("returning to latest page - %s did not load as expected or unusually slowly- Could not find %s",
                     self.driver.current_url, self.Market.result_css)
            return True

    def next_page(self, attempts=0):
        if attempts < int(os.environ['MAX_CLICK_ATTEMPTS']) and self.result_page():
            try:
                button = self.get_next_button()
            except NoSuchElementException as e:
                attempts = attempts + 1
                sleep(attempts)
                LOG.error("Could not find next button %s", e.msg)
                self.next_page(attempts)
                return
            except StaleElementReferenceException as e:
                attempts = attempts + 1
                sleep(attempts)
                LOG.error("Could not find next button %s", e.msg)
                self.next_page(attempts)
                return
            try:
                self.safely_click(button, self.Market.next_page_xpath, By.XPATH, 30)
            except StaleElementReferenceException as e:
                attempts = attempts + 1
                sleep(attempts)
                LOG.error("Could not find next button %s", e.msg)
                self.next_page(attempts)
            return
        else:
            raise MaxAttemptsReached()

    def get_next_button(self):
        buttons = self.driver.find_elements_by_xpath(self.Market.next_page_xpath)
        for button in buttons:
            if button.text.upper() == self.Market.next_button_text.upper():
                return button

    def update_latest_page(self, wait):
        wait = time() + wait
        origin_called = self.last_result
        while time() < wait:
            self.last_result = None
            if origin_called == self.driver.current_url:
                pass
            self.last_result = self.driver.current_url
            return
        self.last_result = origin_called
        self.history.append(origin_called)

    def get_result_array(self):
        content = self.driver.page_source
        cars = []
        cars.extend(re.findall(r'' + self.Market.result_stub + '[^\"]+', content))
        return cars

    def retrace_steps(self, x):
        self.driver.get(self.Market.home)
        WebDriverWait(self.driver, 2)
        page = 1
        while page < x:
            self.next_page()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.Market.next_page_xpath)))
            page = page + 1
            LOG.info(page)

    def health_indicator(self):
        return self.driver.current_url



