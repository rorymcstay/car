import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor
import sys

"""
This module is a collection of functions for 
"""

def update_progress(job_title, progress):
    length = 20  # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
    if progress >= 1: msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()


def get_results(market, page_number, over_write=True):
    """
    This function collects the html source for a specified market place and number of pages

    :param market: The Market object
    :param page_number: The number of pages to get
    :param over_write: should the collected source overwrite what is within the market instance?
    :return: Updates market.latest_source list with html source with javascript compiled. It also
    updates the latest_urls.

    """
    if over_write is True:
        market.latest_source = []
    driver = market.driver
    cars = []

    driver.get(market.url_stub_1 + str(page_number * market.n_page) + market.url_stub_2)
    try:
        element_present = EC.presence_of_element_located((By.ID, market.wait_for))
        WebDriverWait(driver, 10).until(element_present)
        content = driver.page_source
        cars.extend(re.findall(r'' + market.result_stub + '[^\"]+', content))
    except TimeoutException:
        print("Failed to load result page - Check URL stubs and internet")
    market.latest_urls = list(set(cars))


    # Now getting source code
    print("Beginning source code extraction")
    missed_pages = 0
    j = 0
    for url in market.latest_urls:
        update_progress("loading Source", j/len(market.latest_urls))  # Progress bar
        driver.get(url)
        try:
            element_present = EC.presence_of_element_located((By.ID, market.wait_for_car))
            WebDriverWait(driver, 20).until(element_present)
            market.latest_source.append({'url': url, 'source': driver.page_source})
            print 'saved source'
        except TimeoutException:
            print("Timed out waiting for page to load")
            missed_cars = missed_pages+1
        j = j+1
    return


def get_cars(market):
    """
    This
    :param market:
    :return: stores raw car objects in market.cars
    """
    json_parse_miss = 0
    stashed=0
    j=0
    for i in market.latest_source:  # For each source html
        update_progress("Parsing JSON from source", j/len(market.latest_source))
        source_code = i.get('source')
        soup = BeautifulSoup(source_code, 'html.parser')
        for script in soup.find_all('script'):
            if market.json_identifier in script.text:
                try:
                    tree = JavascriptParser().parse(script.text)
                    obj = next(node.right for node in nodevisitor.visit(tree)
                               if (isinstance(node, ast.Assign) and
                                   node.left.to_ecma() == market.json_identifier))
                    data = json.loads(obj.to_ecma())
                    market.cars.append(data)
                    print ("Found " + market.json_identifier)
                    stashed=stashed+1
                except:
                    print("Failed to parse JSON")
                    json_parse_miss = json_parse_miss+1

            else:
                print("Not here, trying next script object")
        j=j+1
    print( "Succesfully found"+ str(stashed) + " cars out of" + str(len(market.latest_source)))
    return


def map_and_persist(market):
    """
    Converts raw car to generic car and puts in mongodb.

    :param market:
    :return:
    """
    for car in market.cars:
        try:
            market.mapping(car)
        except:
            print( "failed to parse car ")


