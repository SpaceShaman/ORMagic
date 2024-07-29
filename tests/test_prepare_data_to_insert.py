from ormagic.models import DBModel


def test_prepare_values_to_insert():
    class User(DBModel):
        name: str
        age: int

    user = User(name="John", age=25)

    values = user._prepare_data_to_insert({"name": "John", "age": 25})

    assert values == {"age": 25, "name": "John"}


def test_prepare_values_to_insert_with_foreign_key():
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        user: User

    User.create_table()
    Post.create_table()
    User(name="John", age=25).save()

    post = Post(title="First post", user=User.get(id=1))

    values = post._prepare_data_to_insert({"title": "First post", "user": {"id": 1}})

    assert values == {"title": "First post", "user": 1}
