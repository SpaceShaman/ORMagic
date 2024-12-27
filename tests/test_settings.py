import os

import pytest

from ormagic.clients.client import DatabaseNotSupported, client_context, get_client
from ormagic.settings import SettingsError


def test_setup_for_sqlite():
    os.environ["ORMAGIC_DATABASE_URL"] = "sqlite://test.db"

    with client_context() as client:
        client.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")

    assert os.path.exists("test.db")
    os.remove("test.db")


def test_setup_for_not_supported_database():
    os.environ["ORMAGIC_DATABASE_URL"] = "not_supported://test.db"

    with pytest.raises(DatabaseNotSupported):
        get_client()


def test_setup_with_invalid_database_url():
    os.environ["ORMAGIC_DATABASE_URL"] = "invalid_url"

    with pytest.raises(SettingsError):
        get_client()


def test_setup_for_sqlite_with_custom_journal_mode():
    os.environ["ORMAGIC_DATABASE_URL"] = "sqlite://test.db"
    os.environ["ORMAGIC_JOURNAL_MODE"] = "DELETE"

    with client_context() as client:
        result = client.fetchone("PRAGMA journal_mode")
    os.remove("test.db")

    assert result[0] == "delete"
