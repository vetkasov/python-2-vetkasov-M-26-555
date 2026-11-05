"""Проверки таблиц в собственных временных базах."""

import os
import shlex
import time

import prompt

from primitive_db import engine
from primitive_db.constants import META_FILE
from primitive_db.utils import load_metadata, load_table_data, save_table_data

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXECUTABLE = os.path.join(ROOT, ".venv", "bin", "database")


def run_cli(commands):
    """Запустить настоящий CLI, проверив отсутствие аварии и ANSI."""
    command = f"printf %s {shlex.quote(commands)} | {shlex.quote(EXECUTABLE)}"
    stream = os.popen(command)
    output = stream.read()
    assert stream.close() is None, output
    assert "Traceback" not in output and "\x1b[" not in output, output
    return output


def check_tables():
    """Проверить формат схемы, ошибки, регистр и перезапуск."""
    output = run_cli(
        "create_table users Name:str name:str age:int active:bool\n"
        "create_table users x:str\nlist_tables\nexit\n"
    )
    assert 'Таблица "users" успешно создана со столбцами: ID:int, Name:str, ' in output
    assert 'Ошибка: Таблица "users" уже существует.' in output
    schema = load_metadata(META_FILE)["users"]
    assert list(schema) == ["ID", "Name", "name", "age", "active"]
    assert load_table_data("users") == []
    assert "- users" in run_cli("list_tables\nexit\n")
    for command in (
        "create_table bad name:STR",
        "create_table bad name:float",
        "create_table bad name:str name:int",
        "create_table ../escape name:str",
        "create_table bad ID:str",
        "create_table bad",
        "list_tables extra",
    ):
        output = run_cli(command + "\nexit\n")
        assert "Некорректное значение:" in output, (command, output)
        assert list(load_metadata(META_FILE)) == ["users"]
    run_cli("create_table 123 Name:str\ncreate_table Users name:str\nexit\n")
    assert set(load_metadata(META_FILE)) == {"users", "Users", "123"}
    save_table_data("users", [{"ID": 1, "Name": "A"}])
    output = run_cli("drop_table users\ny\nexit\n")
    assert 'Таблица "users" успешно удалена.' in output
    assert not os.path.exists("data/users.json")
    run_cli("create_table users Name:str\nexit\n")
    assert load_table_data("users") == []
    assert 'Ошибка: Таблица "absent" не существует.' in run_cli(
        "drop_table absent\nexit\n"
    )


def check_failed_drop():
    """Ошибка сохранения схемы не должна удалять записи."""
    engine.execute("create_table protected name:str")
    save_table_data("protected", [{"ID": 1, "name": "A"}])
    original_save = engine.save_metadata
    original_prompt = prompt.string

    def fail_save(*args):
        raise OSError("simulated failure")

    engine.save_metadata = fail_save
    prompt.string = lambda message, **kwargs: "y"
    try:
        try:
            engine.execute("drop_table protected")
        except OSError:
            pass
    finally:
        engine.save_metadata = original_save
        prompt.string = original_prompt
    assert "protected" in load_metadata(META_FILE)
    assert load_table_data("protected") == [{"ID": 1, "name": "A"}]


def isolated(check):
    """Создать и убрать только принадлежащую этой проверке директорию."""
    previous = os.getcwd()
    directory = os.path.join(
        os.environ.get("TMPDIR", "/tmp"),
        f"db-check-{os.getpid()}-{time.monotonic_ns()}",
    )
    os.mkdir(directory)
    os.chdir(directory)
    try:
        check()
        print(f"PASS {check.__name__}")
    finally:
        os.chdir(previous)
        for parent, directories, files in os.walk(directory, topdown=False):
            for name in files:
                os.remove(os.path.join(parent, name))
            for name in directories:
                os.rmdir(os.path.join(parent, name))
        os.rmdir(directory)


if __name__ == "__main__":
    isolated(check_tables)
    isolated(check_failed_drop)
