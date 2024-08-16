# Many-to-many relationships

To define a many-to-many relationship, use list of other model as a field in the model.

## Create tables
=== "Python"
    ```python
    from ormagic import DBModel

    class Player(DBModel):
        name: str
        teams: list["Team"] = []

    class Team(DBModel):
        name: str
        players: list[Player] = []

    Player.create_table()
    Team.create_table()
    ```
=== "SQL Result"
    ```sql
    CREATE TABLE IF NOT EXISTS player (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS team (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS player_team (
        player_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL,
        PRIMARY KEY (player_id, team_id),
        FOREIGN KEY(player_id) REFERENCES player(id),
        FOREIGN KEY(team_id) REFERENCES team(id)
    );
    ```

## Save data with many-to-many relationships

=== "Python"
    ```python
    player0 = Player(name="Messi").save()
    player1 = Player(name="Ronaldo").save()

    Team(name="Barcelona", players=[player0, player1]).save()
    ```
=== "SQL Result"
    ```sql
    INSERT INTO player (name) VALUES ('Messi');
    INSERT INTO player (name) VALUES ('Ronaldo');
    INSERT INTO team (name) VALUES ('Barcelona');
    INSERT INTO player_team (player_id, team_id) VALUES (1, 1);
    INSERT INTO player_team (player_id, team_id) VALUES (2, 1);
    ```

## Read data with many-to-many relationships

=== "Python"
    ```python
    Team.get(id=1)
    >>> Team(id=1, name='Barcelona', players=[Player(id=1, name='Messi'), Player(id=2, name='Ronaldo')])
    ```
=== "SQL Result"
    ```sql
    SELECT * FROM team WHERE id = 1;
    SELECT * FROM player WHERE id IN (SELECT player_id FROM player_team WHERE team_id = 1);
    ```
