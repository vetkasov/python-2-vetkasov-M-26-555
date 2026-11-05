"""Общие настройки базы данных."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
ID_COLUMN = "ID"
FILE_MODE = 0o600
COMMAND_PROMPT = "Введите команду: "
NAME_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
COMMAND_NAMES = {
    "create_table",
    "list_tables",
    "drop_table",
    "insert",
    "select",
    "update",
    "delete",
    "info",
    "help",
    "exit",
}
VALID_TYPES = {"int": int, "str": str, "bool": bool}
HELP_TEXT = (
    "***Операции с данными***\nФункции:\n"
    "<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу\n"
    "<command> list_tables - показать список всех таблиц\n"
    "<command> drop_table <имя_таблицы> - удалить таблицу\n"
    "<command> insert into <имя_таблицы> values (<значение1>, ...) - создать запись.\n"
    "<command> select from <имя_таблицы> where <столбец> = <значение> "
    "- прочитать записи по условию.\n"
    "<command> select from <имя_таблицы> - прочитать все записи.\n"
    "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
    "where <столбец_условия> = <значение_условия> - обновить запись.\n"
    "<command> delete from <имя_таблицы> where <столбец> = <значение> "
    "- удалить запись.\n"
    "<command> info <имя_таблицы> - вывести информацию о таблице.\n"
    "<command> exit - выход из программы\n"
    "<command> help - справочная информация"
)
