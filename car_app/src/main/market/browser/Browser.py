from time import time
from docker.errors import APIError, ImageNotFound
from src.main.market.utils.BrowserConstants import BrowserConstants
import logging as LOG
import docker


class Browser:

    def __init__(self, name, batch_number):
        """
        Begins a browser container
        :type name: string
        :param name: the name of the container
        :param batch_number: the batch it is inteded to process
        """

        self.batch_number = batch_number
        self.name = name
        self.client = docker.client.from_env()
        self.port = BrowserConstants().base_port + batch_number
        try:
            self.browser = self.client.containers.run(BrowserConstants().browser_image,
                                                      detach=True,
                                                      name='browser-%s-%s' % (name, batch_number),
                                                      ports={'4444/tcp': self.port})
        except ImageNotFound as e:
            LOG.error("Couldn't find image for hub status: %s", e.explanation)
            raise e
        except APIError as e:
            if e.status_code == 409:
                self.browser = self.client.containers.get('browser-%s-%s' % (name, batch_number))
                try:
                    self.browser.restart()
                except:
                    LOG.error("Couldn't start browser image on port %s : %s \n  %s", str(self.port), e.status_code, e.explanation)
                    return
            if e.status_code == 500:
                LOG.error("Tried to start browser but couldn't Could be that the port %s", str(self.port))
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
        raise TimeoutError("Timed out waiting for %s to start on port %s" % (self.browser.short_id, str(self.port)))

    def restart(self):
        try:
            self.browser.restart()
            self.wait_for_log(self.browser, BrowserConstants().CONTAINER_SUCCESS)
        except APIError:
            LOG.warning("Couldn't restart container. Killing it")
            try:
                self.browser.remove()
                self.__init__(self.name, self.batch_number)
            except APIError as e:
                LOG.warning("Couldn't remove container %s after failing to restart it: %s", self.name, e.explanation)
    # TODO handle RemoteDisconnected
    def quit(self):
        try:
            self.browser.kill()
        except APIError as e:
            LOG.warning("Couldn't quit container %s problem was: %s", self.name, e.explanation)
        try:
            self.browser.remove()
        except APIError as e:
            LOG.warning("Failed to remove container %s problem was: %s", self.name, e.explanation)

    def health_indicator(self):
        try:
            self.browser.reload()
        except APIError as e:
            if e.status_code == 404:
                return 'Removed'
        return self.browser.status
