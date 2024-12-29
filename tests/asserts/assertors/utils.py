from .asseror import Column, ForeignKey


def get_expected_column(expected_columns: list[Column], column_name: str) -> Column:
    return next(filter(lambda c: c.name == column_name, expected_columns))


def get_expected_foreign_key(
    expected_foreign_keys: list[ForeignKey], column_name: str
) -> ForeignKey:
    return next(filter(lambda fk: fk.column_name == column_name, expected_foreign_keys))
