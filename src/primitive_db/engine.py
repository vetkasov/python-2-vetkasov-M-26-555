"""Командный цикл и сохранение результатов операций."""

import json

import prompt
from prettytable import PrettyTable

from primitive_db import core
from primitive_db.constants import COMMAND_PROMPT, HELP_TEXT, ID_COLUMN, META_FILE
from primitive_db.decorators import create_cacher, handle_db_errors
from primitive_db.parser import parse_command
from primitive_db.utils import (
    load_metadata,
    remove_table_data,
    save_metadata,
    save_table_data,
)

_cache_result = create_cacher()


def reset_cache():
    """Заменить кэшер после успешно сохранённого изменения базы."""
    global _cache_result
    _cache_result = create_cacher()


def select_rows(schema, name, where):
    """Кэшировать запрос по имени таблицы и стабильному условию."""
    key = json.dumps([name, where], sort_keys=True, ensure_ascii=False)
    return _cache_result(key, lambda: core.select(core.read_rows(schema, name), where))


def print_help():
    """Показать команды текущего этапа."""
    print(HELP_TEXT)


def format_columns(schema):
    """Вывести столбцы в порядке схемы в формате имя:тип."""
    return ", ".join(f"{name}:{type_name}" for name, type_name in schema.items())


def manage_table(metadata, request):
    """Сохранить изменение схемы и обработать физическое удаление данных."""
    name = request["table"]
    if request["command"] == "create_table":
        updated = core.create_table(metadata, name, request["columns"])
        if updated is None:
            return
        save_metadata(META_FILE, updated)
        reset_cache()
        columns = format_columns(updated[name])
        print(f'Таблица "{name}" успешно создана со столбцами: {columns}')
    else:
        core.get_schema(metadata, name)
        updated = core.drop_table(metadata, name)
        if updated is None:
            return
        save_metadata(META_FILE, updated)
        try:
            remove_table_data(name)
        except OSError:
            save_metadata(META_FILE, metadata)
            raise
        reset_cache()
        print(f'Таблица "{name}" успешно удалена.')


def display_rows(schema, rows):
    """Вывести PrettyTable, сохранив порядок столбцов и первый ID."""
    table = PrettyTable()
    table.field_names = list(schema)
    for row in rows:
        table.add_row([row[name] for name in schema])
    print(table)


def operate_rows(metadata, request):
    """Проверить схему и сохранить успешную операцию с записями."""
    command, name = request["command"], request["table"]
    schema = core.get_schema(metadata, name)
    if command == "insert":
        updated = core.insert(metadata, name, request["values"])
        if updated is None:
            return
        save_table_data(name, updated)
        reset_cache()
        identifier = updated[-1][ID_COLUMN]
        print(f'Запись с ID={identifier} успешно добавлена в таблицу "{name}".')
        return
    if command == "info":
        rows = core.read_rows(schema, name)
        print(f"Таблица: {name}")
        print(f"Столбцы: {format_columns(schema)}")
        print(f"Количество записей: {len(rows)}")
        return
    where = request["where"]
    core.validate_values(schema, where or {})
    if command == "select":
        rows = select_rows(schema, name, where)
        if rows is not None:
            display_rows(schema, rows)
        return
    rows = core.read_rows(schema, name)
    if command == "update":
        core.validate_values(schema, request["set"], allow_id=False)
        updated = core.update(rows, request["set"], where)
    else:
        updated = core.delete(rows, where)
    if updated is None:
        return
    save_table_data(name, updated)
    reset_cache()
    for row in rows:
        if core.matches(row, where):
            identifier = row[ID_COLUMN]
            if command == "update":
                print(f'Запись с ID={identifier} в таблице "{name}" успешно обновлена.')
            else:
                print(f'Запись с ID={identifier} успешно удалена из таблицы "{name}".')


@handle_db_errors
def execute(text):
    """Выполнить команду; False означает завершение цикла."""
    request = parse_command(text)
    command = request["command"]
    if command == "exit":
        return False
    if command == "unknown":
        print(f"Функции {request['name']} нет. Попробуйте снова.")
        return True
    if command in {"empty", "help"}:
        if command == "help":
            print_help()
        return True
    metadata = load_metadata(META_FILE)
    if command == "list_tables":
        for name in metadata:
            print(f"- {name}")
    elif command in ("create_table", "drop_table"):
        manage_table(metadata, request)
    else:
        operate_rows(metadata, request)
    return True


def run():
    """Читать команды до exit, EOF или Ctrl+C."""
    print_help()
    while True:
        try:
            text = prompt.string(COMMAND_PROMPT, empty=True)
            if execute(text or "") is False:
                break
        except (EOFError, KeyboardInterrupt):
            print()
            break
