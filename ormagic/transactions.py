from ormagic import DBModel


class transaction:
    def __enter__(self):
        DBModel._is_transaction = True

    def __exit__(self, exc_type, exc_value, traceback):
        DBModel._is_transaction = False
