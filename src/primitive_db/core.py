"""Создание, проверка и удаление схем таблиц."""

from primitive_db.constants import ID_COLUMN, VALID_TYPES
from primitive_db.utils import validate_name


def get_schema(metadata, table_name):
    """Получить схему существующей таблицы."""
    validate_name(table_name)
    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')
    schema = metadata[table_name]
    if not isinstance(schema, dict) or not schema or next(iter(schema)) != ID_COLUMN:
        raise ValueError("Ошибка: Некорректная схема таблицы.")
    if schema[ID_COLUMN] != "int" or any(
        not isinstance(type_name, str) or type_name not in VALID_TYPES
        for type_name in schema.values()
    ):
        raise ValueError("Ошибка: Некорректная схема таблицы.")
    return schema


def create_table(metadata, table_name, columns):
    """Вернуть новые метаданные с проверенной схемой и первым ID:int."""
    validate_name(table_name)
    if table_name in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" уже существует.')
    if not columns:
        raise ValueError(
            "Некорректное значение: пустой список столбцов. Попробуйте снова."
        )
    schema = {ID_COLUMN: "int"}
    explicit_id = False
    for column in columns:
        parts = column.split(":")
        if len(parts) != 2:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")
        name, type_name = parts
        validate_name(name)
        if type_name not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")
        if name == ID_COLUMN and type_name == "int" and not explicit_id:
            explicit_id = True
            continue
        if name in schema:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")
        schema[name] = type_name
    updated = dict(metadata)
    updated[table_name] = schema
    return updated


def drop_table(metadata, table_name):
    """Вернуть метаданные без существующей таблицы."""
    get_schema(metadata, table_name)
    updated = dict(metadata)
    del updated[table_name]
    return updated
