import os
from sqlite3 import Connection

import pytest

from ormagic.connection import DatabaseNotSupported, create_connection


def test_setup_for_sqlite():
    os.environ["ORMAGIC_DATABASE"] = "sqlite://test.db"

    connection = create_connection()
    connection.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")

    assert isinstance(connection, Connection)
    assert os.path.exists("test.db")
    connection.close()
    os.remove("test.db")


def test_setup_for_not_supported_database():
    os.environ["ORMAGIC_DATABASE"] = "not_supported://test.db"

    with pytest.raises(DatabaseNotSupported):
        create_connection()
