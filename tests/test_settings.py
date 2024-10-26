import os
from sqlite3 import Connection

from ormagic.connection import create_connection


def test_setup_for_sqlite():
    os.environ["ORMAGIC_DATABASE"] = "sqlite://test.db"

    connection = create_connection()
    connection.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")

    assert isinstance(connection, Connection)
    assert os.path.exists("test.db")
    connection.close()
    os.remove("test.db")
