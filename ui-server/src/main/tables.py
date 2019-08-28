import json

import psycopg2 as psycopg2
from flask import Response, request
from flask_classy import FlaskView, route
from psycopg2._psycopg import connection, cursor

from settings import database_parameters


class TableManager(FlaskView):
    client: connection = psycopg2.connect(**database_parameters)
    client.autocommit = True
    numberFields = {}

    def getTableNames(self, feedName):

        query = """
        select table_name from information_schema.tables 
        where table_name like '%{}%'""".format(feedName)

        c: cursor = self.client.cursor()
        c.execute(query)
        results = [name[0] for name in c.fetchall()]
        return Response(json.dumps(results), mimetype='application/json')

    def getAllColumns(self, tableName):
        query = """
        SELECT column_name
        FROM information_schema.columns
        where table_name = '{}';
        """.format(tableName)
        c: cursor = self.client.cursor()
        c.execute(query)
        results = [{"name": name[0], "accessor": name[0]} for name in c.fetchall()]
        return Response(json.dumps(results), mimetype='application/json')

    @route('/getResults/<int:page>/<int:pageSize>', methods=['PUT', 'GET'])
    def getResults(self, page, pageSize):
        req = request.get_json()
        query = "select {columns} from {tableName} {predicates} limit {} offset {}".format(page, pageSize, **req)
        c: cursor = self.client.cursor()
        c.execute(query)
        data = list(map(lambda row: {c.description[i].name: row[i] for i in range(len(c.description))}, c.fetchall()))
        columns = [{"Header": column.name, "accessor": column.name} for column in c.description]
        response = {"data": data, "columns": columns}
        return Response(json.dumps(response))
