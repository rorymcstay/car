import logging
import os

from flask import Flask

from src.main.rest import RoutingController

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.FileHandler('/var/tmp/myapp.log')




app = Flask(__name__)
RoutingController.register(app)

if __name__ == '__main__':
    print(app.url_map)
    app.run(port=os.getenv("FLASK_PORT", 5002), host="0.0.0.0")
