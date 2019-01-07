from unittest import TestCase
from car.service.src.rest.Command import Command
from car.market.src.marketplaces import donedeal


class TestCommand(TestCase):
    def setUp(self):
        self.Command = Command(donedeal)
        Command.app.testing = True
        self.app = Command.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()

    def test_hello(self):
        """When a list of arguments is passed to"""

        Command(donedeal)

    def test_initialise(self):
        self.fail()
