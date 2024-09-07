from ormagic import DBModel, transaction


def test_model_is_transaction_if_in_transaction():
    class User(DBModel):
        name: str

    with transaction():
        user = User(name="Alice")
        assert user._is_transaction is True

    assert user._is_transaction is False
