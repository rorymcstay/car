import requests as r
from psycopg2._psycopg import connection
import psycopg2
from settings import nanny_params, database_parameters


class Mapper():
    client: connection = psycopg2.connect(**database_parameters)
    client.autocommit = True
    feeds = r.get("http://{host}:{port}/parametercontroller/getFeeds".format(**nanny_params)).json()
    params = {}
    for name in feeds:

        req = r.get("http://{host}:{port}/mappingmanager/getMapping/{name}/v/{version}".format(name=name, version=1,
                                                                                              **nanny_params))
        if req.status_code < 404:
            params.update({name: req.json()})

    def transform(self, name):
        """

        :param name:
        :return:
        """
        mapping = self.params.get(name)
        fieldDefs = ",\n    ".join(list(map(lambda fieldname: "{} VARCHAR(256)".format(
            fieldname.get('final_column_name')), mapping.get('value'))))
        create = """
        create table if not exists t_fct_{}_results
        (
        source_url varchar(256) primary key,
        captured timestamp not null,
        {fields}
        )
        """.format(name, fields=fieldDefs)

        moveData = """
        insert into t_fct_{name}_results (source_url, captured, {columns}) 
        select url, added, {staging_columns} 
        from t_stg_{name}_results 
        """.format(name=name,
                   columns=", ".join([field.get("final_column_name") for field in mapping.get('value')]),
                   staging_columns=", ".join([field.get("staging_column_name") for field in mapping.get('value')]))

        c = self.client.cursor()
        c.execute(create)
        c.execute(moveData)

        c.execute("truncate table t_stg_{}_results".format(name))


