import logging
import os
from time import time

import docker
from docker.errors import APIError
from docker.models.containers import Container as Browser
from hazelcast import ClientConfig, HazelcastClient
from hazelcast.proxy.map import Map
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
        return "Container {} is {}".format(self.port, "active" if self.active.upper() == "yes".upper() else "not active")

    def __eq__(self, other):
        return type(self) == type(other) and self.port == other.name and self.active == other.active


class ContainerManager:
    container_map=os.getenv("CONTAINER_MAP_NAME", "browser_containers")
    ports = [{"port": 4444 + i, "active": 'no'} for i in range(browser_params["max"])]
    client = docker.client.from_env()
    config = ClientConfig()
    config.serialization_config.portable_factories[Container.FACTORY_ID] = \
        {Container.CLASS_ID: Container}
    config.network_config.addresses.append("{host}:{port}".format(**hazelcast_params))
    hz = HazelcastClient(config)

    for port in ports:
        try:
            client.containers.run(client.images.get(browser_params['image']),
                                  detach=True,
                                  name='worker-{}'.format(port["port"]),
                                  ports={'4444/tcp': port["port"]},
                                  remove=True)
            logging.info("started container {}".format(port["port"]))
            hz.get_map(container_map).put(key=port["port"], value=Container(port=port["port"], active="no"))

        except APIError as e:
            if e.status_code == 409:
                client.containers.get('worker-{}'.format(port["port"]))
                hz.get_map(container_map).put(key=port["port"], value=Container(port=port["port"], active="no"))
                logging.info("reconnected with container {}".format(port["port"]))

    def resetCache(self):
        map = self.hz.get_map(self.container_map)
        map.evict_all()
        for port in self.ports:
            map.put(key=port["port"], value=Container(port=port["port"], active='no')).result()
        return 'ok'

    @property
    def getContainer(self):

        workerPorts = self.hz.get_map(self.container_map)
        unused = workerPorts.values(sql("active = 'no'")).result()
        if len(unused) == 0:
            return "max containers reached"

        else:
            workerPorts.replace(key=unused[0].port, value=Container(port=unused[0].port, active="yes")).result()
            port = unused[0].port
            try:
                browser: Browser = self.client.containers.get('worker-{port}'.format(port=port))
                browser.restart()
            except APIError as e:
                if e.status_code == 404:
                    browser = self.client.containers.run(self.client.images.get(browser_params['image']),
                                                         detach=True,
                                                         name='worker-{}'.format(port),
                                                         ports={'4444/tcp': port})
                else:
                    raise e
            logging.info(msg='starting_browser named worker-{port}'.format(port=port))
            self.wait_for_log(browser, BrowserConstants().CONTAINER_SUCCESS)
            return str(port)

    def getContainerStatus(self):
        map: Map = self.hz.get_map(self.container_map)
        items = map.get_all(keys=[port["port"] for port in self.ports]).result()
        return [str(items[item]) for item in items]

    def freeContainer(self, port):
        workerPorts = self.hz.get_map(self.container_map)
        item = Container(port=port, active="no")
        workerPorts.replace(key=port, value=item)
        browser: Browser = self.client.containers.get('worker-{port}'.format(port=port))
        browser.restart()

        # TODO handle restarting container here - test that you can use a container after running for some time
        return "ok"

    def cleanUpContainers(self):
        workerPorts = self.hz.get_map(self.container_map)
        inactive = workerPorts.values(sql("active = 'no'")).result()
        for container in inactive:
            try:
                res = self.client.containers.get("worker-{}".format(container.port))
                res.kill()
                res.remove()
                logging.info("killed container {}".format(res))
            except APIError as e:
                if e.status_code == 404:
                    logging.info("container not found, moving on")
            workerPorts.replace(key=container.port, value=Container(container.port, "no"))
        return "ok"

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