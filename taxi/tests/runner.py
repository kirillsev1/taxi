"""Runner for setting up db."""
from types import MethodType
from typing import Callable

from django.db import connections
from django.test.runner import DiscoverRunner


def prepare_db(self):
    """
    Prepare the database by executing a command to create the 'postgis' extension if it doesn't exist.

    Args:
        self: The instance of the class.
    """
    self.connect()
    self.connection.cursor().execute('CREATE EXTENSION IF NOT EXISTS postgis;')


class PostgresSchemaRunner(DiscoverRunner):
    """Custom test runner for PostgreSQL databases with PostGIS extension support."""

    def setup_databases(self, **kwargs) -> Callable:
        """
        Setup_databases method to enable the PostGIS extension.

        Args:
            kwargs: Keys and values for setting up the database.

        Returns:
            Callable: The result of the base class's setup_databases method.
        """
        for _, conn_name in enumerate(connections):
            conn = connections[conn_name]
            conn.ops.postgis = True
            conn.prepare_database = MethodType(prepare_db, conn)
        return super().setup_databases(**kwargs)
