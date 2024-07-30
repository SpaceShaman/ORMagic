from ormagic.models import DBModel


def test_featchone_raw_data(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()
    User(name="John", age=25).save()

    row_data = User._fetchone_raw_data(id=1)

    assert isinstance(row_data, dict)
    assert row_data["id"] == 1
    assert row_data["name"] == "John"
    assert row_data["age"] == 25


def test_featchone_raw_data_with_foreign_key(db_cursor):
    class Team(DBModel):
        name: str

    class Player(DBModel):
        name: str
        team: Team

    Team.create_table()
    Player.create_table()

    team = Team(name="Barcelona").save()
    Player(name="Messi", team=team).save()

    row_data = Player._fetchone_raw_data(id=1)

    assert isinstance(row_data, dict)
    assert row_data["id"] == 1
    assert row_data["name"] == "Messi"
    assert row_data["team"] == {"id": 1, "name": "Barcelona"}


def test_featchone_raw_data_with_optional_foreign_key_not_set(db_cursor):
    class Team(DBModel):
        name: str

    class Player(DBModel):
        name: str
        team: Team | None = None

    Team.create_table()
    Player.create_table()

    Player(name="Messi").save()

    row_data = Player._fetchone_raw_data(id=1)

    assert isinstance(row_data, dict)
    assert row_data["id"] == 1
    assert row_data["name"] == "Messi"
    assert row_data["team"] is None


def test_featchall_raw_data(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()
    data = [("John", 30), ("Jane", 25), ("Doe", 35), ("John", 40)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()

    rows_data = User._fetchall_raw_data()

    assert isinstance(rows_data, list)
    assert len(rows_data) == 4
    assert all(isinstance(row, dict) for row in rows_data)
    assert all(row["id"] in [1, 2, 3, 4] for row in rows_data)
    assert all(row["name"] in ["John", "Jane", "Doe"] for row in rows_data)
    assert all(row["age"] in [25, 30, 35, 40] for row in rows_data)


def test_featchall_raw_data_with_foreign_key(db_cursor):
    class Team(DBModel):
        name: str

    class Player(DBModel):
        name: str
        team: Team

    Team.create_table()
    Player.create_table()

    team_0 = Team(name="Barcelona").save()
    team_1 = Team(name="Real Madrid").save()
    Player(name="Messi", team=team_0).save()
    Player(name="Ronaldo", team=team_1).save()

    rows_data = Player._fetchall_raw_data()

    assert isinstance(rows_data, list)
    assert len(rows_data) == 2
    assert all(isinstance(row, dict) for row in rows_data)
    assert all(row["id"] in [1, 2] for row in rows_data)
    assert all(row["name"] in ["Messi", "Ronaldo"] for row in rows_data)
    assert all(
        row["team"]
        in [{"id": 1, "name": "Barcelona"}, {"id": 2, "name": "Real Madrid"}]
        for row in rows_data
    )


def test_featchall_raw_data_with_optional_foreign_key_not_set(db_cursor):
    class Team(DBModel):
        name: str

    class Player(DBModel):
        name: str
        team: Team | None = None

    Team.create_table()
    Player.create_table()

    Player(name="Messi").save()

    rows_data = Player._fetchall_raw_data()

    assert isinstance(rows_data, list)
    assert len(rows_data) == 1
    assert all(isinstance(row, dict) for row in rows_data)
    assert all(row["id"] == 1 for row in rows_data)
    assert all(row["name"] == "Messi" for row in rows_data)
    assert all(row["team"] is None for row in rows_data)


def test_featchone_raw_data_with_many_to_many(db_cursor):
    # sourcery skip: extract-duplicate-method
    class Team(DBModel):
        name: str
        players: list["Player"] = []

    class Player(DBModel):
        name: str
        teams: list[Team]

    Team.create_table()
    Player.create_table()

    team_0 = Team(name="Barcelona").save()
    team_1 = Team(name="Real Madrid").save()
    Player(name="Messi", teams=[team_0, team_1]).save()

    row_player_data = Player._fetchone_raw_data(id=1)

    assert isinstance(row_player_data, dict)
    assert row_player_data["id"] == 1
    assert row_player_data["name"] == "Messi"
    assert row_player_data["teams"] == [
        {"id": 1, "name": "Barcelona"},
        {"id": 2, "name": "Real Madrid"},
    ]

    row_team_data = Team._fetchone_raw_data(id=1)

    assert isinstance(row_team_data, dict)
    assert row_team_data["id"] == 1
    assert row_team_data["name"] == "Barcelona"
    assert row_team_data["players"] == [{"id": 1, "name": "Messi"}]
