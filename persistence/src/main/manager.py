import logging

from psycopg2._psycopg import connection
import psycopg2
import requests as r
from settings import nanny_params, database_parameters
from src.main.mapper import Mapper


class MappingManager():
    client: connection = psycopg2.connect(**database_parameters)
    feeds = r.get("http://{host}:{port}/parametercontroller/getFeeds/".format(**nanny_params)).json()
    mapper = Mapper()

    def main(self):
        c = self.client.cursor()
        count = list(map(lambda name: c.execute(
            "select count(*) from t_stg_{}_results".format(name)
        ), self.feeds))
        for feed, _ in filter(lambda name: c.fetchone()[0] > 0, zip(self.feeds, count)):
            self.mapper.transform(feed)
            logging.info("mapped values for {}".format(feed))
