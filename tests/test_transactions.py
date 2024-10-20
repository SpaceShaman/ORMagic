from ormagic import transaction


def test_is_under_transaction():
    with transaction():
        assert transaction._is_transaction is True

    assert transaction._is_transaction is False
