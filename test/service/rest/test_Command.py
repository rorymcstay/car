import os
import unittest
from unittest import TestCase
from car.src.service.rest import Command
from car.test.resources.donedeal_market import market as donedeal_market
from car.src.service.rest.Command import Command

from flask import request, Flask

app = Flask(__name__)
Command.register(app)


class TestCommand(TestCase):

    def test_hello(self):
        """When a list of arguments is passed to"""


    def test_initialise(self):
        self.fail()
