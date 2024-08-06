from .sql_utils import execute_sql


def save(self):
    return self._update() if self.id else _insert(self)


def _insert(self):
    prepared_data = self._prepare_data_to_insert(self.model_dump(exclude={"id"}))
    fields = ", ".join(prepared_data.keys())
    values = ", ".join(
        f"'{value}'" if value else "NULL" for value in prepared_data.values()
    )
    sql = f"INSERT INTO {self._get_table_name()} ({fields}) VALUES ({values})"
    cursor = execute_sql(sql)
    cursor.connection.close()
    self.id = cursor.lastrowid
    self._update_many_to_many_intermediate_table()
    return self
