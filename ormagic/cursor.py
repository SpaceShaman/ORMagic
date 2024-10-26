from contextlib import contextmanager
from typing import Generator

from .connection import Cursor, create_connection
from .transactions import transaction


@contextmanager
def get_cursor() -> Generator[Cursor, None, None]:
    if transaction._is_transaction:
        yield transaction._connection.cursor()
    else:
        connection = create_connection()
        try:
            yield connection.cursor()
        finally:
            connection.close()
