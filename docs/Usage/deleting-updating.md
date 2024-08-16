# Deleting and updating tables

To delete a table, use the `drop_table` method.

=== "Python"

    ```python
    User.drop_table()
    ```
=== "SQL Result"

    ```sql
    DROP TABLE IF EXISTS user;
    ```

To update a table, use the `update_table` method.

=== "Python"
    ```python
    User.update_table()
    ```
=== "SQL Result"
    ```sql
    ALTER TABLE user ADD COLUMN email TEXT;
    ```

There are some restrictions on updating tables:

- The new column cannot have `unique` or `primary_key` set to `True`.
- The new column needs to have a default value or set as optional.
- You can rename, drop and add multiple columns at once but you cannot mix this tree operations in one call.