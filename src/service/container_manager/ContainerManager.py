import os

from flask_classy import FlaskView, route
from car.src.service.service import browser_service
from flask import request, Flask
import requests


class ContainerManager(FlaskView):

    @route('/add_market/<string:name>/<int:remote>/<string:make>/<string:model>', methods=['PUT'])
    def intialise_market_specific(self, name, make, model):
        remote = browser_service.new_service(name)
        market_definition = request.get_json()
        market_definition.remote = remote.url
        response = requests.post('http://%s:%s/add_market/%s/1/%s/%s/%s'
                                 % (name,
                                    os.environ["SERVICE_HOST"],
                                    os.environ['SERVICE_HOST'],
                                    name,
                                    make,
                                    model),
                                 json=market_definition)
        return response

    @route('/add_market/<string:name>', methods=['PUT'])
    def initialise_market(self, name):
        # headers = {
        #     "Content-Type": "application/json"
        # }
        browser = browser_service.new_service(name)
        market_definition = request.get_json()
        market_definition['remote'] = str(browser['url'])
        response = requests.put('http://%s:%s/command/add_market/%s/1' % (os.environ["SERVICE_HOST"],
                                                                          os.environ['SERVICE_PORT'],
                                                                          name),
                                # headers=headers,
                                json=market_definition)
        return 'ok'


app = Flask(__name__)
ContainerManager.register(app)
app.run(host='0.0.0.0', port='5000')
