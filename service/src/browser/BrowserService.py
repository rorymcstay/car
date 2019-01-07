import os
import docker
from io import BytesIO
import logging as LOG

from docker.errors import APIError, ImageNotFound


class BrowserService:

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
                                             name=name + "_hub")
        except APIError, e:
            if e.status_code == 409:
                LOG.info('%s already has a hub. connecting' % name)
                hub = self.client.containers.get('%s_hub' % name)
                if hub.status != 'running':
                    try:
                        self.client.containers.run('%s_hub' % name, detach=True)
                    except:
                        LOG.error("Error starting %s_hub. Container was already created but is not likely the issue",
                                  name)
                        raise
            else:
                LOG.error("Error starting %s_hub", name)
                LOG.error("Docker error: %s", e.message)
                raise

        LOG.info("%s hub started", name)
        for line in hub.logs().split('\n'):
            if 'wd/hub' in line:
                hub.url = line.split(' ')[-1]

                # building browser image
        with open(self.browser) as image:
            dockerfile = BytesIO(image.read() % str(hub.name).encode('utf-8'))
            browser_image = self.client.images.build(fileobj=dockerfile, rm=True, tag='browser')
            # running browser image

            try:
                browser = self.client.containers.run(image=browser_image[0].id,
                                                     detach=True,
                                                     network=os.environ['APP_NAME'],
                                                     name=name + "_browser")
            except APIError, e:
                if e.status_code == 409:
                    LOG.info('%s already has a browser. connecting' % name)
                    browser = self.client.containers.get('%s_browser' % name)
                    if browser.status != 'running':
                        try:
                            self.client.containers.run(image=browser_image[0].id, detach=True)
                        except:
                            LOG.error(
                                "Error starting %s_browser. Container was already created but is not likely the issue",
                                name)
                            raise
                else:
                    LOG.error("Error starting %s_browser", name)
                    LOG.error("Docker error: %s", e.message)
                    raise
        LOG.info("Webcrawler has started a new browser and hub instance browser:%s, hub:%s", browser.name, hub.name)
        return hub


browser_service = BrowserService('%s/service/src/browser/Dockerfile.hub' % os.getcwd(),
                                 '%s/service/src/browser/Dockerfile.browser' % os.getcwd())
# browser = BrowserService('./Dockerfile.hub', './Dockerfile.browser')
