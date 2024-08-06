from pydantic.fields import FieldInfo

from .field_utils import is_many_to_many_field
from .sql_utils import execute_sql


def create_table(cls, table_name: str, model_fields: dict[str, FieldInfo]):
    columns = ["id INTEGER PRIMARY KEY"]
    for field_name, field_info in model_fields.items():
        if field_name == "id":
            continue
        if is_many_to_many_field(field_info.annotation):
            _create_intermediate_table(
                cls=cls, table_name=table_name, field_info=field_info
            )
            continue
        columns.append(cls._prepare_column_definition(field_name, field_info))

    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
    cursor = execute_sql(sql)
    cursor.connection.close()


def _create_intermediate_table(cls, table_name: str, field_info: FieldInfo) -> None:
    related_table_name = getattr(field_info.annotation, "__args__")[0].__name__.lower()
    if cls._get_intermediate_table_name(related_table_name):
        return
    execute_sql(
        f"CREATE TABLE IF NOT EXISTS {table_name}_{related_table_name} ("
        "id INTEGER PRIMARY KEY, "
        f"{table_name}_id INTEGER, "
        f"{related_table_name}_id INTEGER, "
        f"FOREIGN KEY ({table_name}_id) REFERENCES {table_name}(id) ON DELETE CASCADE, "
        f"FOREIGN KEY ({related_table_name}_id) REFERENCES {related_table_name}(id) ON DELETE CASCADE)"
    )
