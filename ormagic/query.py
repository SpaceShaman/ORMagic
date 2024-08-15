from .field_utils import prepare_where_conditions


class Q:
    def __init__(self, *args, **kwargs):
        self.conditions, self.params = prepare_where_conditions(**kwargs)
        for arg in args:
            if isinstance(arg, Q):
                if self.conditions:
                    self.conditions += f" AND {arg.conditions}"
                else:
                    self.conditions = arg.conditions
                self.params.extend(arg.params)
        if len(self.params) > 1:
            self.conditions = f"({self.conditions})"

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
