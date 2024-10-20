from contextlib import contextmanager
from sqlite3 import Cursor
from typing import Any, Generator

from ormagic.connection import create_connection
from ormagic.transactions import transaction


@contextmanager
def get_cursor() -> Generator[Cursor, Any, None]:
    if transaction._is_transaction:
        yield transaction._connection.cursor()
    else:
        connection = create_connection()
        try:
            yield connection.cursor()
        finally:
            connection.close()
