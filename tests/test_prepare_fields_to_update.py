from ormagic.models import DBModel


def test_prepare_fields_to_update():
    fields = DBModel._prepare_fields_to_update({"name": "John", "age": 25})

    assert fields == "name='John', age='25'"


def test_prepare_fields_to_update_with_foreign_key():
    fields = DBModel._prepare_fields_to_update(
        {"title": "First post", "user": {"id": 1}}
    )

    assert fields == "title='First post', user='1'"
