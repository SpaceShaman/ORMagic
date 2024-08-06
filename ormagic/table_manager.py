from pydantic.fields import FieldInfo

from .sql_utils import execute_sql


def create_table(cls, table_name: str, model_fields: dict[str, FieldInfo]):
    columns = ["id INTEGER PRIMARY KEY"]
    for field_name, field_info in model_fields.items():
        if field_name == "id":
            continue
        if cls._is_many_to_many_field(field_info.annotation):
            cls._create_intermediate_table(field_info)
            continue
        columns.append(cls._prepare_column_definition(field_name, field_info))

    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
    cursor = execute_sql(sql)
    cursor.connection.close()
