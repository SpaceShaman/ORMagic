from ormagic import DBModel


def test_try_to_get_all_users_with_sql_injection(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()
    User(name="John", age=30).save()
    User(name="Alice", age=25).save()
    User(name="Bob", age=35).save()

    users = User.filter(name="John' OR 1=1 --")

    assert len(users) == 0


def test_try_to_get_all_users_with_sql_injection_in_list(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()
    User(name="John", age=30).save()
    User(name="Alice", age=25).save()
    User(name="Bob", age=35).save()

    users = User.filter(name__in=["John' OR 1=1 --"])

    assert len(users) == 0
