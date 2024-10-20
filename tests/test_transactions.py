from ormagic import DBModel, transaction


def test_is_under_transaction():
    with transaction():
        assert transaction._is_transaction is True

    assert transaction._is_transaction is False


def test_save_multiple_objects_under_transaction():
    class TestModel(DBModel):
        name: str

    TestModel.create_table()

    with transaction():
        TestModel(name="test").save()
        TestModel(name="test").save()

    assert len(TestModel.all()) == 2


def test_try_to_save_multiple_objects_with_rollbacks():
    class TestModel(DBModel):
        name: str

    TestModel.create_table()

    try:
        TestModel(name="test").save()
        with transaction():
            TestModel(name="test").save()
            TestModel(name="test").save()
            TestModel().save()  # type: ignore
    except Exception:
        pass
    finally:
        assert len(TestModel.all()) == 1
