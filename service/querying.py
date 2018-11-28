import json
from flask import Flask, request
from car.src.persisting.mongoservice import MongoService
from car.src.persisting.queryconstructor import QueryConstructor

from car.service.headers import JSON

querying = Flask(__name__)

service = MongoService()


@querying.route("/cars")
def getAllCars():
    return json.dumps(service.queryToJSON({}))


@querying.route('/cars/')
@JSON
def filter():
    """
    :return: filters the cars collection by make, model and age
    """
    make = request.args.get('make', default='', type=str)
    model = request.args.get('model', default='', type=str)
    age = request.args.get('age', default='', type=int)
    values = [make, model, age]
    names = ['make', 'model', 'age']
    usedParams = []
    usedNames = []
    for name, value in zip(names, values):
        if value != '':
            usedParams.append(value)
            usedNames.append(name)
    query = QueryConstructor(usedParams, usedNames, 'carDetails').main()
    response = json.dumps(service.queryToJSON(query))
    return response

querying.run()