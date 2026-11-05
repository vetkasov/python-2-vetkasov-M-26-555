"""Командный цикл и сохранение результатов операций."""

import prompt

from primitive_db import core
from primitive_db.constants import HELP_TEXT, META_FILE
from primitive_db.parser import parse_command
from primitive_db.utils import load_metadata, remove_table_data, save_metadata


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
        save_metadata(META_FILE, updated)
        columns = format_columns(updated[name])
        print(f'Таблица "{name}" успешно создана со столбцами: {columns}')
    else:
        updated = core.drop_table(metadata, name)
        save_metadata(META_FILE, updated)
        try:
            remove_table_data(name)
        except OSError:
            save_metadata(META_FILE, metadata)
            raise
        print(f'Таблица "{name}" успешно удалена.')


def execute(text):
    """Выполнить команду; False означает завершение цикла."""
    request = parse_command(text)
    command = request["command"]
    if command == "exit":
        return False
    if command in {"empty", "help"}:
        if command == "help":
            print_help()
        return True
    metadata = load_metadata(META_FILE)
    if command == "list_tables":
        for name in metadata:
            print(f"- {name}")
    else:
        manage_table(metadata, request)
    return True


def run():
    """Читать команды до exit, EOF или Ctrl+C."""
    print_help()
    while True:
        try:
            text = prompt.string("Введите команду: ")
            if execute(text) is False:
                break
        except (EOFError, KeyboardInterrupt):
            print()
            break
        except (ValueError, KeyError) as error:
            print(str(error))
        except OSError as error:
            print(f"Ошибка работы с файлами: {error}")
