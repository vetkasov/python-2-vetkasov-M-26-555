"""Разбор команд управления таблицами."""

import shlex

from primitive_db.utils import validate_name


def parse_command(text):
    """Проверить команду, количество аргументов и имя таблицы."""
    try:
        tokens = shlex.split(text)
    except ValueError as error:
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.") from error
    if not tokens:
        return {"command": "empty"}
    command = tokens[0]
    result = {"command": command}
    if command not in {"create_table", "list_tables", "drop_table", "help", "exit"}:
        raise ValueError(f"Функции {command} нет. Попробуйте снова.")
    if command in {"help", "exit", "list_tables"}:
        if len(tokens) != 1:
            raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")
    else:
        if len(tokens) < 2 or (command == "drop_table" and len(tokens) != 2):
            raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")
        result["table"] = validate_name(tokens[1])
        result["columns"] = tokens[2:]
    return result
