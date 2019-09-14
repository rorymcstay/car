import json
import logging
from datetime import datetime

import hazelcast
import pandas as pd
import psycopg2
from hazelcast import ClientConfig, HazelcastClient
from hazelcast.core import HazelcastJsonValue
from psycopg2._psycopg import connection
from sqlalchemy import create_engine

from settings import hazelcast_params, database_parameters

config = hazelcast.ClientConfig()

config.network_config.addresses.append('127.0.0.1')
config.network_config.addresses.append('192.168.1.99')
config.network_config.addresses.append('localhost:5702')


class CacheManager:
    config = ClientConfig()
    config.network_config.addresses.append("{host}:{port}".format(**hazelcast_params))
    client = HazelcastClient(config)

    def insertResult(self, name, result, key):
        """
        request the next set of results

        :return:
        """

        map = self.client.get_map(name)
        map.put(key=key, value=HazelcastJsonValue(json.dumps(result)))

        logging.debug('inserted object result {}'.format(key))


class ObjectManager:
    client: connection = psycopg2.connect(**database_parameters)
    client.autocommit = True
    numberFields = {}
    batch_size = 100

    batches: pd.DataFrame = {}

    def _generateTable(self, name, number_fields):
        self.numberFields.update({name: number_fields})
        fields = map(lambda number: "field_{} VARCHAR(256)".format(number), range(number_fields))
        definition = """
        CREATE TABLE IF NOT EXISTS t_stg_{name}_results_{number_fields}(
            url VARCHAR(256) PRIMARY KEY,
            added TIMESTAMP NOT NULL,
            {fields}
        )
        """.format(fields=",\n      ".join(list(fields)), name=name, number_fields=number_fields)
        c = self.client.cursor()
        c.execute(definition)


    def prepareRow(self, name, row):
        if name not in self.batches.keys():
            self.batches.update({name: pd.DataFrame()})
        engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
        self.batches[name] = self.batches[name].append(row, ignore_index=True)
        try:
            if len(self.batches[name]) > self.batch_size:
                self.batches[name] = self.batches[name].set_index(['url'])
                self.batches[name]['added'] = datetime.now()
                self.batches[name].to_sql('t_stg_{}_results'.format(name), con=engine, if_exists='append')
                self.batches[name] = pd.DataFrame()
        except Exception as e:
            self.batches[name] = pd.DataFrame()
            logging.warning("failed row {}", e.args)
            pass
