from .field_utils import extract_field_operator


class Q:
    def __init__(self, **kwargs):
        field, operator = extract_field_operator(list(kwargs.keys())[0])
        self.condition = f"{field} {operator} '{list(kwargs.values())[0]}'"
