from .connection import Connection, create_connection


class transaction:
    _is_transaction = False
    _connection: Connection

    @classmethod
    def __enter__(cls):
        cls._is_transaction = True
        cls._connection = create_connection()
        cls._connection.execute("BEGIN")

    @classmethod
    def __exit__(cls, exc_type, exc_value, traceback):
        cls._is_transaction = False
        if exc_type:
            cls._connection.rollback()
        else:
            cls._connection.commit()
        cls._connection.close()
