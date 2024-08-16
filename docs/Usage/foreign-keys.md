# Define foreign keys

To define a foreign key, use other models as fields in the model.
By default, the foreign key will be set to `CASCADE`, but you can change it by setting the `on_delete` parameter of the pydantic field to one of the following values: `CASCADE`, `SET NULL`, `RESTRICT`, `SET DEFAULT`, `NO ACTION`.

## Create tables with foreign keys

=== "Python"
    ```python
    from ormagic import DBModel

    class User(DBModel):
        name: str

    class Post(DBModel):
        title: str
        content: str
        user: User # Define a foreign key with default on_delete=CASCADE

    User.create_table()
    Post.create_table()
    ```
=== "SQL Result"
    ```sql
    CREATE TABLE user (
        id INTEGER PRIMARY KEY
    );
    CREATE TABLE post (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        user INTEGER NOT NULL,
        FOREIGN KEY (user) REFERENCES user (id) ON DELETE CASCADE
    );
    ```

## Save data with foreign keys

=== "Python"
    ```python
    user = User(name="John")
    user.save()

    Post(title="Hello", content="World", user=user).save()
    ```
=== "SQL Result"
    ```sql
    INSERT INTO user (name) VALUES ('John');
    INSERT INTO post (title, content, user) VALUES ('Hello', 'World', 1);
    ```

You can also save child models with new parent object in one step, this will save the parent object first and then the child object

=== "Python"
    ```python
    Post(title="Hello", content="World", user=User(name="Alice")).save()
    ```
=== "SQL Result"
    ```sql
    INSERT INTO user (name) VALUES ('Alice');
    INSERT INTO post (title, content, user) VALUES ('Hello', 'World', 2);
    ```

## Define foreign key with custom on_delete

To define a foreign key with a custom `on_delete` behavior, set the `on_delete` parameter of the `DBField` to one of the following values: `CASCADE`, `SET NULL`, `RESTRICT`, `SET DEFAULT`, `NO ACTION`.

=== "CASCADE"
    ```python
    from ormagic import DBModel, DBField

    class User(DBModel):
        name: str

    class Post(DBModel):
        title: str
        content: str
        user: User = DBField(on_delete="CASCADE")

    User.create_table()
    Post.create_table()
    ```
=== "RESTRICT"
    ```python
    from ormagic import DBModel, DBField

    class User(DBModel):
        name: str

    class Post(DBModel):
        title: str
        content: str
        user: User = DBField(on_delete="RESTRICT")

    User.create_table()
    Post.create_table()
    ```
=== "NO ACTION"
    ```python
    from ormagic import DBModel, DBField

    class User(DBModel):
        name: str

    class Post(DBModel):
        title: str
        content: str
        user: User = DBField(on_delete="NO ACTION")

    User.create_table()
    Post.create_table()
    ```
=== "SET DEFAULT"
    ```python
    from ormagic import DBModel, DBField

    class User(DBModel):
        name: str

    class Post(DBModel):
        title: str
        content: str
        user: User = DBField(on_delete="SET DEFAULT", default=1)

    User.create_table()
    Post.create_table()
    ```
=== "SET NULL"
    ```python
    from ormagic import DBModel, DBField

    class User(DBModel):
        name: str

    class Post(DBModel):
        title: str
        content: str
        user: User = DBField(on_delete="SET NULL", default=None)

    User.create_table()
    Post.create_table()
    ```

## One to one relationships

To define a one-to-one relationship, use the `unique` parameter of the `DBField` to `True`. You can find more information about one-to-one relationships in the [Unique constraints](unique.md#one-to-one-relationships) section.
