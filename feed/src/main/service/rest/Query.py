import json

import yaml
from bson import json_util
from flask import request, Blueprint, json
from flask_classy import FlaskView, route

from src.main.service.mongo_service.MongoService import MongoService
from src.main.service.rest.flask_helper.headers import JSON

query = Blueprint('query', __name__,)
service = MongoService('0.0.0.0:27017')


class Query(FlaskView):
    @route('/cars/')
    @JSON
    def json_query(self):
        req = yaml.safe_load(json.dumps(request.get_json()))
        x = service.cars.find(req['query'], req['projection'])
        return json_util.dumps(x, default=json_util.default)

    @route('/get_result_list/<string:name>', methods=['GET'])
    def getResultList(self, name):
        results = marketSet[name].getListOfResults()
        return json.dumps(results)

    @route('/get_results/<string:name>', methods=['GET'])
    def getResults(self, name):
        """
        return current page of results

        :param name:
        :return:
        """
        returnString = marketSet[name].getResults()
        marketSet[name].webCrawler.next_page()
        return json.dumps(returnString, cls=Encoder)


