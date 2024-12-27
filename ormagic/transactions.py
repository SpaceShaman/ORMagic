from .clients.client import Client, get_client


class transaction:
    _is_transaction = False
    _client: Client

    @classmethod
    def __enter__(cls):
        cls._is_transaction = True
        cls._client = get_client()
        cls._client.create_connection()
        cls._client.execute("BEGIN")

    @classmethod
    def __exit__(cls, exc_type, exc_value, traceback):
        cls._is_transaction = False
        if exc_type:
            cls._client.rollback()
        else:
            cls._client.commit()
        cls._client.close()
