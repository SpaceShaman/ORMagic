from sqlite3 import IntegrityError, OperationalError

import pytest

from ormagic import DBField, DBModel


def test_save_object_after_save_integrity_error(db_cursor):
    class User(DBModel):
        name: str = DBField(unique=True)
        age: int

    User.create_table()

    User(name="John", age=30).save()

    with pytest.raises(IntegrityError):
        User(name="John", age=20).save()

    User(name="Jane", age=25).save()

    res = User.all()
    assert len(res) == 2
    assert res[0].name == "John"
    assert res[0].age == 30
    assert res[1].name == "Jane"
    assert res[1].age == 25


def test_save_object_after_delete_operational_error(db_cursor):
    class User(DBModel):
        name: str = DBField(unique=True)
        age: int

    User.create_table()

    with pytest.raises(OperationalError):
        User(name="John", age=30).delete()

    User(name="John", age=30).save()

    res = User.all()
    assert len(res) == 1
    assert res[0].name == "John"
    assert res[0].age == 30
