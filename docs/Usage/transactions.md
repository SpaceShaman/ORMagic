# Transactions

Transactions are a way to group multiple operations together. They are atomic, meaning that either all operations in the transaction are applied or none are. This is useful when you want to make sure that multiple operations are applied together or not at all.

To use transactions, you can use the `transaction` context manager. This will start a new transaction and commit the transaction if no exceptions are raised. If an exception is raised, the transaction will be rolled back.

=== "Python"

    ```python
    from ormagic import DBModel, transaction

    class User(DBModel):
        name: str
        age: int

    with transaction():
        user1 = User(name="John", age=30)
        user1.save()

        user2 = User(name="Alice", age=25)
        user2.save()
    ```

=== "SQL Result"

    ```sql
    BEGIN;
    INSERT INTO user (name, age) VALUES ('John', 30);
    INSERT INTO user (name, age) VALUES ('Alice', 25);
    COMMIT;
    ```
