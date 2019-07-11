import logging
import os

from flask import Flask

from src.main.feedmanager import FeedManager
from src.main.rest import ContainerController, ParameterController
from flask_cors import CORS

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.FileHandler('/var/tmp/myapp.log')


app = Flask(__name__)
CORS(app)
ContainerController.register(app)
ParameterController.register(app)
FeedManager.register(app)

if __name__ == '__main__':
    print(app.url_map)
    app.run(port=os.getenv("FLASK_HOST"), host="0.0.0.0")
