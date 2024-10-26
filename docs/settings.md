# Settings

Settings are configured using environment variables. The following settings are available:

- `ORMAGIC_DATABASE_URL`: The URL to the database. Defaults to `sqlite://db.sqlite3`.
- `ORMAGIC_JOURNAL_MODE`: The journal mode to use for SQLite. Defaults to `WAL`.

For now, only SQLite is supported as a database backend.
