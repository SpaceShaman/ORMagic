class transaction:
    _is_transaction = False

    @classmethod
    def __enter__(cls):
        cls._is_transaction = True

    @classmethod
    def __exit__(cls, exc_type, exc_value, traceback):
        cls._is_transaction = False
