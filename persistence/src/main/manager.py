import logging

from psycopg2._psycopg import connection
import psycopg2
import requests as r
from settings import nanny_params, database_parameters
from src.main.mapper import Mapper


class MappingManager():
    client: connection = psycopg2.connect(**database_parameters)
    feeds = r.get("http://{host}:{port}/parametercontroller/getFeeds".format(**nanny_params))
    mapper = Mapper()

    def main(self):
        c = self.client.cursor()
        count = list(map(lambda name: {count: c.execute(
            "select count(*) from t_stg_{}_results".format(name)
        ).fetch_one()[0], 'name': name}, self.feeds))
        for table in filter(lambda item: item.get('count'), count):
            self.mapper.transform(table.get("name"))
            logging.info("mapped {} values for {}".format(table.get('count'), table.get('name')))
