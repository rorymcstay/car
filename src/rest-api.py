import json
from functools import wraps

from flask import Flask, request, make_response
from Persisting.MongoService import MongoService
from Persisting.QueryConstructor import QueryConstructor

app = Flask(__name__)

datasource = MongoService()


def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


def JSON(f):
    """This decorator passes Content-Type: application/json header"""
    @wraps(f)
    @add_response_headers({'Content-Type': 'application/json'})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


@app.route("/hello")
def hello():
    return "Hello World!"


@app.route("/cars")
def getAllCars():
    return json.dumps(datasource.queryToJSON({}))


@app.route('/cars/')
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
    response = json.dumps(datasource.queryToJSON(query))
    return response


app.run()
