import os
import time

import docker
from io import BytesIO
import logging as LOG
from urlparse import urlparse

from docker.errors import APIError


class Browser:

    def __init__(self, hub_file, browser_file):
        self.port = os.environ["HUB_PORT"]
        self.browser = browser_file
        self.client = docker.from_env()
        with open(hub_file) as image:
            self.hub_image = self.client.images.build(fileobj=image, tag='hub')

    def new_service(self, name):
        # running a hub
        try:
            hub = self.client.containers.run(image=self.hub_image[0].id,
                                             detach=True,
                                             network=os.environ['APP_NAME'],
                                             name=name + "hub")
        except APIError, e:
            if e.status_code == 409:
                LOG.info('%s already has a hub. connecting' % name)
                hub = self.client.containers.get('%shub' % name)
                if hub.status != 'running':
                    try:
                        hub = self.client.containers.run(str(hub.name).lower(), detach=True)
                    except:
                        LOG.error("Error starting %s_hub. Container was already created but is not likely the issue",
                                  name)
                        raise
            else:
                LOG.error("Error starting %s_hub", name)
                LOG.error("Docker error: %s", e.message)
                raise

        LOG.info("%s hub started", name)

        url = self.get_hub_host(hub)
        if url is None:
            time.sleep(60)
            url = self.get_hub_host(hub)

        # building browser image
        with open(self.browser) as image:

            dockerfile = BytesIO(image.read() % urlparse(url).hostname)
            browser_image = self.client.images.build(fileobj=dockerfile, rm=True, tag='browser')

            # running browser image
            try:
                browser = self.client.containers.run(image=browser_image[0].id,
                                                     detach=True,
                                                     network=os.environ['APP_NAME'],
                                                     name=name + "browser")
            except APIError, e:
                if e.status_code == 409:
                    LOG.info('%s already has a browser. connecting' % name)
                    browser = self.client.containers.get('%sbrowser' % name)
                    if browser.status != 'running':
                        try:
                            self.client.containers.run(image=browser_image[0].id, detach=True)
                        except:
                            LOG.error(
                                "Error starting %s_browser. Container was already created but is not likely the issue",
                                name)
                            raise
                else:
                    LOG.error("Error starting %sbrowser", name)
                    LOG.error("Docker error: %s", e.message)
                    raise
        LOG.info("Webcrawler has started a browser instance:%s", browser.name)
        return {'hub': hub, 'browser': browser, 'url': url}

    def get_hub_host(self, hub):
        for line in hub.logs().split('\n'):
            if 'wd/hub' in line:
                LOG.info(line)
                return line.split(' ')[-1]
        return None


print os.getcwd()

# browser = BrowserService('/car/service/src/browser/.hub', '/car/service/src/browser/.browser')
