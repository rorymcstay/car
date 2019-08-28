import json
import logging
import os
import signal
import socket
import traceback
from http.client import RemoteDisconnected
from time import time, sleep

import bs4
import requests
import selenium.webdriver as webdriver
from kafka import KafkaProducer, KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.exceptions import ProtocolError, MaxRetryError

from settings import kafka_params, nanny_params, browser_params


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


def getOpenPort():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


class Worker:
    producer = KafkaProducer(**kafka_params)
    consumer: KafkaConsumer = KafkaConsumer(**kafka_params, value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    port = None

    def __init__(self):
        """
        Worker class has a browser container and selenium driver which it uses to collect cars in a seperate thread.

        :param batch_number:
        :param market:
        :param remote:
        """

        port = requests.get("http://{host}:{port}/{api_prefix}/getContainer".format(**nanny_params)).text
        if browser_params['host'] is None:
            url = "http://worker-{port}:{base}/wd/hub".format(port=port, base=browser_params["base_port"])
        else:
            url = "http://{}:{}/wd/hub".format(browser_params['host'], port)
        logging.debug("Starting remote webdriver")
        options = Options()
        options.add_argument("--headless")
        self.driver = self.startWebdriverSession(url, options, port)

    def startWebdriverSession(self, url, options, port, attempts=0):

        max_attempts = 10
        attempts += 1
        try:

            self.driver = webdriver.Remote(command_executor=url,
                                           desired_capabilities=DesiredCapabilities.CHROME,
                                           options=options)

        except (RemoteDisconnected, ProtocolError, MaxRetryError) as e:
            logging.warning(
                "failed to communicate with selenium, trying again for {} more times".format(max_attempts - attempts))
            if attempts < max_attempts:
                self.startWebdriverSession(url, options, port, attempts)
                sleep(3)
            else:
                requests.get("http://{host}:{port}/{api_prefix}/freeContainer/{}".format(port, **nanny_params))
                sleep(3)
                port = requests.get(
                    "http://{host}:{port}/{api_prefix}/getContainer".format(**nanny_params,
                                                                                                  submission_port=port)).text
                self.startWebdriverSession(url, options, port)
        except MaxRetryError as e:
            logging.warning(
                "failed to communicate with selenium, trying again for {} more times".format(max_attempts - attempts))
            if attempts < max_attempts:
                self.startWebdriverSession(url, options, port, attempts)
                sleep(3)
            else:
                requests.get("http://{host}:{port}/{api_prefix}/freeContainer/{}".format(port, **nanny_params))
                sleep(3)
                port = requests.get(
                    "http://{host}:{port}/{api_prefix}/getContainer/".format(**nanny_params)).text
                self.startWebdriverSession(url, options, port)
        logging.info("started webdriver session")

    def publishObject(self, url, streamName):
        """
        Updates a list provided called out. Intended to be used in a different thread in conjunction with multiple
        workers

        :param results: the batch or urls
        """
        r = requests.get("http://{host}:{port}/parametercontroller/getParameter/worker/{name}".format(**nanny_params,
                                                                                                    name=streamName))
        stream = r.json()
        webTime = time()
        self.driver.get(url)
        logging.info(msg="{url} loaded in: {time_elapsed} s".format(url=self.driver.current_url,
                                                                    time_elapsed=time() - webTime))
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, stream['page_ready']))
        WebDriverWait(self.driver, int(os.getenv("WORKER_TIMEOUT"))).until(element_present)
        parser = bs4.BeautifulSoup(self.driver.page_source, features="html.parser")
        if stream.get("single"):
            if stream.get("class") is None:
                message = bytes(self.driver.page_source, "utf-8")
            else:
                message = bytes(str(parser.find(attrs={"class": stream.get("class")})), 'utf-8')
            self.producer.send(topic="{name}-items".format(name=streamName),
                               value=message,
                               key=bytes(self.driver.current_url, 'utf-8'))
            logging.info("published result to kafka")
        else:
            items = parser.findAll(attrs={"class": stream.get("class")})
            i = 0
            for item in items:
                i += 1
                payload = dict(value=bytes(str(item), 'utf-8'),
                               key=bytes("{}_{}".format(self.driver.current_url, i), 'utf-8'))
                self.producer.send(topic="{name}-items".format(name=streamName), **payload)
            logging.info("published result to kafka")

    def main(self):
        killer = GracefulKiller()
        self.consumer.subscribe(["worker-queue"])
        try:
            while 1:
                item: ConsumerRecord
                for item in self.consumer:
                    self.publishObject(url=item.value["url"], streamName=item.value["type"])
                    if killer.kill_now:
                        requests.get(
                            "http://{host}:{port}/{api_prefix}/freeContainer/{close_port}".format(close_port=self.port, **nanny_params))
                        self.consumer.close()
        except Exception as e:
            traceback.print_exc()
            requests.get("http://{host}:{port}/{api_prefix}/freeContainer/{close_port}".format(close_port=self.port, **nanny_params))