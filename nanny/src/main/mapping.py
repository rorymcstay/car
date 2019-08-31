import json

from flask import request, Response
from flask_classy import FlaskView, route
import pymongo
from settings import mongo_params

class MappingManager(FlaskView):
    mongoClient = pymongo.MongoClient(**mongo_params)
    mappings = mongoClient['mappings']

    def getMapping(self, name, version):
        mapping = self.mappings[name].find_one({'version': version})

        return Response(json.dumps(mapping), mimetype='application/json')

    def setMapping(self, name):
        mapping = request.get_json('mapping')
