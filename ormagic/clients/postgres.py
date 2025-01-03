from typing import Any

from psycopg2 import connect
from psycopg2._psycopg import connection, cursor
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from ormagic.field_utils import (
    get_foreign_key_model,
    get_on_delete_action,
    is_primary_key_field,
    is_unique_field,
    transform_field_annotation_to_sql_type,
)
from ormagic.settings import Settings


class PostgresClient:
    def create_connection(self) -> connection:
        settings = Settings()
        connection = connect(settings.database_url)
        self.connection = connection
        self.cursor = connection.cursor()
        return connection

    def execute(self, sql: str, parameters: list | None = None) -> cursor:
        self.cursor.execute(sql, parameters)
        self.commit()
        return self.cursor

    def close(self) -> None:
        self.connection.close()

    def rollback(self) -> None:
        self.connection.rollback()

    def commit(self) -> None:
        self.connection.commit()

    def create_table(self, table_name: str, columns: list[str]) -> None:
        self.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")

    def is_table_exists(self, table_name: str) -> bool:
        cursor = self.execute(
            f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
        )
        result = cursor.fetchone()
        return result is not None and result[0] == 1

    def get_column_names(self, table_name: str) -> list[str]:
        cursor = self.execute(f"PRAGMA table_info({table_name})")
        return [column[1] for column in cursor.fetchall()]

    def drop_column(self, table_name: str, column_name: str) -> None:
        self.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")

    def rename_column(
        self, table_name: str, old_column_name: str, new_column_name: str
    ) -> None:
        self.execute(
            f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name}"
        )

    def add_column(self, table_name: str, column_name: str) -> None:
        self.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name}")

    def drop_table(self, table_name: str) -> None:
        self.execute(f"DROP TABLE {table_name}")

    def update_rows(self, table_name: str, fields: dict[str, Any], where: str) -> None:
        set_fields = ", ".join(
            f"{field} = '{value}'" if value else f"{field} = NULL"
            for field, value in fields.items()
        )
        self.execute(f"UPDATE {table_name} SET {set_fields} WHERE {where}")

    def delete_rows(self, table_name: str, where: str) -> None:
        self.execute(f"DELETE FROM {table_name} WHERE {where}")

    def insert_row(
        self, table_name: str, columns: list[str], values: list[str]
    ) -> None:
        self.execute(
            f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values])})",
            values,
        )

    def insert_row_and_get_id(
        self, table_name: str, columns: list[str], values: list[str], id_column: str
    ) -> int:
        cursor = self.execute(
            f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values])}) RETURNING {id_column}",
            values,
        )
        return result[0] if (result := cursor.fetchone()) else 0

    def is_row_exists(self, table_name: str, where: str) -> bool:
        cursor = self.execute(f"SELECT count(*) FROM {table_name} WHERE {where}")
        result = cursor.fetchone()
        return result is not None and result[0] == 1

    def fetchone(self, sql: str, parameters: list[Any] | None = None) -> Any:
        cursor = self.execute(sql, parameters)
        return cursor.fetchone()

    def fetchall(self, sql: str, parameters: list[Any] | None = None) -> list[Any]:
        cursor = self.execute(sql, parameters)
        return cursor.fetchall()

    def prepare_column_definition(self, field_name: str, field_info: FieldInfo) -> str:
        field_type = transform_field_annotation_to_sql_type(field_info.annotation)
        column_definition = f"{field_name} {field_type}"
        if field_info.default not in (PydanticUndefined, None):
            column_definition += f" DEFAULT '{field_info.default}'"
        if field_info.is_required():
            column_definition += " NOT NULL"
        if is_unique_field(field_info):
            column_definition += " UNIQUE"
        if foreign_model := get_foreign_key_model(field_info.annotation):
            action = get_on_delete_action(field_info)
            column_definition += f", FOREIGN KEY ({field_name}) REFERENCES {foreign_model._get_table_name()}({foreign_model._get_primary_key_field_name()}) ON UPDATE {action} ON DELETE {action}"
        if is_primary_key_field(field_info):
            column_definition = column_definition.replace("INTEGER", "SERIAL")
            column_definition += " PRIMARY KEY"
        return column_definition
