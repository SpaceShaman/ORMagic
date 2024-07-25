from ormagic.models import DBModel


def test_create_instance_from_data(db_cursor):
    class User(DBModel):
        name: str
        age: int

    user = User._create_instance_from_data((1, "John", 25))

    assert user.id == 1
    assert user.name == "John"
    assert user.age == 25


def test_create_instance_from_data_with_foreign_key(db_cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        user: User

    User.create_table()
    Post.create_table()
    User(name="John", age=25).save()

    post = Post._create_instance_from_data((1, "First post", 1))

    assert post.id == 1
    assert post.title == "First post"
    assert post.user.id == 1
    assert post.user.name == "John"
    assert post.user.age == 25
