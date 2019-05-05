import logging
import os

from flask import Flask

from src.main.rest import RoutingController

logging.basicConfig(level=logging.INFO)
logging.FileHandler('/var/tmp/routing.log')

app = Flask(__name__)
RoutingController.register(app)

if __name__ == '__main__':
    print(app.url_map)
    app.run(port=os.getenv("PORT"), host=os.getenv("HOST"))
