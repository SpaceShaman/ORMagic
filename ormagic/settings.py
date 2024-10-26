import os


class SettingsError(Exception):
    pass


class Settings:
    def __init__(self):
        self.database_url = os.getenv("ORMAGIC_DATABASE_URL", "sqlite://db.sqlite3")
        if "://" not in self.database_url:
            raise SettingsError("Database URL is not valid")
        self.db_type = self.database_url.split("://")[0]
        self.path = self.database_url.split("://")[1]
        self.journal_mode = os.getenv("ORMAGIC_JOURNAL_MODE", "WAL")
