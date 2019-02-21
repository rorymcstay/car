import os

import requests
from flask import request, Flask
from flask_classy import FlaskView, route


class ContainerManager(FlaskView):

    @route('/add_market/<string:name>/<int:remote>/<string:make>/<string:model>', methods=['PUT'])
    def intialise_market_specific(self, name, make, model):
        market_definition = request.get_json()
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
        market_definition = request.get_json()
        response = requests.put('http://%s:%s/command/add_market/%s/1' % (os.environ["SERVICE_HOST"],
                                                                          os.environ['SERVICE_PORT'],
                                                                          name),
                                # headers=headers,
                                json=market_definition)
        return 'ok'


app = Flask(__name__)
ContainerManager.register(app)
app.run(host='0.0.0.0', port='5001')
