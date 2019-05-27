import logging as log
import re
import traceback
from http.client import RemoteDisconnected
from time import time, sleep

import bs4
import requests as r
import selenium.webdriver as webdriver
from bs4 import Tag
from selenium.common.exceptions import (TimeoutException,
                                        StaleElementReferenceException,
                                        WebDriverException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.exceptions import MaxRetryError, ProtocolError

from settings import routing_params, feed_params, browser_params, nanny_params
from src.main.exceptions import NextPageException
from src.main.market.utils.WebCrawlerConstants import WebCrawlerConstants

logging = log.getLogger(__name__)


class WebCrawler:
    driver: WebDriver

    def __init__(self, port=browser_params["port"]):
        """

        """
        port = r.get("http://{host}:{port}/{api_prefix}/getMainContainer/{submission_port}".format(**nanny_params,
                                                                                                   submission_port=port)).text
        self.number_of_pages = None
        self.last_result = None
        url = "http://{host}:{port}/wd/hub".format(host=browser_params["host"], port=port)
        logging.debug("Starting remote webdriver ")
        options = Options()
        options.add_argument("--headless")
        self.startWebdriverSession(url, options)
        self.port = port
        logging.info('remote driver initiated'.format(url))
        self.driver.set_window_size(1020, 900)
        self.history = []
        self.page = 1

    def startWebdriverSession(self, url, options, attempts=0):

        max_attempts = 10
        try:
            attempts += 1
            self.driver = webdriver.Remote(command_executor=url,
                                           desired_capabilities=DesiredCapabilities.CHROME,
                                           options=options)
        except (RemoteDisconnected, ProtocolError) as e:
            logging.warning(
                "failed to communicate with selenium, trying again for {} more times".format(max_attempts - attempts))
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
            logging.warning(
                msg="click failure - text: {button}, exception: {exception}".format(button=item.text, exception=e.msg))
            traceback.print_exc()
            return False
        except WebDriverException:
            traceback.print_exc()
            item = self.driver.find_element_by_css_selector(feed_params["next_page_css"])
            item.click()
            return False

    def resultPage(self):
        if all(chunk in self.driver.current_url for chunk in feed_params['base_url']):
            return True
        else:
            return False

    def latestPage(self):
        try:
            self.driver.get(self.last_result)
            element_present = EC.presence_of_all_elements_located((By.CSS_SELECTOR, feed_params['wait_for']))
            WebDriverWait(self.driver, 5).until(element_present)
            return True
        except TimeoutException:
            logging.warning("{} did not load as expected or unusually slowly at {}".format(feed_params['wait_for'],
                                                                                           self.driver.current_url))
            return True

    def nextPage(self, attempts=0):

        logging.info("attempt {}: going to next page from {}".format(attempts, self.driver.current_url))
        if not attempts > 0:
            r.put("http://{host}:{port}/{api_prefix}/updateHistory/{name}".format(name=feed_params["name"],
                                                                                  **routing_params),
                  data=self.driver.current_url)
            self.page += 1
        while attempts < WebCrawlerConstants().max_attempts:
            try:
                button = self.getNextButton()
                button.click()

                return
            except AttributeError:
                traceback.print_exc()
                attempts += 1
                self.nextPage(attempts)
                return
            except WebDriverException as e:
                raise NextPageException(self.page, e.msg)
        raise NextPageException(self.page, "maximum attempts reached")

    def getNextButton(self, attempts=0) -> WebElement:
        while attempts < WebCrawlerConstants().max_attempts:
            buttons = self.driver.find_elements_by_xpath(feed_params['next_page_xpath'])
            i = 0
            for button in buttons:
                i += 1
                text = button.text
                logging.debug("{} button text: {}".format(i, text))
                if feed_params['next_button_text'].upper() in text.upper():
                    return button

            # 1st fallback is to use css
            buttons = self.driver.find_elements_by_css_selector(feed_params.get("next_page_css"))
            logging.debug("getting next page by css")
            for button in buttons:
                text = button.text.upper()
                if feed_params.get("next_button_text").upper() in text:
                    return button

            # fallback 2, use beautiful soup and regex to find pagination bar
            logging.debug("getting next page using bs4")
            return self.driver.find_element_by_class_name(self.parseNextButton().attrs.get("class")[0])

    def parseNextButton(self) -> Tag:
        item: Tag = bs4.BeautifulSoup(self.driver.page_source,
                                      features='html.parser').find(attrs={"class": re.compile('.*(?i)pagination.*')})
        next = item.findAll(attrs={"class": re.compile('.*(?i)next.*')})
        for item in next:
            if feed_params['next_button_text'].upper() in item.text.upper():
                logging.info("found button {}".format(item.text))
                return item

    def getResultList(self):
        start = time()
        content = self.driver.page_source
        cars = []
        cars.extend(re.findall(r'' + feed_params['result_stub'] + '[^\"]+', content))
        logging.debug(
            "parsed result array of length {length} in {time} s".format(length=len(cars), time=time() - start))
        return list(set(cars))

    def retrace_steps(self, x):
        self.driver.get(feed_params['home'])
        WebDriverWait(self.driver, 2)
        page = 1
        while page < x:
            self.nextPage()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, feed_params['next_page_xpath'])))
            page = page + 1
            logging.info(page)

    def healthIndicator(self):
        try:
            return self.driver.current_url
        except (WebDriverException, Exception) as e:
            return 'Unhealthy'

    def quit(self):
        try:
            self.driver.quit()
        except MaxRetryError as e:
            logging.error("Tried to close browser when it was not running.")
