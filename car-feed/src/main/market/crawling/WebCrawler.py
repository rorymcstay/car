import json
import logging as log
import re
import traceback
from http.client import RemoteDisconnected
from time import time, sleep

import selenium.webdriver as webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import (TimeoutException,
                                        StaleElementReferenceException,
                                        NoSuchElementException, WebDriverException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor
from urllib3.exceptions import MaxRetryError, ProtocolError

from src.main.market.crawling.Exceptions import (ExcludedResultNotifier,
                                                 EndOfQueueNotification,
                                                 QueueServicingError,
                                                 ResultCollectionFailure,
                                                 MaxAttemptsReached)
from src.main.market.utils.WebCrawlerConstants import WebCrawlerConstants
from src.main.utils.LogGenerator import LogGenerator, write_log

LOG = LogGenerator(log, name='webcrawler')


class WebCrawler:

    def __init__(self, market, remote=False):
        """
        :type remote: Container
        :type market: Market
        """
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
            write_log(LOG.info, msg='local driver initiated', name=self.Market.name)
        else:
            url = remote
            LOG.debug("Starting remote driver for %s", market.name)
            options = Options()
            options.add_argument("--headless")
            self.startWebdriverSession(url, options)
            write_log(LOG.info,msg='remote driver initiated', webdriver_host=url)
        self.driver.set_window_size(1120, 900)
        self.history = []

    def startWebdriverSession(self, url, options, attempts=0):
        try:
            attempts += 1
            self.driver = webdriver.Remote(command_executor=url,
                                           desired_capabilities=DesiredCapabilities.CHROME,
                                           options=options)
        except (RemoteDisconnected, ProtocolError) as e:
            write_log(LOG.warning, msg="failed to communicate with selenium")
            if attempts < 10:
                sleep(3)
                self.startWebdriverSession(url, options, attempts)
            else:
                raise e


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
                    write_log(LOG.debug,msg='found raw car', url=self.driver.current_url)
                    out.append(raw_car)
            if len(out) == 0:
                ResultCollectionFailure(self.driver.current_url, "Nothing found here", exception=None)
                write_log(LOG.debug, msg='could not find raw car', url=self.driver.current_url)
                return False
        except Exception as e:
            traceback.print_exc()
            error = ResultCollectionFailure(self.driver.current_url, None, e)
            raise error
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
        except StaleElementReferenceException as e:
            write_log(LOG.warning, msg="click failure", button=item.text, exception=e.msg)
            traceback.print_exc()
            return False
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
            write_log(LOG.error,msg='failed to find results', url=self.driver.current_url, exception=e.msg)
            raise QueueServicingError(url=self.driver.current_url,
                                      reason="NoSuchElementException",
                                      exception=e,
                                      attempt="Queue length")
        return range(len(queue))

    def get_queue_member(self, i, ignore, attempt=0):
        if attempt < WebCrawlerConstants().max_attempts:
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
            write_log(LOG.warning, msg="{} did not load as expected or unusually slowly".format(self.Market.result_css), url=self.driver.current_url)
            return True

    def next_page(self, attempts=0):
        if attempts < WebCrawlerConstants().max_attempts and self.result_page():
            try:
                button = self.get_next_button()
            except NoSuchElementException as e:
                attempts = attempts + 1
                sleep(attempts)
                LOG.warning("Could not find next button %s", e.msg)
                self.next_page(attempts)
                return
            except StaleElementReferenceException as e:
                attempts = attempts + 1
                sleep(attempts)
                LOG.warning("Could not find next button %s", e.msg)
                self.next_page(attempts)
                return
            try:
                self.safely_click(button, self.Market.next_page_xpath, By.XPATH, 30)
            except StaleElementReferenceException as e:
                attempts = attempts + 1
                sleep(attempts)
                LOG.error("Could not click on next button %s", e.msg)
                self.next_page(attempts)
            except TimeoutException:
                LOG.warning("Next page did not load as expected")
            self.update_latest_page()
            return
        else:
            raise MaxAttemptsReached()

    def get_next_button(self):
        buttons = self.driver.find_elements_by_xpath(self.Market.next_page_xpath)
        for button in buttons:
            if button.text.upper() == self.Market.next_button_text.upper():
                return button

    def update_latest_page(self):
        """Updates the latest pages and stores it in the WebCrawler.last_result field and updates history"""
        self.last_result = self.driver.current_url
        self.history.append(self.last_result)

    def get_result_array(self):
        start = time()
        content = self.driver.page_source
        cars = []
        cars.extend(re.findall(r'' + self.Market.result_stub + '[^\"]+', content))
        write_log(LOG.debug, msg="parsed_result_array", length=len(cars), time=time()-start)
        return list(set(cars))

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
        try:
            return self.driver.current_url
        except (WebDriverException, Exception) as e:
            return 'Unhealthy'

    def quit(self):
        try:
            self.driver.quit()
        except MaxRetryError as e:
            LOG.error("Tried to close browser when it was not running.")




