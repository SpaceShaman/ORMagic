from ormagic import DBModel


def test_get_intermediate_table_name(db_cursor):
    class Course(DBModel):
        name: str

    class User(DBModel):
        name: str
        courses: list[Course] = []

    User.create_table()
    Course.create_table()

    assert (
        User._get_intermediate_table_name(related_table_name="course") == "user_course"
    )
    assert (
        Course._get_intermediate_table_name(related_table_name="user") == "user_course"
    )


def test_try_get_intermediate_table_name_with_non_existing_related_table(db_cursor):
    class Course(DBModel):
        name: str

    class User(DBModel):
        name: str
        courses: list[Course] = []

    User.create_table()
    Course.create_table()

    assert (
        User._get_intermediate_table_name(related_table_name="non_existing_table")
        is None
    )
    assert (
        Course._get_intermediate_table_name(related_table_name="non_existing_table")
        is None
    )
