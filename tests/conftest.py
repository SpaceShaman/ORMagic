import os
import sqlite3

import pytest


def remove_db():
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")


@pytest.fixture
def db_cursor():
    remove_db()
    con = sqlite3.connect("db.sqlite3")  # type: ignore
    yield con.cursor()
    con.close()
    remove_db()
