from .asseror import Column, ForeignKey
from .utils import get_expected_column, get_expected_foreign_key


class PostgresAssertor:
    def __init__(self, cursor):
        self.cursor = cursor

    def assert_table_schema(self, table_name: str, expected_columns: list[Column]):
        columns = self._get_table_columns(table_name)
        assert len(columns) == len(expected_columns)
        for column in columns:
            expected_column = get_expected_column(expected_columns, column[0])
            assert column[0] == expected_column.name
            assert column[1] == expected_column.type.lower()
            assert column[2] == "YES" if expected_column.nullable else "NO"
            assert column[3] == (
                f"{expected_column.default}::{expected_column.type.lower()}"
                if expected_column.default
                else None
            )
            assert column[4] == expected_column.is_primary_key

    def assert_foreign_keys(
        self, table_name: str, expected_foreign_keys: list[ForeignKey]
    ):
        foreign_keys = self._get_foreign_keys(table_name)
        assert len(foreign_keys) == len(expected_foreign_keys)
        for foreign_key in foreign_keys:
            expected_foreign_key = get_expected_foreign_key(
                expected_foreign_keys, foreign_key[0]
            )
            assert foreign_key[0] == expected_foreign_key.column_name
            assert foreign_key[1] == expected_foreign_key.foreign_table_name
            assert foreign_key[2] == expected_foreign_key.column_name_in_foreign_table
            assert foreign_key[3] == expected_foreign_key.on_delete
            assert foreign_key[4] == expected_foreign_key.on_update

    def _get_foreign_keys(self, table_name):
        self.cursor.execute(
            """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS column_name_in_foreign_table,
                rc.delete_rule AS on_delete,
                rc.update_rule AS on_update
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            JOIN information_schema.referential_constraints AS rc
            ON rc.constraint_name = tc.constraint_name
            WHERE tc.table_name = %s
            """,
            (table_name,),
        )
        return self.cursor.fetchall()

    def _get_table_columns(self, table_name):
        self.cursor.execute(
            """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                (SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_name = kcu.table_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND kcu.column_name = c.column_name
                    AND kcu.table_name = %s
                )) AS is_primary_key
            FROM information_schema.columns c
            WHERE table_name = %s;
            """,
            (table_name, table_name),
        )
        return self.cursor.fetchall()
