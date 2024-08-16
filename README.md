<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-light.png">
  <img src="docs/assets/logo-dark.png">
</picture>

<!--intro-start-->
[![GitHub License](https://img.shields.io/github/license/SpaceShaman/ORMagic)](https://github.com/SpaceShaman/ORMagic?tab=MIT-1-ov-file)
[![Tests](https://img.shields.io/github/actions/workflow/status/SpaceShaman/ORMagic/release.yml?label=tests)](https://github.com/SpaceShaman/ORMagic/blob/master/.github/workflows/tests.yml)
[![Codecov](https://img.shields.io/codecov/c/github/SpaceShaman/ORMagic)](https://codecov.io/gh/SpaceShaman/ORMagic)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ORMagic)](https://pypi.org/project/ORMagic)
[![PyPI - Version](https://img.shields.io/pypi/v/ORMagic)](https://pypi.org/project/ORMagic)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/badge/linting-Ruff-black?logo=ruff&logoColor=black)](https://github.com/astral-sh/ruff)
[![Pydantic](https://img.shields.io/badge/technology-Pydantic-blue?logo=pydantic&logoColor=blue)](https://docs.pydantic.dev)
[![SQLite](https://img.shields.io/badge/technology-SQLite-blue?logo=sqlite&logoColor=blue)](https://www.sqlite.org)
[![Pytest](https://img.shields.io/badge/testing-Pytest-red?logo=pytest&logoColor=red)](https://docs.pytest.org/)
[![MkDocs-Material](https://img.shields.io/badge/docs-Material%20for%20MkDocs-yellow?logo=MaterialForMkDocs&logoColor=yellow)](https://spaceshaman.github.io/ORMagic/)

The main goal of ORMagic is to provide a simple and easy-to-use ORM for [Python](https://www.python.org/), that is easy to understand and use, while still providing the necessary features to interact with a database.
Is based on the [Pydantic](https://docs.pydantic.dev) model and extends it with the ability to interact with [SQLite](https://www.sqlite.org) database.

## Simple example

```python
from ormagic import DBModel

class User(DBModel):
    name: str
    age: int

User.create_table()

User(name="John", age=30).save()

User.get(name="John")
>>> User(id=1, name='John', age=30)
```
<!--intro-end-->

## Installation

<!--installation-start-->
You can install ORMagic using pip:

```bash
pip install ORMagic
```

Or you can install the latest version from the GitHub repository:

```bash
git clone git@github.com:SpaceShaman/ORMagic.git
cd ORMagic
pip install .
```
<!--installation-end-->

## Documentation

The full documentation is available at [spaceshaman.github.io/ORMagic/](https://spaceshaman.github.io/ORMagic/)

## Usage

### Define a model

To define a model, create a class that inherits from `DBModel` and define the fields using Pydantic's field types.

```python
from ormagic import DBModel

class User(DBModel):
    name: str
    age: int

# Create the table in the database
User.create_table()
```

### Save, read, update and delete data

```python
# Save data to the database, this will create a new record or update an existing one if the primary key is already present
user = User(name="John", age=30)
user.save()

# Read data from the database
user = User.get(id=1)
>>> User(id=1, name='John', age=30)

# Read all data from the database
users = User.all()
>>> [User(id=1, name='John', age=30), User(id=2, name='Alice', age=25), ...]

# Delete data from the database
user.delete()

# Update data
user = User.get(id=1)
user.age = 31
user.save()

# Filter data and retrieve multiple records
users = User.filter(age=31)
>>> [User(id=1, name='John', age=31), User(id=2, name='Alice', age=31), ...]
```

### Define foreign keys

To define a foreign key, use other models as fields in the model.
By default, the foreign key will be set to `CASCADE`, but you can change it by setting the `on_delete` parameter of the pydantic field to one of the following values: `CASCADE`, `SET NULL`, `RESTRICT`, `SET DEFAULT`, `NO ACTION`.

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

user = User(name="John")
user.save()

Post(title="Hello", content="World", user=user).save()

# You can also save child models with new parent object in one step, this will save the parent object first and then the child object
Post(title="Hello", content="World", user=User(name="Alice")).save()
```

#### Define foreign key with custom on_delete

```python
from ormagic import DBModel, DBField

class User(DBModel):
    name: str

class Post(DBModel):
    title: str
    content: str
    user: User = DBField(on_delete="CASCADE")
    user: User = DBField(on_delete="RESTRICT")
    user: User = DBField(on_delete="NO ACTION")
    user: User = DBField(on_delete="SET DEFAULT", default=1)
    user: User = DBField(on_delete="SET NULL", default=None)

User.create_table()
Post.create_table()
```

### Unique constraints

To define a unique constraint, use the `unique` parameter set to `True` in the Pydantic field.

```python
from ormagic import DBModel, DBField

class User(DBModel):
    name: str
    email: str = DBField(unique=True)
```

You can also use the `unique` parameter to define one to one relationships between tables.

```python
from ormagic import DBModel, DBField

class User(DBModel):
    name: str

class UserProfile(DBModel):
    user: User = DBField(unique=True)
    bio: str
```

### Deleting and updating tables

To delete a table, use the `drop_table` method.

```python
User.drop_table()
```

To update a table, use the `update_table` method.

```python
User.update_table()
```

There are some restrictions on updating tables:

- The new column cannot have `unique` or `primary_key` set to `True`.
- The new column needs to have a default value or set as optional.
- You can rename, drop and add multiple columns at once but you cannot mix this tree operations in one call.

### Many-to-many relationships

To define a many-to-many relationship, use list of other model as a field in the model.

```python
from ormagic import DBModel

class Player(DBModel):
    name: str
    teams: list["Team"] = []

class Team(DBModel):
    name: str
    players: list[Player] = []

Player.create_table()
Team.create_table()

player0 = Player(name="Messi").save()
player1 = Player(name="Ronaldo").save()

Team(name="Barcelona", players=[player0, player1]).save()

Team.get(id=1)
>>> Team(id=1, name='Barcelona', players=[Player(id=1, name='Messi'), Player(id=2, name='Ronaldo')])
```

### Filtering data

To filter data and retrieve multiple records, use the `filter` method.
There are several filter options available:

#### Equal

```python
User.filter(name="John")
```

#### Not equal

```python
User.filter(name__ne="John")
```

#### Greater than

```python
User.filter(age__gt=30)
```

#### Greater than or equal

```python
User.filter(age__gte=30)
```

#### Less than

```python
User.filter(age__lt=30)
```

#### Less than or equal

```python
User.filter(age__lte=30)
```

#### Like (Pattern matching with % and _)

```python
User.filter(name__like="%Cat%")
```

#### Not like (Pattern matching with % and _)

```python
User.filter(name__nlike="%Cat%")
```

#### In (List of values)

```python
User.filter(name__in=["John", "Alice"])
```

#### Not in (List of values)

```python
User.filter(name__nin=["John", "Alice"])
```

#### Between (Two values)

```python
User.filter(age__between=[30, 40])
```

#### Not between (Two values)

```python
User.filter(age__nbetween=[30, 40])
```

#### Complex filters with Q objects (AND, OR, NOT)

Keyword arguments are combined with AND by default, but you can use Q objects to combine filters with OR, NOT, and AND.

For example, to filter users with age greater than 30 or name equal to "Alice":

```python
from ormagic import Q

User.filter(Q(age__gt=30) | Q(name="Alice"))
```

This is equivalent to the following SQL WHERE clause:

```sql
WHERE age > 30 OR name = 'Alice'
```

To filter users with age less than 30 and name not equal to "Alice":

```python
User.filter(Q(age__lt=30) & ~Q(name="Alice"))
```

This is equivalent to the following SQL WHERE clause:

```sql
WHERE age < 30 AND name != 'Alice'

You can also combine multiple conditions in one Q object:

```python
User.filter(Q(age__lt=30, name="John") | Q(age__gt=30, name="Alice"))
```

This is equivalent to the following SQL WHERE clause:

```sql
WHERE (age < 30 AND name = 'John') OR (age > 30 AND name = 'Alice')
```

You can even build very complex queries by nesting Q objects:

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

This is equivalent to the following SQL WHERE clause:

```sql
WHERE (name = 'Alice' AND age < 25 OR weight >= 70) OR (name = 'Bob' AND age > 30 OR weight <= 80)
```

### Order by

To order the results, use the `filter` or `all` method with the `order_by` parameter.

```python
User.filter(order_by="age")
```

To order the results in descending order, use the `-` sign before the field name.

```python
User.all(order_by="-age")
```

You can also order by multiple fields and mix them with filters.

```python
User.filter(name="John", order_by=["age", "-name"])
```

### Limit and offset

To limit the number of results, use the `limit` parameter.

```python
User.all(limit=10)
```

You can also use the `offset` parameter to skip a certain number of results to implement pagination.

```python
User.all(limit=10, offset=10)
```

You can also use the `limit` and `offset` parameters with filters and order by.

```python
User.filter(age__between=[30, 40], order_by="age", limit=10, offset=10)
```

### Integration with [FastAPI](https://fastapi.tiangolo.com/)

Because ORMagic is based on [Pydantic](https://docs.pydantic.dev), it can be easily integrated with [FastAPI](https://fastapi.tiangolo.com/).
Below is an example of how to use ORMagic with [FastAPI](https://fastapi.tiangolo.com/) to create a simple CRUD REST API.

```python
from fastapi import FastAPI
from ormagic import DBModel

app = FastAPI()

class User(DBModel):
    name: str
    age: int

User.create_table()

@app.post("/users/")
def create_user(user: User):
    return user.save()

@app.get("/users/")
def read_users():
    return User.all()

@app.get("/users/{id}")
def read_user(id: int):
    return User.get(id=id)

@app.put("/users/{id}")
def update_user(id: int, user: User):
    user.id = id
    return user.save()

@app.delete("/users/{id}")
def delete_user(id: int):
    User.get(id=id).delete()
    return {"message": "User deleted"}
```

## Features and Roadmap

<!--roadmap-start-->
- [x] Define table schema using Pydantic models
- [x] Basic CRUD operations
    - [x] Save data to the database
    - [x] Read data from the database
    - [x] Update data in the database
    - [x] Delete data from the database
- [x] Relationships between tables
    - [x] One-to-many
        - [x] Create a tables with a foreign key
        - [x] Save data with a foreign key
        - [x] Read data with a foreign key
        - [x] Update data with a foreign key
        - [x] Delete data with a foreign key
            - [X] Cascade
            - [x] Set null
            - [x] Restrict
            - [x] Set default
            - [x] No action
    - [x] One-to-one
    - [x] Many-to-many
- [x] Unique constraints
- [x] Remove table
- [x] Read all data from the database
- [x] Filter data and retrieve multiple records
    - [x] Equal
    - [x] Not equal
    - [x] Greater than
    - [x] Greater than or equal
    - [x] Less than
    - [x] Less than or equal
    - [x] Like (Pattern matching with % and _)
    - [x] Not like (Pattern matching with % and _)
    - [x] In (List of values)
    - [x] Not in (List of values)
    - [x] Between (Two values)
    - [x] Not between (Two values)
    - [x] Q objects to combine filters (AND, OR, NOT)
- [x] Protect against SQL injection
- [x] Order by
- [x] Limit and offset
- [x] Update table schema
    - [x] Add new column
    - [x] Rename column
    - [x] Drop column
- [ ] Custom primary key
- [ ] Functions
    - [ ] Aggregate functions
    - [ ] String functions
    - [ ] Date and time functions
    - [ ] Mathematical functions
    - [ ] Control flow functions
- [ ] Bulk operations (save, update, delete)
- [ ] Migrations
<!--roadmap-end-->

## Changelog

<!--changelog-start-->
Changes for each release are thoroughly documented in [release notes](https://github.com/SpaceShaman/ORMagic/releases)
<!--changelog-end-->

## License

This project is licensed under the terms of the [MIT license](https://github.com/SpaceShaman/ORMagic?tab=MIT-1-ov-file)

## Contributing

<!--contributing-start-->
Contributions are welcome! Feel free to open an issue or submit a pull request.
I would like to keep the library to be safe as possible, so i would appreciate if you cover any new feature with tests to maintain 100% coverage.
<!--contributing-end-->
