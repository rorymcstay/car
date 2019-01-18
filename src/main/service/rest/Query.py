import json
import yaml

from bson import json_util
from flask import request, Blueprint, json
from flask_classy import FlaskView, route
from car.src.main.service import QueryConstructor
from car.src.main.service import JSON
from car.src.main.market import MongoService

query = Blueprint('query', __name__,)
service = MongoService()

class Query(FlaskView):

    @route("/cars")
    def get_all_cars(self):
        return json.dumps(service.query({}))

    def filter(self):
        """
        :return: filters the cars collection by make, model and age
        """
        make = request.args.get('make', default='', type=str)
        model = request.args.get('model', default='', type=str)
        age = request.args.get('age', default='', type=int)
        values = [make, model, age]
        names = ['make', 'model', 'age']
        used_params = []
        used_names = []
        for name, value in zip(names, values):
            if value != '':
                used_params.append(value)
                used_names.append(name)
        query = QueryConstructor(used_params, used_names, 'carDetails').main()
        response = json.dumps(service.query(query))
        return response

    @route('/cars/')
    @JSON
    def json_query(self):
        req = yaml.safe_load(json.dumps(request.get_json()))
        x = service.cars.find(req['query'], req['projection'])
        return json_util.dumps(x)


