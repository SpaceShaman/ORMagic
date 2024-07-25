# ORMagic - Simple ORM for Python

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

The main goal of ORMagic is to provide a simple and easy-to-use ORM for [Python](https://www.python.org/), that is easy to understand and use, while still providing the necessary features to interact with a database.
The library is in the early stages of development, so it is not recommended to use it in production.
Is based on the [Pydantic](https://docs.pydantic.dev) model and extends it with the ability to save, read, update and delete data from a [SQLite](https://www.sqlite.org) database.

## Installation

```bash
pip install ORMagic
```

## Usage

### Define a model

To define a model, create a class that inherits from `DBModel` and define the fields using Pydantic's field types.

```python
from ormagic import DBModel

class User(DBModel):
    name: str
    age: int
    created_at: datetime = datetime.now()

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
print(user)
>>> User(id=1, name='John', age=30, created_at=datetime.datetime(2021, 10, 10, 12, 0, 0))

# Delete data from the database
user.delete()

# Update data
user = User.get(id=1)
user.age = 31
user.save()
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
from ormagic import DBModel
from pydantic import Field

class User(DBModel):
    name: str

class Post(DBModel):
    title: str
    content: str
    user: User = Field(on_delete="CASCADE")
    user: User = Field(on_delete="RESTRICT")
    user: User = Field(on_delete="NO ACTION")
    user: User = Field(on_delete="SET DEFAULT", default=1)
    user: User = Field(on_delete="SET NULL", default=None)

User.create_table()
Post.create_table()
```

### Unique constraints

To define a unique constraint, use the `unique` parameter set to `True` in the Pydantic field.

```python
from ormagic import DBModel
from pydantic import Field

class User(DBModel):
    name: str
    email: str = Field(unique=True)
```

You can also use the `unique` parameter to define one to one relationships between tables.

```python
from ormagic import DBModel
from pydantic import Field

class User(DBModel):
    name: str

class UserProfile(DBModel):
    user: User = Field(unique=True)
    bio: str
```

### Deleting and updating tables

To delete a table, use the `drop_table` method.

```python
User.drop_table()
```

To update a table, use the `update_table` method. (Not implemented yet)

```python
User.update_table()
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

- [x] Define table schema using Pydantic models
- [x] Basic CRUD operations
  - [x] Save data to the database
  - [x] Read data from the database
  - [x] Update data in the database
  - [x] Delete data from the database
- [ ] Relationships between tables
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
  - [ ] Many-to-many
- [x] Unique constraints
- [x] Remove table
- [ ] Update table schema
- [ ] Filter data and retrieve multiple records
- [ ] Custom primary key
- [ ] Bulk operations (save, update, delete)
- [ ] Migrations

## License

This project is licensed under the terms of the [MIT license](https://github.com/SpaceShaman/ORMagic?tab=MIT-1-ov-file)

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## Why?

There are many ORMs for Python, but most of them are too complex or have too many features that are not needed for simple projects.
