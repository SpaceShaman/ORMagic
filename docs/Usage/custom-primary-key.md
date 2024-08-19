# Custom primary key

By default, `ORMagic` will create a primary key column named `id` for each model.
However, you can specify a custom primary key by setting the `primary_key` attribute on the model field to `True`.

=== "Python"
    ```python
    from ormagic import DBModel, DBField

    class User(DBModel):
        custom_id: int | None = DBField(primary_key=True)
        name: str

    User.create_table()
    ```

=== "SQL Result"
    ```sql
    CREATE TABLE IF NOT EXISTS user (
        custom_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );
    ```
