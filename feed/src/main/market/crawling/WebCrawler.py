import logging as log
import re
import traceback
from http.client import RemoteDisconnected
from time import time, sleep

import requests as r
import selenium.webdriver as webdriver
from selenium.common.exceptions import (TimeoutException,
                                        StaleElementReferenceException,
                                        NoSuchElementException, WebDriverException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.exceptions import MaxRetryError, ProtocolError

from settings import routing_params, market_params, browser_params, nanny_params
from src.main.market.crawling.Exceptions import MaxAttemptsReached
from src.main.market.utils.WebCrawlerConstants import WebCrawlerConstants
from src.main.utils.LogGenerator import LogGenerator, write_log

LOGGER.setLevel(log.WARNING)
LOG = LogGenerator(log, name='webcrawler')


class WebCrawler:

    def __init__(self, port=browser_params["port"]):
        """

        """
        port = r.get("http://{host}:{port}/{api_prefix}/getContainer/{submission_port}".format(**nanny_params, submission_port=port)).text
        self.number_of_pages = None
        self.last_result = None
        url = "http://{host}:{port}/wd/hub".format(host=browser_params["host"], port=port)
        LOG.debug("Starting remote webdriver ")
        options = Options()
        options.add_argument("--headless")
        self.startWebdriverSession(url, options)
        write_log(LOG.info, msg='remote driver initiated', webdriver_host=url)
        self.driver.set_window_size(1120, 900)
        self.history = []

    def startWebdriverSession(self, url, options, attempts=0):
        max_attempts=10
        try:
            attempts += 1
            self.driver = webdriver.Remote(command_executor=url,
                                           desired_capabilities=DesiredCapabilities.CHROME,
                                           options=options)
        except (RemoteDisconnected, ProtocolError) as e:
            write_log(LOG.warning, msg="failed to communicate with selenium, trying again for {} more times".format(max_attempts-attempts))
            if attempts < max_attempts:
                sleep(3)
                self.startWebdriverSession(url, options, attempts)
            else:
                raise e

    def safelyClick(self, item, wait_for, selector, timeout=3):
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

    def resultPage(self):
        if all(chunk in self.driver.current_url for chunk in market_params['home']):
            return True
        else:
            return False

    def latestPage(self):
        try:
            self.driver.get(self.last_result)
            element_present = EC.presence_of_all_elements_located((By.CSS_SELECTOR, market_params['result_css']))
            WebDriverWait(self.driver, 5).until(element_present)
            return True
        except TimeoutException:
            write_log(LOG.warning, msg="{} did not load as expected or unusually slowly".format(market_params['result_css']), url=self.driver.current_url)
            return True

    def nextPage(self, attempts=0):
        if attempts < WebCrawlerConstants().max_attempts and self.resultPage():
            try:
                button = self.getNextButton()
            except NoSuchElementException as e:
                attempts = attempts + 1
                sleep(attempts)
                LOG.warning("Could not find next button %s", e.msg)
                self.nextPage(attempts)
                return
            except StaleElementReferenceException as e:
                attempts = attempts + 1
                sleep(attempts)
                LOG.warning("Could not find next button %s", e.msg)
                self.nextPage(attempts)
                return
            try:
                self.safelyClick(button, market_params['next_page_xpath'], By.XPATH, 30)
            except StaleElementReferenceException as e:
                attempts = attempts + 1
                sleep(attempts)
                LOG.error("Could not click on next button %s", e.msg)
                self.nextPage(attempts)
            except TimeoutException:
                LOG.warning("Next page did not load as expected")
            r.put("http://{host}:{port}/{api_prefix}/updateHistory/{name}".format(name=market_params["name"], **routing_params), data=self.driver.current_url)
            return
        else:
            raise MaxAttemptsReached()

    def getNextButton(self):
        buttons = self.driver.find_elements_by_xpath(market_params['next_page_xpath'])
        for button in buttons:
            if button.text.upper() == market_params['next_button_text'].upper():
                return button

    def getResultList(self):
        start = time()
        content = self.driver.page_source
        cars = []
        cars.extend(re.findall(r'' + market_params['result_stub'] + '[^\"]+', content))
        write_log(LOG.debug, msg="parsed_result_array", length=len(cars), time=time()-start)
        return list(set(cars))

    def retrace_steps(self, x):
        self.driver.get(market_params['home'])
        WebDriverWait(self.driver, 2)
        page = 1
        while page < x:
            self.nextPage()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, market_params['next_page_xpath'])))
            page = page + 1
            LOG.info(page)

    def healthIndicator(self):
        try:
            return self.driver.current_url
        except (WebDriverException, Exception) as e:
            return 'Unhealthy'

    def quit(self):
        try:
            self.driver.quit()
        except MaxRetryError as e:
            LOG.error("Tried to close browser when it was not running.")




