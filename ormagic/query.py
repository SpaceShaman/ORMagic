from .field_utils import prepare_where_conditions


class Q:
    def __init__(self, **kwargs):
        self.conditions, self.params = prepare_where_conditions(**kwargs)
