import os
from sqlite3 import Connection

import pytest

from ormagic.connection import DatabaseNotSupported, create_connection
from ormagic.settings import SettingsError


def test_setup_for_sqlite():
    os.environ["ORMAGIC_DATABASE_URL"] = "sqlite://test.db"

    connection = create_connection()
    connection.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")

    assert isinstance(connection, Connection)
    assert os.path.exists("test.db")
    connection.close()
    os.remove("test.db")


def test_setup_for_not_supported_database():
    os.environ["ORMAGIC_DATABASE_URL"] = "not_supported://test.db"

    with pytest.raises(DatabaseNotSupported):
        create_connection()


def test_setup_with_invalid_database_url():
    os.environ["ORMAGIC_DATABASE_URL"] = "invalid_url"

    with pytest.raises(SettingsError):
        create_connection()


def test_setup_for_sqlite_with_custom_journal_mode():
    os.environ["ORMAGIC_DATABASE_URL"] = "sqlite://test.db"
    os.environ["ORMAGIC_JOURNAL_MODE"] = "DELETE"

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("PRAGMA journal_mode")
    result = cursor.fetchone()

    connection.close()
    os.remove("test.db")

    assert result[0] == "delete"
