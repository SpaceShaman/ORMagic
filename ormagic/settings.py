import os


class Settings:
    def __init__(self):
        self.database: str = os.getenv("ORMAGIC_DATABASE", "sqlite://db.sqlite3")
