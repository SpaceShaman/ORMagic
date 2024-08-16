# Unique constraints

To define a unique constraint, use the `unique` parameter set to `True` in the Pydantic field.

=== "Python"
    ```python
    from ormagic import DBModel, DBField

    class User(DBModel):
        name: str
        email: str = DBField(unique=True)
    ```
=== "SQL Result"
    ```sql
    CREATE TABLE user (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    );
    ```

## One to one relationships

You can also use the `unique` parameter to define one to one relationships between tables.

=== "Python"
    ```python
    from ormagic import DBModel, DBField

    class User(DBModel):
        name: str

    class UserProfile(DBModel):
        user: User = DBField(unique=True)
        bio: str
    ```
=== "SQL Result"
    ```sql
    CREATE TABLE user (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );
    CREATE TABLE user_profile (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE NOT NULL,
        bio TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user (id)
    );
    ```
