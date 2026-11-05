"""Проверки CRUD и строгой грамматики команд."""

import os

from check_tables import isolated, run_cli

from primitive_db import engine, utils
from primitive_db.parser import parse_command


def check_crud():
    """Проверить полный цикл, порядок полей, типы и сохранение."""
    output = run_cli(
        "create_table users name:str age:int active:bool\n"
        'insert into users values ("Sergei",28,TRUE)\n'
        'insert into users values ( "Ivanov, Ivan" , 22 , false )\n'
        'select from users\nupdate users set age=29 where name="Sergei"\n'
        "select from users where ID=1\ninfo users\nexit\n"
    )
    assert 'Запись с ID=1 успешно добавлена в таблицу "users".' in output
    assert 'Запись с ID=1 в таблице "users" успешно обновлена.' in output
    assert "| ID |" in output and "Ivanov, Ivan" in output
    assert "Столбцы: ID:int, name:str, age:int, active:bool" in output
    assert "Количество записей: 2" in output
    rows = utils.load_table_data("users")
    assert rows[0] == {"ID": 1, "name": "Sergei", "age": 29, "active": True}
    assert rows[1]["name"] == "Ivanov, Ivan"
    assert "Sergei" in run_cli("select from users where age=29\nexit\n")
    invalid = [
        'insert into users values ("Bad", "28", true)',
        'insert into users values ("Bad", true, false)',
        'insert into users values ("Bad", 1)',
        "insert into users values (Sergei, 1, true)",
        'insert into users values ("A",1,true),("B",2,false)',
        'insert into users other values ("A",1,true)',
        'insert into users,other values ("A",1,true)',
        'insert into users values "A",1,true',
        'insert into users values ("A",1,true) extra',
        'insert into users VALUES ("A",1,true)',
        'insert INTO users values ("A",1,true)',
        'update users set age="29" where ID=1',
        "update users set ID=10 where ID=1",
        "update users set age=30",
        'select from users where age="29"',
        "select from users where age=true",
        "select from users users",
        "select from users where age=29 extra",
        "delete from users",
        "delete from users where ID=1 extra",
        "update users set age=30 where ID=1 extra",
        'insert into users values ("unterminated,1,true)',
        'insert into users values ("A",1,true,)',
    ]
    for command in invalid:
        output = run_cli(command + "\nexit\n")
        assert "Некорректное значение:" in output, (command, output)
        assert utils.load_table_data("users") == rows, command
    for command in (
        "select from users where absent=1",
        "update users set absent=1 where ID=1",
        "delete from users where absent=1",
    ):
        assert "не найден" in run_cli(command + "\nexit\n")
        assert utils.load_table_data("users") == rows
    assert "Функции SELECT нет." in run_cli("SELECT from users\nexit\n")
    output = run_cli("delete from users where ID=1\ny\nexit\n")
    assert 'Запись с ID=1 успешно удалена из таблицы "users".' in output
    run_cli('insert into users values ("Next", 40, True)\nexit\n')
    assert [row["ID"] for row in utils.load_table_data("users")] == [2, 3]


def check_parser_strings():
    """Сохранить содержимое строк и поддержать имена-ключевые слова."""
    command = r'insert into users values ("a\"b", -2, fAlSe)'
    assert parse_command(command)["values"] == ['a"b', -2, False]
    command = r'insert into users values ("C:\new\test", 2, true)'
    assert parse_command(command)["values"][0] == r"C:\new\test"
    request = parse_command('insert into users values ("  x, where = (y)  ",0,true)')
    assert request["values"][0] == "  x, where = (y)  "
    run_cli(
        "create_table words where:int set:str values:bool\n"
        'insert into words values (1,"x",true)\n'
        'update words set where=2 where set="x"\nexit\n'
    )
    assert utils.load_table_data("words")[0]["where"] == 2


def check_case_sensitive_tables():
    """Таблицы users и Users не должны разделять файл на macOS."""
    run_cli(
        "create_table users Name:str name:str\n"
        "create_table Users Name:str name:str\n"
        'insert into users values ("lower","a")\n'
        'insert into Users values ("upper","b")\nexit\n'
    )
    assert utils.load_table_data("users")[0]["Name"] == "lower"
    assert utils.load_table_data("Users")[0]["Name"] == "upper"
    assert utils.table_path("users").lower() != utils.table_path("Users").lower()


def check_empty_and_failed_writes():
    """Валидировать пустые таблицы и не перезаписывать данные при ошибке."""
    run_cli("create_table users name:str age:int active:bool\nexit\n")
    assert "| ID |" in run_cli("select from users\nexit\n")
    assert "не найден" in run_cli("select from users where absent=1\nexit\n")
    assert "Некорректное значение:" in run_cli(
        'update users set age="x" where ID=99\nexit\n'
    )
    run_cli('insert into users values ("A",1,true)\nexit\n')
    before = utils.load_table_data("users")
    original = utils.os.replace

    def fail_replace(*args):
        raise OSError("simulated replace failure")

    utils.os.replace = fail_replace
    try:
        try:
            engine.execute('insert into users values ("B",2,false)')
        except OSError:
            pass
    finally:
        utils.os.replace = original
    assert utils.load_table_data("users") == before
    assert os.listdir("data") == ["users.json"]
    with open("data/users.json", "w") as target:
        target.write("{invalid")
    output = run_cli('insert into users values ("B",2,false)\nexit\n')
    assert "Некорректный JSON" in output
    with open("data/users.json") as source:
        assert source.read() == "{invalid"


if __name__ == "__main__":
    for check in (
        check_crud,
        check_parser_strings,
        check_case_sensitive_tables,
        check_empty_and_failed_writes,
    ):
        isolated(check)
