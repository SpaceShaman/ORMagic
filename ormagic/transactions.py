import sqlite3


class transaction:
    _is_transaction = False
    _connection = None
    _cursor = None

    @classmethod
    def __enter__(cls):
        cls._is_transaction = True
        cls._connection = sqlite3.connect("db.sqlite3", isolation_level=None)
        cls._connection.execute("PRAGMA foreign_keys = ON")
        cls._connection.execute("PRAGMA journal_mode = WAL")
        cls._cursor = cls._connection.cursor()
        cls._cursor.execute("BEGIN")

    @classmethod
    def __exit__(cls, exc_type, exc_value, traceback):
        cls._is_transaction = False
        if exc_type is None:
            cls._connection.commit()
        else:
            cls._connection.rollback()
        cls._connection.close()
