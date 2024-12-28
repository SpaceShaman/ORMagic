import os

import pytest

from ormagic.clients.client import client_context


@pytest.fixture
def cursor():
    with client_context() as client:
        yield client.create_connection().cursor()


@pytest.fixture(autouse=True)
def remove_db():
    os.environ["ORMAGIC_DATABASE_URL"] = "sqlite://db.sqlite3"
    yield
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
