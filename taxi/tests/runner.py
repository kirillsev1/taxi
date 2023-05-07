from django.test.runner import DiscoverRunner
from django.db import connections
from types import MethodType


def prepare_db(self):
    self.connect()
    self.connection.cursor().execute('CREATE EXTENSION IF NOT EXISTS postgis;')


class PostgresSchemaRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        for conn_name in connections:
            conn = connections[conn_name]
            conn.ops.postgis = True
            conn.prepare_database = MethodType(prepare_db, conn)
        return super().setup_databases(**kwargs)
