import json
from flask_classy import FlaskView
from hazelcast import HazelcastClient, ClientConfig
from flask import request, Response
from hazelcast.serialization.predicate import sql

from settings import hazelcast_params


class Search(FlaskView):

    config = ClientConfig()
    config.network_config.addresses.append("{host}:{port}".format(**hazelcast_params))
    hz = HazelcastClient(config)

    def getResultSummaries(self, feedName, searchField, searchValue):
        map = self.hz.get_map('{}-results'.format(feedName))
        pred = sql("{} like %{}%".format(searchField, searchValue))
        values = map.values(pred).result()
        payload = []
        for value in values:
            payload.append(value.loads())
        return Response(json.dumps(payload), "application/json")

