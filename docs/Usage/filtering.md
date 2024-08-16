# Filtering data

To filter data and retrieve multiple records, use the `filter` method.
There are several filter options available:

## Equal

=== "Python"
    ```python
    User.filter(name="John")
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE name = 'John';
    ```

## Not equal

=== "Python"
    ```python
    User.filter(name__ne="John")
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE name != 'John';
    ```

## Greater than

=== "Python"
    ```python
    User.filter(age__gt=30)
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE age > 30;
    ```

## Greater than or equal

=== "Python"
    ```python
    User.filter(age__gte=30)
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE age >= 30;
    ```

## Less than

=== "Python"
    ```python
    User.filter(age__lt=30)
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE age < 30;
    ```

## Less than or equal

=== "Python"
    ```python
    User.filter(age__lte=30)
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE age <= 30;
    ```

## Like (Pattern matching with % and _)

=== "Python"
    ```python
    User.filter(name__like="%Cat%")
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE name LIKE '%Cat%';
    ```

## Not like (Pattern matching with % and _)

=== "Python"
    ```python
    User.filter(name__nlike="%Cat%")
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE name NOT LIKE '%Cat%';
    ```

## In (List of values)

=== "Python"
    ```python
    User.filter(name__in=["John", "Alice"])
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE name IN ('John', 'Alice');
    ```

## Not in (List of values)

=== "Python"
    ```python
    User.filter(name__nin=["John", "Alice"])
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE name NOT IN ('John', 'Alice');
    ```

## Between (Two values)

=== "Python"
    ```python
    User.filter(age__between=[30, 40])
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE age BETWEEN 30 AND 40;
    ```

## Not between (Two values)

=== "Python"
    ```python
    User.filter(age__nbetween=[30, 40])
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM user WHERE age NOT BETWEEN 30 AND 40;
    ```

## Complex filters with Q objects (AND, OR, NOT)

Keyword arguments are combined with AND by default, but you can use Q objects to combine filters with OR, NOT, and AND.

For example, to filter users with age greater than 30 or name equal to "Alice":

=== "Python"
    ```python
    from ormagic import Q

    User.filter(Q(age__gt=30) | Q(name="Alice"))
    ```
=== "SQL Result"
    ```sql
    WHERE age > 30 OR name = 'Alice'
    ```

To filter users with age less than 30 and name not equal to "Alice":

=== "Python"
    ```python
    User.filter(Q(age__lt=30) & ~Q(name="Alice"))
    ```
=== "SQL Result"
    ```sql
    WHERE age < 30 AND name != 'Alice'
    ```

You can also combine multiple conditions in one Q object:

=== "Python"
    ```python
    User.filter(Q(age__lt=30, name="John") | Q(age__gt=30, name="Alice"))
    ```
=== "SQL Result"
    ```sql
    WHERE (age < 30 AND name = 'John') OR (age > 30 AND name = 'Alice')
    ```

You can even build very complex queries by nesting Q objects:

=== "Python"
    ```python
    q1 = Q(name="Alice")
    q2 = Q(age__lt=25)
    q3 = Q(weight__gte=70)
    q4 = Q(name="Bob")
    q5 = Q(age__gt=30)
    q6 = Q(weight__lte=80)
    q = Q(q1 & q2 | q3) | Q(q4 & q5 | q6)
    User.filter(q)
    ```
=== "SQL Result"
    ```sql
    WHERE (name = 'Alice' AND age < 25 OR weight >= 70) OR (name = 'Bob' AND age > 30 OR weight <= 80)
    ```
