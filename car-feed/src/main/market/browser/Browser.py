import logging as log
from time import time, sleep

import docker
from docker.errors import APIError, ImageNotFound

from src.main.market.utils.BrowserConstants import BrowserConstants, get_open_port
from src.main.utils.LogGenerator import write_log, LogGenerator

LOG = LogGenerator(log, name='browser')


class Browser:

    def __init__(self, name, port, batch_number):
        """
        Begins a browser container
        :type name: string
        :param name: the name of the container
        :param batch_number: the batch it is inteded to process
        """

        self.batch_number = batch_number
        self.name = name

        self.client = docker.client.from_env()
        self.port = port
        try:
            self.browser = self.client.containers.run(BrowserConstants().browser_image,
                                                      detach=True,
                                                      name='browser-{}-{}-{}'.format(name, batch_number, self.port),
                                                      ports={'4444/tcp': self.port},
                                                      remove=True)
            write_log(LOG.info, msg='starting_browser', thread=self.batch_number)
        except ImageNotFound as e:
            write_log(LOG.error, thread=self.batch_number, msg="couldn't find image for hub", port=self.port, status_code=e.status_code, explanation=e.explanation)
            raise e
        except APIError as e:
            if e.status_code == 409:
                self.browser = self.client.containers.get('browser-{}-{}-{}'.format(self.name, batch_number, self.port))
                try:
                    self.browser.restart()
                    sleep(5)
                except:
                    write_log(LOG.error, thread=self.batch_number, msg="couldn't start browser image", port=self.port, status_code=e.status_code, exception=e.explanation)
                    return
            if e.status_code == 500:
                write_log(LOG.error, thread=self.batch_number, msg="docker server error running docker browser image", status_code=e.status_code,port=self.port)
                raise e
        self.wait_for_log(self.browser, BrowserConstants().CONTAINER_SUCCESS)

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
            write_log(LOG.warning,thread=self.batch_number, msg="Couldn't restart container. Killing it")
            try:
                self.port = get_open_port()
                self.browser.remove()
                self.__init__(self.name, self.port, self.batch_number)
            except APIError as e:
                write_log(LOG.warning, msg="couldn't remove container after failing to restart it", thread=self.batch_number, explanation=e.explanation)
    # TODO handle RemoteDisconnected

    def quit(self):
        try:
            self.browser.kill()
        except APIError as e:
            write_log(LOG.warning,msg="Couldn't quit container %s problem was: %s", thread=self.batch_number, explanation=e.explanation)
        try:
            self.browser.remove()
        except APIError as e:
            write_log(LOG.warning, msg="failed to remove container", thread=self.batch_number, explanation=e.explanation)

    def health_indicator(self):
        try:
            self.browser.reload()
        except APIError as e:
            if e.status_code == 404:
                return 'Removed'
        return self.browser.status
