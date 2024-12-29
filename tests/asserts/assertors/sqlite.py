from .asseror import Column, ForeignKey
from .utils import get_expected_column, get_expected_foreign_key


class SQLiteAssertor:
    def __init__(self, cursor):
        self.cursor = cursor

    def assert_table_schema(self, table_name: str, expected_columns: list[Column]):
        columns = self._get_table_columns(table_name)
        assert len(columns) == len(expected_columns)
        for column in columns:
            expected_column = get_expected_column(expected_columns, column[1])
            assert column[1] == expected_column.name
            assert column[2] == expected_column.type
            assert column[3] == 0 if expected_column.nullable else 1
            assert column[4] == expected_column.default
            assert column[5] == expected_column.is_primary_key

    def assert_foreign_keys(
        self, table_name: str, expected_foreign_keys: list[ForeignKey]
    ):
        foreign_keys = self._get_foreign_keys(table_name)
        assert len(foreign_keys) == len(expected_foreign_keys)
        for foreign_key in foreign_keys:
            expected_foreign_key = get_expected_foreign_key(
                expected_foreign_keys, foreign_key[3]
            )
            assert foreign_key[2] == expected_foreign_key.foreign_table_name
            assert foreign_key[3] == expected_foreign_key.column_name
            assert foreign_key[4] == expected_foreign_key.column_name_in_foreign_table
            assert foreign_key[5] == expected_foreign_key.on_delete
            assert foreign_key[6] == expected_foreign_key.on_update

    def _get_foreign_keys(self, table_name):
        return self.cursor.execute(f"PRAGMA foreign_key_list({table_name});").fetchall()

    def _get_table_columns(self, table_name):
        return self.cursor.execute(f"PRAGMA table_info({table_name});").fetchall()
