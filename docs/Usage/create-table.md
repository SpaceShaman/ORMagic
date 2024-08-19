# Create Table

To create a table in the database, first create a class that inherits from `DBModel` and call the `create_table` method.

=== "Python"

    ```python
    from ormagic import DBModel

    class User(DBModel):
        name: str
        age: int

    User.create_table()
    ```

=== "SQL Result"

    ```sql
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL
    );
    ```
