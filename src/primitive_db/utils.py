"""Чтение, атомарная запись и удаление файлов базы данных."""

import json
import os
import time

from primitive_db.constants import DATA_DIR


def validate_name(name):
    """Разрешить только непустое имя из латиницы, цифр и подчёркивания."""
    if not name or any(
        char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        for char in name
    ):
        raise ValueError(f"Некорректное значение: {name}. Попробуйте снова.")
    return name


def read_json(filepath, default):
    """Вернуть значение по умолчанию только при отсутствии файла."""
    try:
        with open(filepath, encoding="utf-8") as source:
            return json.load(source)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError as error:
        raise ValueError(f"Ошибка: Некорректный JSON в файле {filepath}.") from error


def write_json(filepath, data):
    """Заменить файл после полной успешной записи временного файла."""
    parent = os.path.dirname(filepath)
    if parent:
        os.makedirs(parent, exist_ok=True)
    temporary = f"{filepath}.{os.getpid()}.{time.monotonic_ns()}.tmp"
    descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as target:
            json.dump(data, target, ensure_ascii=False, indent=2)
            target.write("\n")
        os.replace(temporary, filepath)
    finally:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass


def load_metadata(filepath):
    """Загрузить схемы таблиц или пустой словарь при первом запуске."""
    metadata = read_json(filepath, {})
    if not isinstance(metadata, dict):
        raise ValueError("Ошибка: Некорректный файл метаданных.")
    return metadata


def save_metadata(filepath, data):
    """Сохранить схемы таблиц."""
    write_json(filepath, data)


def table_path(table_name):
    """Сформировать безопасный путь к данным таблицы."""
    validate_name(table_name)
    filename = "".join(
        f"%{ord(char):02x}" if char.isupper() else char for char in table_name
    )
    return os.path.join(DATA_DIR, f"{filename}.json")


def load_table_data(table_name):
    """Загрузить записи или пустой список при отсутствии файла."""
    rows = read_json(table_path(table_name), [])
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Ошибка: Некорректный файл данных таблицы.")
    return rows


def save_table_data(table_name, data):
    """Сохранить записи одной таблицы."""
    write_json(table_path(table_name), data)


def remove_table_data(table_name):
    """Физически удалить файл; отсутствие файла допустимо."""
    try:
        os.remove(table_path(table_name))
    except FileNotFoundError:
        pass
