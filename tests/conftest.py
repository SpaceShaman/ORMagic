import os

import pytest

from ormagic.clients.client import client_context


@pytest.fixture(
    params=[
        "sqlite://db.sqlite3",
        "postgresql://postgres:password@localhost/postgres",
    ]
)
def cursor(request):
    os.environ["ORMAGIC_DATABASE_URL"] = request.param
    with client_context() as client:
        yield client.create_connection().cursor()


@pytest.fixture(autouse=True)
def cleanup():
    yield
    database_url = os.getenv("ORMAGIC_DATABASE_URL", "sqlite://db.sqlite3")
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
    if database_url.startswith("postgresql"):
        with client_context() as client:
            client.execute("DROP SCHEMA public CASCADE")
            client.execute("CREATE SCHEMA public")
            client.commit()
