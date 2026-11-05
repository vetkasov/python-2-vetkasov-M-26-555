"""Общие настройки базы данных."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
ID_COLUMN = "ID"
VALID_TYPES = {"int": int, "str": str, "bool": bool}
HELP_TEXT = """***Процесс работы с таблицей***
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу
<command> exit - выход из программы
<command> help - справочная информация"""
