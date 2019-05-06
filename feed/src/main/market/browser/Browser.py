import logging as log
import traceback
from http.client import RemoteDisconnected
from time import time

import docker
import requests
from docker.errors import APIError, ImageNotFound
from docker.models.containers import Container

from settings import browser_params, routing_params, market_params
from src.main.market.utils.BrowserConstants import BrowserConstants, getOpenPort
from src.main.utils.LogGenerator import write_log, LogGenerator

LOG = LogGenerator(log, name='browser')


class Browser:

    browser: Container
    client = docker.client.from_env()

    def __init__(self, port=browser_params['port']):
        # TODO handle: selenium.common.exceptions.WebDriverException: Message: unknown error: session deleted because of page crash
        self.port = port
        portAssigned = requests.put("http://{host}:{port}/{api_prefix}/assignNewPort/{port}".format(port=self.port,
                                                                                                    **routing_params,
                                                                                                    **market_params))
        if portAssigned.text.isdigit():
            self.port = portAssigned.text
            self.browser = self.client.containers.get('worker-{port}'.format(port=self.port))
            self.browser.restart()
            self.wait_for_log(self.browser, BrowserConstants().CONTAINER_QUIT)
            self.wait_for_log(self.browser, BrowserConstants().CONTAINER_SUCCESS)

        try:
            self.browser = self.client.containers.run(self.client.images.get(browser_params['image']),
                                                      detach=True,
                                                      name='worker-{}'.format(self.port),
                                                      ports={'4444/tcp': self.port},
                                                      remove=True)
            write_log(LOG.info, msg='starting_browser', thread="worker-{port}".format(port=self.port))
            self.wait_for_log(self.browser, BrowserConstants().CONTAINER_SUCCESS)

        except ImageNotFound as e:
            write_log(LOG.error, thread="worker-{port}".format(port=self.port), msg="couldn't find image for hub", port=self.port, status_code=e.status_code, explanation=e.explanation)
            raise e
        except APIError as e:
            if e.status_code == 500:
                write_log(LOG.error, thread="worker-{port}".format(port=self.port), msg="docker server error running docker browser image", status_code=e.status_code,port=self.port)
                raise e
            else:
                write_log(log.error, thread="worker-{port}".format(port=self.port), msg='Browser container not reachable')
                raise e

        except RemoteDisconnected as e:
            write_log(log.error, thread="worker-{port}".format(port=self.port), msg='Browser container not reachable')
            self.wait_for_log(self.browser, BrowserConstants().CONTAINER_SUCCESS)

        except Exception as e:
            traceback.print_exc()
            write_log(thread="worker-{port}".format(port=self.port), msg="unknown exception occured")

    def wait_for_log(self, hub, partial_url):
        """
        Wait until the partial_url returns in the logs
        :type hub: docker.client.containers
        :param hub:
        :param partial_url:
        :return:
        """
        timeMax = time() + BrowserConstants().CONTAINER_TIMEOUT
        while time() < timeMax:
            for line in hub.logs().decode().split('\n'):
                if partial_url in line:
                    LOG.debug(line)
                    return line.split(' ')[-1]
        write_log(LOG.warning, msg="container_start_timeout", id=self.browser.short_id, port=self.port)

    def restart(self):
        try:
            self.browser.restart()
            self.wait_for_log(self.browser, BrowserConstants().CONTAINER_SUCCESS)
        except APIError:
            write_log(LOG.warning,thread="worker-{port}".format(port=self.port), msg="Couldn't restart container. Killing it")
            try:
                self.port = getOpenPort()
                self.browser.remove()
                self = self.__init__(self.port)
            except APIError as e:
                write_log(LOG.warning, msg="couldn't remove container after failing to restart it", thread="worker-{port}".format(port=self.port), explanation=e.explanation)


    # TODO handle RemoteDisconnected
    # TODO check for running containers before creation/worker to store running containers

    def quit(self):
        """Destroy the container"""
        try:
            self.browser.kill()
        except APIError as e:
            write_log(LOG.warning,msg="Couldn't quit container %s problem was: %s", thread="worker-{port}".format(port=self.port), explanation=e.explanation)
        try:
            self.browser.remove()
        except APIError as e:
            write_log(LOG.warning, msg="failed to remove container", thread="worker-{port}".format(port=self.port), explanation=e.explanation)

    def health_indicator(self):
        """
        get the status of the container

        :return:
        """
        try:
            self.browser.reload()
        except APIError as e:
            if e.status_code == 404:
                return 'Removed'
        return self.browser.status
