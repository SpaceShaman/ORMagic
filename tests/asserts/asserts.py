from .assertors.asseror import Column, ForeignKey, get_assertor


def assert_table_schema(cursor, table_name: str, expected_columns: list[Column]):
    assertor = get_assertor(cursor)
    assertor.assert_table_schema(table_name, expected_columns)


def assert_foreign_keys(
    cursor, table_name: str, expected_foreign_keys: list[ForeignKey]
):
    assertor = get_assertor(cursor)
    assertor.assert_foreign_keys(table_name, expected_foreign_keys)
