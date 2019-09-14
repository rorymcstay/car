import json

from flask import request, Response
from flask_classy import FlaskView, route
import pymongo
from settings import mongo_params


class MappingManager(FlaskView):
    mongoClient = pymongo.MongoClient(**mongo_params)
    mappings = mongoClient['mapping']

    @route("/getMapping/<string:name>/v/<int:version>")
    def getMapping(self, name, version):
        mapping = self.mappings['values'].find_one({'name': name})
        if mapping is None:
            return Response(status=404)
        mapping.pop('_id')
        return Response(json.dumps(mapping), mimetype='application/json')
