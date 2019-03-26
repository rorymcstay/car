import logging

from flask import Flask

from src.main.service.rest.Command import Command

logging.basicConfig(level=logging.INFO)
logging.FileHandler('/var/tmp/myapp.log')

app = Flask(__name__)
Command.register(app)

if __name__ == '__main__':
    print(app.url_map)
    app.run()
