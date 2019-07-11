import os
from flask import Flask
from flask_cors import CORS

from src.main.search import Search

app = Flask(__name__)
CORS(app)
Search.register(app)
print(app.url_map)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("FLASK_PORT", 5004))
