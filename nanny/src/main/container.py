import logging
from time import time

import docker
from docker.errors import APIError
from hazelcast import ClientConfig, HazelcastClient
from hazelcast.serialization.api import Portable
from hazelcast.serialization.portable.writer import ClassDefinitionWriter
from hazelcast.serialization.predicate import sql

from settings import browser_params, hazelcast_params, BrowserConstants


class Container(Portable):
    FACTORY_ID = 666
    CLASS_ID = 2

    def __init__(self, port=None, active="yes"):
        self.port = port
        self.active = active

    def write_portable(self, writer: ClassDefinitionWriter):
        """

        :type writer: ClassDefinitionWriter
        """
        writer.write_int("port", self.port)
        writer.write_utf("active", self.active)

    def read_portable(self, reader):
        self.active = reader.read_utf("active")
        self.port = reader.read_int("port")

    def get_factory_id(self):
        return self.FACTORY_ID

    def get_class_id(self):
        return self.CLASS_ID

    def __str__(self):
        return "Container {} is {}".format(self.port, "active" if self.port else "not active")

    def __eq__(self, other):
        return type(self) == type(other) and self.port == other.name and self.active == other.active



class ContainerManager:
    client = docker.client.from_env()
    config = ClientConfig()

    config.serialization_config.portable_factories[Container.FACTORY_ID] = \
        {Container.CLASS_ID: Container}

    config.network_config.addresses.append("{host}:{port}".format(**hazelcast_params))
    hz = HazelcastClient(config)

    def getContainer(self, port):

        # TODO handle: selenium.common.exceptions.WebDriverException: Message: unknown error: session deleted because of page crash

        portAssigned = self.assignPort(port)

        if portAssigned:
            port = portAssigned
            browser = self.client.containers.get('worker-{port}'.format(port=port))
            browser.reload()
            return str(port)
        try:
            browser = self.client.containers.run(self.client.images.get(browser_params['image']),
                                                 detach=True,
                                                 name='worker-{}'.format(port),
                                                 ports={'4444/tcp': port},
                                                 remove=True)
        except APIError as e:
            if e.status_code == 409:
                browser = self.client.containers.get('worker-{port}'.format(port=port))
                browser.reload()
            else:
                raise e
        logging.info(msg='starting_browser named worker-{port}'.format(port=port))
        self.wait_for_log(browser, BrowserConstants().CONTAINER_SUCCESS)
        return str(port)

    def freeContainer(self, port):
        workerPorts = self.hz.get_map("browser_containers")
        item = Container(port=port, active="no")
        workerPorts.replace(key=port, value=item)
        # TODO handle restarting container here - test that you can use a container after running for some time
        return "ok"

    def assignPort(self, port):
        workerPorts = self.hz.get_map("browser_containers")
        item = Container(port)
        unused = workerPorts.values(sql("active = 'no'")).result()
        if len(unused) == 0 or workerPorts.size().result() == 0:
            workerPorts.put(key=port, value=item)
            return False
        else:
            workerPorts.replace(key=unused[0].port, value=Container(port=unused[0].port, active="yes"))
            return unused[0].port

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
                    logging.debug(line)
                    return line.split(' ')[-1]

        # TODO handle RemoteDisconnected
        # TODO check for running containers before creation/worker to store running containers
