<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-light.png">
  <img src="docs/assets/logo-dark.png" alt="ORMagic">
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
[![Material for MkDocs](https://img.shields.io/badge/docs-Material%20for%20MkDocs-yellow?logo=MaterialForMkDocs&logoColor=yellow)](https://spaceshaman.github.io/ORMagic/)

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

You can find more examples and detailed documentation at [spaceshaman.github.io/ORMagic/](https://spaceshaman.github.io/ORMagic/)

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
- [x] Custom primary key
- [x] Transactions
- [ ] Functions
    - [ ] Aggregate functions
    - [ ] String functions
    - [ ] Date and time functions
    - [ ] Mathematical functions
    - [ ] Control flow functions
- [ ] Migrations
- [ ] Integration with other databases
<!--roadmap-end-->

## Changelog

<!--changelog-start-->
Changes for each release are thoroughly documented in [release notes](https://github.com/SpaceShaman/ORMagic/releases)
<!--changelog-end-->

## Contributing

<!--contributing-start-->
Contributions are welcome! Feel free to open an issue or submit a pull request.
I would like to keep the library to be safe as possible, so i would appreciate if you cover any new feature with tests to maintain 100% coverage.

### Install in a development environment

1. First, clone the repository:

    ```bash
    git clone git@github.com:SpaceShaman/ORMagic.git
    ```

2. Install poetry if you don't have, here you can find the [instructions](https://python-poetry.org/docs/#installing-with-the-official-installer)

3. Create a virtual environment and install the dependencies:

    ```bash
    cd ORMagic
    poetry install --no-root
    ```

4. Activate the virtual environment:

    ```bash
    poetry shell
    ```

### Run tests

If you in the virtual environment, you can run the tests with the following command:

```bash
pytest
```

You can also run the tests with coverage:

```bash
pytest --cov=ormagic
```

<!--contributing-end-->

## License

This project is licensed under the terms of the [MIT license](https://github.com/SpaceShaman/ORMagic?tab=MIT-1-ov-file)
