from sqlite3 import Connection, connect


def create_connection() -> Connection:
    connection = connect("db.sqlite3", isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection
