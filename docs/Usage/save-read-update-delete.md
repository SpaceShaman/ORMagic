# Save, read, update and delete data

## Save data

To save data to the database, create an instance of the `DBModel` class and call the `save` method. This will create a new record in the database if the primary key is not present, or update an existing record if the primary key is already present.

=== "Python"

    ```python
    user = User(name="John", age=30)
    user.save()
    ```

=== "SQL Result"

    ```sql
    INSERT INTO user (name, age) VALUES ('John', 30);
    ```

## Read single record

To read a single record from the database, use the `get` with keyword arguments to filter the record by the specified fields.

=== "Python"

    ```python
    user = User.get(id=1)
    >>> User(id=1, name='John', age=30)
    ```

=== "SQL Result"

    ```sql
    SELECT * FROM user WHERE id = 1;
    ```

## Read all records

To read all records from the database, use the `all` method, this will return a list of all records in the table.

=== "Python"

    ```python
    users = User.all()
    >>> [User(id=1, name='John', age=30), User(id=2, name='Alice', age=25), ...]
    ```

=== "SQL Result"

    ```sql
    SELECT * FROM user;
    ```

## Delete data

To delete a record from the database, call the `delete` method on the instance of the `DBModel` class.

=== "Python"

    ```python
    user.delete()
    ```

=== "SQL Result"

    ```sql
    DELETE FROM user WHERE id = 1;
    ```
