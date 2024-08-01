from datetime import datetime

import pytest

from ormagic.models import DBModel, ObjectNotFound


@pytest.fixture
def prepare_db(db_cursor):
    db_cursor.execute(
        "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
    )
    db_cursor.connection.commit()
    data = [("John", 30), ("Jane", 25), ("Doe", 35), ("John", 40)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()


class User(DBModel):
    name: str
    age: int


def test_get_object_from_db(prepare_db):
    user = User.get(id=2)

    assert user.id == 2
    assert user.name == "Jane"
    assert user.age == 25


def test_get_object_from_db_by_name(prepare_db):
    user = User.get(name="Doe")

    assert user.id == 3
    assert user.name == "Doe"
    assert user.age == 35


def test_get_object_from_db_with_multiple_conditions(prepare_db):
    user = User.get(name="John", age=30)

    assert user.id == 1
    assert user.name == "John"
    assert user.age == 30


def test_try_to_get_non_existing_object_from_db(prepare_db):
    with pytest.raises(ObjectNotFound):
        User.get(id=100)


def test_try_to_get_object_from_db_with_wrong_condition(prepare_db):
    with pytest.raises(ValueError):
        User.get(wrong_field="John")


def test_get_object_from_db_with_datetime_field(prepare_db, db_cursor):
    class UserWithDatetime(DBModel):
        name: str
        created_at: datetime

    UserWithDatetime.create_table()
    UserWithDatetime(name="John", created_at=datetime(2022, 3, 1, 12, 0, 0)).save()

    user_from_db = UserWithDatetime.get(id=1)
    assert user_from_db.id == 1
    assert user_from_db.name == "John"
    assert user_from_db.created_at == datetime(2022, 3, 1, 12, 0, 0)


def test_get_object_from_db_with_foreign_key(db_cursor):
    class Team(DBModel):
        name: str

    class Player(DBModel):
        name: str
        team: Team

    Team.create_table()
    Player.create_table()

    team = Team(name="Barcelona").save()
    Player(name="Messi", team=team).save()

    player_from_db = Player.get(id=1)
    assert player_from_db.id == 1
    assert player_from_db.name == "Messi"
    assert player_from_db.team.id == 1
    assert player_from_db.team.name == "Barcelona"


def test_get_object_from_db_with_optional_foreign_key_not_set(db_cursor):
    class Team(DBModel):
        name: str

    class Player(DBModel):
        name: str
        team: Team | None = None

    Team.create_table()
    Player.create_table()

    Player(name="Messi").save()

    player_from_db = Player.get(id=1)
    assert player_from_db.id == 1
    assert player_from_db.name == "Messi"
    assert player_from_db.team is None


def test_get_object_from_db_with_optional_foreign_key_set(db_cursor):
    class Team(DBModel):
        name: str

    class Player(DBModel):
        name: str
        team: Team | None = None

    Team.create_table()
    Player.create_table()

    team = Team(name="Barcelona").save()
    Player(name="Messi", team=team).save()

    player_from_db = Player.get(id=1)
    assert player_from_db.id == 1
    assert player_from_db.name == "Messi"
    assert player_from_db.team.id == 1  # type: ignore
    assert player_from_db.team.name == "Barcelona"  # type: ignore


def test_get_object_with_many_to_many_relationship(db_cursor):
    class Team(DBModel):
        name: str
        players: list["Player"] = []

    class Player(DBModel):
        name: str
        teams: list[Team] = []

    Team.create_table()
    Player.create_table()

    team1 = Team(name="Barcelona").save()
    team2 = Team(name="Real Madrid").save()
    Player(name="Messi", teams=[team1, team2]).save()
    Player(name="Ronaldo", teams=[team2]).save()

    player_from_db = Player.get(id=1)

    assert player_from_db.id == 1
    assert player_from_db.name == "Messi"
    assert len(player_from_db.teams) == 2
    assert player_from_db.teams[0].id == 1
    assert player_from_db.teams[0].name == "Barcelona"
    assert player_from_db.teams[1].id == 2
    assert player_from_db.teams[1].name == "Real Madrid"

    team1_from_db = Team.get(id=1)
    assert team1_from_db.id == 1
    assert team1_from_db.name == "Barcelona"
    assert len(team1_from_db.players) == 1
    assert team1_from_db.players[0].id == 1
    assert team1_from_db.players[0].name == "Messi"

    team2_from_db = Team.get(id=2)
    assert team2_from_db.id == 2
    assert team2_from_db.name == "Real Madrid"
    assert len(team2_from_db.players) == 2
    assert team2_from_db.players[0].id == 1
    assert team2_from_db.players[0].name == "Messi"
    assert team2_from_db.players[1].id == 2
    assert team2_from_db.players[1].name == "Ronaldo"


def test_get_object_with_many_to_many_relationship_without_related_objects(db_cursor):
    class Team(DBModel):
        name: str

    class Player(DBModel):
        name: str
        teams: list[Team] = []

    Team.create_table()
    Player.create_table()

    Player(name="Messi").save()

    player_from_db = Player.get(id=1)
    assert player_from_db.id == 1
    assert player_from_db.name == "Messi"
    assert len(player_from_db.teams) == 0
