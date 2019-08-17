import logging
import os

from flask import Flask

from src.main.rest import ContainerController, ParameterController
from flask_cors import CORS

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.FileHandler('/var/tmp/myapp.log')


app = Flask(__name__)
ContainerController.register(app)
ParameterController.register(app)
CORS(app)

if __name__ == '__main__':
    print(app.url_map)
    app.run(port=os.getenv("FLASK_HOST", 5000), host="0.0.0.0")