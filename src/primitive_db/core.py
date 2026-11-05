"""Создание, проверка и удаление схем таблиц."""

from primitive_db.constants import ID_COLUMN, VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data, validate_name


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


@handle_db_errors
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


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Вернуть метаданные без существующей таблицы."""
    get_schema(metadata, table_name)
    updated = dict(metadata)
    del updated[table_name]
    return updated


def validate_values(schema, values, allow_id=True):
    """Проверить существование столбцов и строгие типы значений."""
    for name, value in values.items():
        if name not in schema:
            raise KeyError(name)
        if not allow_id and name == ID_COLUMN:
            raise ValueError("Некорректное значение: ID. Попробуйте снова.")
        if type(value) is not VALID_TYPES[schema[name]]:
            raise ValueError(f"Некорректное значение: {value}. Попробуйте снова.")


def read_rows(schema, table_name):
    """Прочитать записи и не допустить перезаписи повреждённых данных."""
    rows = load_table_data(table_name)
    identifiers = set()
    for row in rows:
        if set(row) != set(schema):
            raise ValueError("Ошибка: Структура записи не соответствует схеме.")
        validate_values(schema, row)
        identifier = row[ID_COLUMN]
        if identifier < 1 or identifier in identifiers:
            raise ValueError("Ошибка: Некорректный ID записи.")
        identifiers.add(identifier)
    return rows


def matches(row, where_clause):
    """Проверить равенство с учётом точного типа значения."""
    return all(
        type(row[name]) is type(value) and row[name] == value
        for name, value in (where_clause or {}).items()
    )


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Создать запись с автоматическим уникальным ID."""
    schema = get_schema(metadata, table_name)
    columns = [name for name in schema if name != ID_COLUMN]
    if len(columns) != len(values):
        raise ValueError(f"Некорректное значение: {values}. Попробуйте снова.")
    record = dict(zip(columns, values))
    validate_values(schema, record)
    rows = read_rows(schema, table_name)
    identifier = max((row[ID_COLUMN] for row in rows), default=0) + 1
    rows.append({ID_COLUMN: identifier, **record})
    return rows


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Вернуть копии подходящих записей либо всех записей."""
    return [dict(row) for row in table_data if matches(row, where_clause)]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновить копии только подходящих записей."""
    updated = []
    for row in table_data:
        record = dict(row)
        if matches(row, where_clause):
            record.update(set_clause)
        updated.append(record)
    return updated


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Вернуть записи, которые не соответствуют условию удаления."""
    return [dict(row) for row in table_data if not matches(row, where_clause)]
