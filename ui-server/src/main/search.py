import json

import pymongo
from flask_classy import FlaskView, route
from hazelcast import HazelcastClient, ClientConfig
from flask import request, Response
from hazelcast.serialization.predicate import sql
from hazelcast.serialization import predicate as preds

from settings import hazelcast_params, mongo_params


class Search(FlaskView):
    config = ClientConfig()
    config.network_config.addresses.append("{host}:{port}".format(**hazelcast_params))
    hz = HazelcastClient(config)
    mongoClient = pymongo.MongoClient(**mongo_params)
    querySchemas = mongoClient['search']['schema']

    @route('/getResults/<string:feedName>', methods=['PUT', 'GET'])
    def getResults(self, feedName):
        query = request.get_json()
        map = self.hz.get_map('{}-{}'.format(feedName, query.get("kind")))
        predicate = sql(query.get("value"))
        values = map.values(predicate).result()

        payload = []
        for value in values:
            payload.append(value.loads())
        if payload:
            return Response(json.dumps(payload), mimetype="application/json")
        else:
            return Response("not found", status=404)

    def getQuerySchema(self, querySchema):
        schema = self.querySchemas.find_one({"name": querySchema})
        val = schema['value']
        return Response(json.dumps(val), mimetype="application/json")

    def getSchemaList(self):
        schemas = self.querySchemas.find({})
        names = [{
            "key": schema.get("name"),
            "value": schema.get("name"),
            "text": schema.get("name")
        } for schema in schemas]
        return Response(json.dumps(names), mimetype='application/json')
