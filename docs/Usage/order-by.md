# Order by

To order the results, use the `filter` or `all` method with the `order_by` parameter.

=== "Python"
    ```python
    User.all(order_by="age")
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user ORDER BY age;
    ```

To order the results in descending order, use the `-` sign before the field name.

=== "Python"
    ```python
    User.all(order_by="-age")
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user ORDER BY age DESC;
    ```

You can also order by multiple fields and mix them with filters.

=== "Python"
    ```python
    User.filter(name="John", order_by=["age", "-name"])
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE name = 'John' ORDER BY age, name DESC;
    ```
