from unittest import TestCase
from src.main.service.rest.Command import Command

from flask import Flask

app = Flask(__name__)
Command.register(app)


class TestCommand(TestCase):

    def test_hello(self):
        """When a list of arguments is passed to"""


    def test_initialise(self):
        self.fail()
