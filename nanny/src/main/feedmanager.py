import json
import os

from flask import Response
from flask_classy import FlaskView
import pymongo
from pymongo.database import Database

from settings import mongo_params


class FeedManager(FlaskView):

    client = pymongo.MongoClient(**mongo_params)
    forms: Database = client[os.getenv("FORM_DATABASE", "forms")]
    feeds: Database = client[os.getenv("PARAMETER_DATABASE", "params")]
    parameterSchemas = forms['parameterSchemas']

    def getParameterTypes(self):
        c = self.parameterSchemas.find({})
        data = json.dumps([param.get("name") for param in c])
        return Response(json.dumps(data), mimetype="application/json")

    def getParameterSchema(self, parameterName):
        parameter = self.parameterSchemas.find_one({"name": parameterName})
        val = parameter['value']
        return Response(json.dumps(val), mimetype="application/json")

    def getFeeds(self):
        c = self.feeds["feed"].find({})
        data = [param.get("name") for param in c]
        return Response(json.dumps(data), mimetype="application/json")
