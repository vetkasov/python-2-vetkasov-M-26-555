"""Проверки подтверждений, ошибок и кэширования."""

import prompt
from check_tables import isolated, run_cli

from primitive_db import core, engine, utils
from primitive_db.constants import META_FILE
from primitive_db.decorators import create_cacher


def check_confirmation_and_timing():
    """Отмена и Y не удаляют данные; y выполняет удаление."""
    output = run_cli(
        'create_table users name:str\ninsert into users values ("A")\n'
        "delete from users where ID=1\nn\ndrop_table users\nY\n"
        "select from users\nexit\n"
    )
    assert output.count("Операция отменена.") == 2
    assert "Функция insert выполнилась за " in output
    assert "Функция select выполнилась за " in output
    assert utils.load_table_data("users") == [{"ID": 1, "name": "A"}]
    assert "users" in utils.load_metadata(META_FILE)
    for command in ("delete from users where ID=1", "drop_table users"):
        blank = run_cli(command + "\n\nlist_tables\nexit\n")
        assert "Операция отменена." in blank and "- users" in blank
        assert utils.load_table_data("users") == [{"ID": 1, "name": "A"}]
    run_cli("\n" * 1200 + "exit\n")
    output = run_cli("delete from users where ID=1\ny\ndrop_table users\ny\nexit\n")
    assert 'Запись с ID=1 успешно удалена из таблицы "users".' in output
    assert 'Таблица "users" успешно удалена.' in output
    assert core.select.__name__ == "select" and core.insert.__name__ == "insert"


def check_cacher_closure():
    """Повторный ключ переиспользует результат; ошибка None не кэшируется."""
    cache = create_cacher()
    calls = []

    def compute():
        calls.append(1)
        return {"answer": 42}

    assert cache("a", compute) == {"answer": 42}
    assert cache("a", compute) == {"answer": 42}
    assert calls == [1]
    assert cache("b", lambda: None) is None
    assert cache("b", compute) == {"answer": 42}
    assert calls == [1, 1]
    assert create_cacher()("a", lambda: 99) == 99


def check_cache_keys_and_invalidation():
    """Различать таблицы/условия и сбрасывать кэш после сохранённых изменений."""
    original_select = core.select
    original_prompt = prompt.string
    calls = []

    def counted_select(*args):
        calls.append(1)
        return original_select(*args)

    core.select = counted_select
    prompt.string = lambda message, **kwargs: "y"
    try:
        engine.execute("create_table a value:int")
        engine.execute("create_table b value:int")
        engine.execute("insert into a values (1)")
        engine.execute("insert into b values (2)")
        metadata = utils.load_metadata(META_FILE)
        schema = metadata["a"]
        assert engine.select_rows(schema, "a", {"ID": 1})[0]["value"] == 1
        assert engine.select_rows(schema, "a", {"ID": 1})[0]["value"] == 1
        assert len(calls) == 1
        assert engine.select_rows(schema, "a", None)[0]["value"] == 1
        assert len(calls) == 2
        assert engine.select_rows(metadata["b"], "b", {"ID": 1})[0]["value"] == 2
        assert len(calls) == 3
        engine.execute("insert into a values (3)")
        assert len(engine.select_rows(schema, "a", None)) == 2
        assert len(calls) == 4
        engine.execute("update a set value=4 where ID=1")
        assert engine.select_rows(schema, "a", {"ID": 1})[0]["value"] == 4
        assert len(calls) == 5
        original_save = engine.save_table_data

        def fail_save(*args):
            raise OSError("simulated data save failure")

        engine.save_table_data = fail_save
        try:
            engine.execute("update a set value=9 where ID=1")
        finally:
            engine.save_table_data = original_save
        assert engine.select_rows(schema, "a", {"ID": 1})[0]["value"] == 4
        assert len(calls) == 5
        prompt.string = lambda message, **kwargs: "n"
        engine.execute("delete from a where ID=1")
        assert engine.select_rows(schema, "a", {"ID": 1})[0]["value"] == 4
        assert len(calls) == 5
        prompt.string = lambda message, **kwargs: "y"
        engine.execute("delete from a where ID=1")
        assert engine.select_rows(schema, "a", {"ID": 1}) == []
        assert len(calls) == 6
        engine.execute("drop_table a")
        engine.execute("create_table a value:int")
        assert engine.select_rows(schema, "a", None) == []
        assert len(calls) == 7
    finally:
        core.select = original_select
        prompt.string = original_prompt


def check_failed_file_removal():
    """Если файл нельзя удалить, восстановить схему и сохранить записи."""
    engine.execute("create_table users name:str")
    engine.execute('insert into users values ("A")')
    original_remove = engine.remove_table_data
    original_prompt = prompt.string

    def fail_remove(*args):
        raise OSError("simulated removal failure")

    engine.remove_table_data = fail_remove
    prompt.string = lambda message, **kwargs: "y"
    try:
        engine.execute("drop_table users")
    finally:
        engine.remove_table_data = original_remove
        prompt.string = original_prompt
    assert "users" in utils.load_metadata(META_FILE)
    assert utils.load_table_data("users") == [{"ID": 1, "name": "A"}]


if __name__ == "__main__":
    for check in (
        check_confirmation_and_timing,
        check_cacher_closure,
        check_cache_keys_and_invalidation,
        check_failed_file_removal,
    ):
        isolated(check)
