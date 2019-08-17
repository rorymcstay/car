import logging
import os
from flask import Flask
from flask_cors import CORS

from src.main.feedmanager import FeedManager
from src.main.scheduler import ScheduleManager
from src.main.search import Search

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

Search.register(app)
FeedManager.register(app)
ScheduleManager.register(app)

print(app.url_map)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("FLASK_PORT", 5004))
