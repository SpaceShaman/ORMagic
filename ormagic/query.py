from .field_utils import prepare_where_conditions


class Q:
    def __init__(self, **kwargs):
        self.conditions, self.params = prepare_where_conditions(**kwargs)

    def __or__(self, other: "Q") -> "Q":
        self.conditions = f"{self.conditions} OR {other.conditions}"
        self.params.extend(other.params)
        return self

    def __and__(self, other: "Q") -> "Q":
        self.conditions = f"{self.conditions} AND {other.conditions}"
        self.params.extend(other.params)
        return self

    def __invert__(self) -> "Q":
        self.conditions = f"NOT ({self.conditions})"
        return self
