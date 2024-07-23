from ormagic.models import DBModel


def test_create_instance_from_data():
    class User(DBModel):
        name: str
        age: int

    user = User._create_instance_from_data((1, "John", 25))

    assert user.id == 1
    assert user.name == "John"
    assert user.age == 25
