import os
import docker
from io import BytesIO
import logging as LOG


class BrowserService:

    def __init__(self, hub_file, browser_file):
        self.port = os.environ["HUB_PORT"]
        self.browser = browser_file
        self.client = docker.from_env()
        with open(hub_file) as image:
            self.hub_image = self.client.images.build(fileobj=image, tag='hub')

    def new_service(self, name):
        # running a hub
        hub = self.client.containers.run(image=self.hub_image[0].id,
                                         detach=True,
                                         network=os.environ['APP_NAME'],
                                         name=name+"_hub")
        LOG.info("%s hub started", name)
        # building browser image
        with open(self.browser) as image:
            dockerfile = BytesIO(image.read() % str(hub.name).encode('utf-8'))
            browser_image = self.client.images.build(fileobj=dockerfile, rm=True, tag='browser')
            # running browser image
            browser = self.client.containers.run(image=browser_image[0].id,
                                                 detach=True,
                                                 network=os.environ['APP_NAME'],
                                                 name=name+"_browser")

        LOG.info("Webcrawler has started a new browser and hub instance browser:%s, hub:%s", browser.name, hub.name)
        return hub

browser_service = BrowserService('%s/service/src/browser/Dockerfile.hub' % os.getcwd(), '%s/service/src/browser/Dockerfile.browser' % os.getcwd())

