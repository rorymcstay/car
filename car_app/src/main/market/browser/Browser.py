import os
from time import sleep

from io import BytesIO
import logging as LOG
from urllib.parse import urlparse
from docker import DockerClient

from docker.errors import APIError


class Browser:

    def __init__(self, hub_file, browser_file):
        self.port = os.environ["HUB_PORT"]
        self.browser = browser_file
        self.client = DockerClient(base_url='unix://var/run/docker.sock')
        with open(hub_file, 'rb') as image:
            self.hub_image = self.client.images.build(fileobj=image, tag='hub')

    def new_service(self, name):
        # running a hub
        try:
            hub = self.client.containers.run(image=self.hub_image[0].id,
                                             detach=True,
                                             network=os.environ['APP_NAME'],
                                             name=name + "hub")
        except APIError as e:
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
                LOG.error("Docker error: %s", e.msg)
                raise

        LOG.info("%s hub started", name)

        url = self.get_hub_host(hub)
        if url is None:
            sleep(60)
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
            except APIError as e:
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
                    LOG.error("Docker error: %s", e.msg)
                    raise
        LOG.info("Webcrawler has started a browser instance:%s", browser.name)
        return {'hub': hub, 'browser': browser, 'url': url}

    def get_hub_host(self, hub):
        for line in hub.logs().split('\n'):
            if 'wd/hub' in line:
                LOG.info(line)
                return line.split(' ')[-1]
        return None

    def get_browser(self):
        self.hub = self.client.containers.create(self.client.images.get('hub'))
        self.client.run(self.hub, detach=True)
        self.get_hub_host()
        while
        self.hub = self.client.containers.create(self.client.images.get('browser'))


# browser = BrowserService('/car/service/src/browser/.hub', '/car/service/src/browser/.browser')
