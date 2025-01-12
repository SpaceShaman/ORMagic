# Settings

Settings are configured using environment variables. The following settings are available:

- `ORMAGIC_DATABASE_URL`: The URL to the database. Defaults to `sqlite://db.sqlite3`.
- `ORMAGIC_JOURNAL_MODE`: The journal mode to use for [SQLite](https://www.sqlite.org). Defaults to `WAL`.

To use a database other than [SQLite](https://www.sqlite.org), you need to set the `ORMAGIC_DATABASE_URL` environment variable (for now, only [SQLite](https://www.sqlite.org) and [PostgreSQL](https://www.postgresql.org) are supported, but more databases will be added in the future). For example, to use [PostgreSQL](https://www.postgresql.org), you need to set the `ORMAGIC_DATABASE_URL` environment variable like below:

```bash
ORMAGIC_DATABASE_URL=postgresql://user:password@localhost/dbname
```
