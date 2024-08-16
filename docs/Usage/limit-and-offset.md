# Limit and offset

To limit the number of results, use the `limit` parameter.

=== "Python"
    ```python
    User.all(limit=10)
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user LIMIT 10;
    ```

You can also use the `offset` parameter to skip a certain number of results to implement pagination.

=== "Python"
    ```python
    User.all(limit=10, offset=10)
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user LIMIT 10 OFFSET 10;
    ```

You can also use the `limit` and `offset` parameters with filters and order by.

=== "Python"
    ```python
    User.filter(age__between=[30, 40], order_by="age", limit=10, offset=10)
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE age BETWEEN 30 AND 40 ORDER BY age LIMIT 10 OFFSET 10;
    ```
