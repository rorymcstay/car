import logging
import traceback

from flask import Flask

from src.main.service.rest.Command import Command
from src.main.service.rest.Query import Query

logging.basicConfig(level=logging.DEBUG)
logging.FileHandler('/var/tmp/myapp.log')

app = Flask(__name__)
Command.register(app)
Query.register(app)

@app.errorhandler(500)
def internal_error(exception):
    print("500 error caught")
    print(traceback.format_exc())
    return traceback.format_exc()

print(app.url_mapew)

app.run()
