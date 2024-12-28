from typing import Optional

from ormagic import DBField, DBModel

from .asserts import Column, assert_table_schema


def test_create_table(cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()

    assert_table_schema(
        cursor,
        "users",
        [
            Column(name="id", type="INTEGER", is_primary_key=True),
            Column(name="name", type="TEXT"),
            Column(name="age", type="INTEGER"),
        ],
    )


def test_create_table_with_optional_field(cursor):
    class User(DBModel):
        name: str
        age: int
        optional_field: str | None = None
        another_optional_field: Optional[int] = None

    User.create_table()

    assert_table_schema(
        cursor,
        "users",
        [
            Column(name="id", type="INTEGER", is_primary_key=True),
            Column(name="name", type="TEXT"),
            Column(name="age", type="INTEGER"),
            Column(name="optional_field", type="TEXT", nullable=True),
            Column(name="another_optional_field", type="INTEGER", nullable=True),
        ],
    )


def test_create_table_with_default_value(cursor):
    class User(DBModel):
        default_field: str = "default value"

    User.create_table()

    assert_table_schema(
        cursor,
        "users",
        [
            Column(name="id", type="INTEGER", is_primary_key=True),
            Column(name="default_field", type="TEXT", default="'default value'"),
        ],
    )


def test_create_tables_with_one_to_many_relationship(cursor):
    class User(DBModel):
        name: str

    class Post(DBModel):
        title: str
        author: User

    User.create_table()
    Post.create_table()

    assert_table_schema(
        cursor,
        "users",
        [
            Column(name="id", type="INTEGER", is_primary_key=True),
            Column(name="name", type="TEXT"),
        ],
    )
    assert_table_schema(
        cursor,
        "posts",
        [
            Column(name="id", type="INTEGER", is_primary_key=True),
            Column(name="title", type="TEXT"),
            Column(name="author", type="INTEGER"),
        ],
    )


def test_create_tables_with_many_to_many_relationship(cursor):
    class User(DBModel):
        name: str
        groups: list["Grade"] = []

    class Grade(DBModel):
        name: str
        users: list["User"] = []

    User.create_table()
    Grade.create_table()

    assert_table_schema(
        cursor,
        "users",
        [
            Column(name="id", type="INTEGER", is_primary_key=True),
            Column(name="name", type="TEXT"),
        ],
    )
    assert_table_schema(
        cursor,
        "grades",
        [
            Column(name="id", type="INTEGER", is_primary_key=True),
            Column(name="name", type="TEXT"),
        ],
    )
    assert_table_schema(
        cursor,
        "users_grades",
        [
            Column(name="id", type="INTEGER", is_primary_key=True),
            Column(name="users_id", type="INTEGER"),
            Column(name="grades_id", type="INTEGER"),
        ],
    )


def test_create_table_with_custom_primary_key(cursor):
    class User(DBModel):
        custom_id: int = DBField(primary_key=True)
        name: str

    User.create_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert "id" not in User.model_fields.keys()
    assert "custom_id" in User.model_fields.keys()
    assert data == [
        (0, "custom_id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
    ]


def test_create_table_with_custom_primary_key_string(cursor):
    class User(DBModel):
        custom_id: str = DBField(primary_key=True)
        name: str

    User.create_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert "id" not in User.model_fields.keys()
    assert "custom_id" in User.model_fields.keys()
    assert data == [
        (0, "custom_id", "TEXT", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
    ]


def test_create_table_with_custom_primary_key_uuid(cursor):
    from uuid import UUID

    class User(DBModel):
        custom_id: UUID = DBField(primary_key=True)
        name: str

    User.create_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert "id" not in User.model_fields.keys()
    assert "custom_id" in User.model_fields.keys()
    assert data == [
        (0, "custom_id", "TEXT", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
    ]


def test_create_table_with_one_to_many_relationship_and_custom_primary_key(cursor):
    class User(DBModel):
        custom_id: int = DBField(primary_key=True)
        name: str

    class Post(DBModel):
        title: str
        user: User

    User.create_table()
    Post.create_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "custom_id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
    ]

    res = cursor.execute("PRAGMA table_info(post)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "title", "TEXT", 1, None, 0),
        (2, "user", "INTEGER", 1, None, 0),
    ]
    # check if foreign key is correct
    res = cursor.execute("PRAGMA foreign_key_list(post)")
    data = res.fetchall()
    assert data == [(0, 0, "user", "user", "custom_id", "CASCADE", "CASCADE", "NONE")]


def test_create_table_with_many_to_many_relationship_and_custom_primary_key(cursor):
    class Team(DBModel):
        team_id: int = DBField(primary_key=True)
        name: str

    class Player(DBModel):
        player_id: int = DBField(primary_key=True)
        name: str
        teams: list[Team] = []

    Team.create_table()
    Player.create_table()

    res = cursor.execute("PRAGMA table_info(team)")
    data = res.fetchall()
    assert data == [
        (0, "team_id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
    ]

    res = cursor.execute("PRAGMA table_info(player)")
    data = res.fetchall()
    assert data == [
        (0, "player_id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
    ]

    res = cursor.execute("PRAGMA table_info(player_team)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "player_id", "INTEGER", 0, None, 0),
        (2, "team_id", "INTEGER", 0, None, 0),
    ]
    # check if foreign key is correct
    res = cursor.execute("PRAGMA foreign_key_list(player_team)")
    data = res.fetchall()
    assert data == [
        (0, 0, "team", "team_id", "team_id", "CASCADE", "CASCADE", "NONE"),
        (1, 0, "player", "player_id", "player_id", "CASCADE", "CASCADE", "NONE"),
    ]
