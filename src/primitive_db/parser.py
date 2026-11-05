"""Строгий разбор команд без SQL-библиотек и выполнения кода."""

from primitive_db.constants import COMMAND_NAMES
from primitive_db.utils import validate_name


def tokenize(text):
    """Сохранить тип токена, пробелы и пунктуацию внутри строк."""
    tokens = []
    index = 0
    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
        elif char in "(),=":
            tokens.append(("symbol", char))
            index += 1
        elif char in "\"'":
            quote = char
            value = ""
            index += 1
            while index < len(text) and text[index] != quote:
                if (
                    text[index] == "\\"
                    and index + 1 < len(text)
                    and text[index + 1] in (quote, "\\")
                ):
                    index += 1
                value += text[index]
                index += 1
            if index == len(text):
                raise ValueError("Незакрытая строка")
            tokens.append(("string", value))
            index += 1
        else:
            start = index
            while (
                index < len(text)
                and not text[index].isspace()
                and text[index] not in "(),=\"'"
            ):
                index += 1
            tokens.append(("word", text[start:index]))
    return tokens


def word(token, expected=None):
    """Прочитать некавыченный токен, при необходимости — ключевое слово."""
    if token[0] != "word" or (expected is not None and token[1] != expected):
        raise ValueError("Некорректный токен")
    return token[1]


def parse_value(token):
    """Разобрать строку, строгое целое число или bool любого регистра."""
    kind, value = token
    if kind == "string":
        return value
    if kind == "word":
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        digits = value[1:] if value[:1] in ("+", "-") else value
        if digits and all(char in "0123456789" for char in digits):
            return int(value)
    raise ValueError("Некорректное значение")


def parse_condition(tokens):
    """Разобрать ровно одно равенство столбец = значение."""
    if len(tokens) != 3 or tokens[1] != ("symbol", "="):
        raise ValueError("Некорректное условие")
    name = validate_name(word(tokens[0]))
    return {name: parse_value(tokens[2])}


def parse_tokens(tokens):
    """Проверить точную структуру команды и отсутствие лишних токенов."""
    command = word(tokens[0])
    result = {"command": command}
    if command not in COMMAND_NAMES:
        return {"command": "unknown", "name": command}
    if command in ("help", "exit", "list_tables"):
        if len(tokens) != 1:
            raise ValueError("Лишние аргументы")
        return result
    if command == "create_table":
        if len(tokens) < 3:
            raise ValueError("Отсутствуют столбцы")
        result["table"] = validate_name(word(tokens[1]))
        result["columns"] = [word(token) for token in tokens[2:]]
        return result
    if command in ("drop_table", "info"):
        if len(tokens) != 2:
            raise ValueError("Неверное число аргументов")
        result["table"] = validate_name(word(tokens[1]))
        return result
    if command == "update":
        if len(tokens) != 10:
            raise ValueError("Неверная структура update")
        result["table"] = validate_name(word(tokens[1]))
        word(tokens[2], "set")
        word(tokens[6], "where")
        result["set"] = parse_condition(tokens[3:6])
        result["where"] = parse_condition(tokens[7:])
        return result
    word(tokens[1], "into" if command == "insert" else "from")
    result["table"] = validate_name(word(tokens[2]))
    if command == "insert":
        word(tokens[3], "values")
        if tokens[4] != ("symbol", "(") or tokens[-1] != ("symbol", ")"):
            raise ValueError("Нужна одна группа значений")
        values = tokens[5:-1]
        if values and len(values) % 2 == 0:
            raise ValueError("Неполный список значений")
        if any(token != ("symbol", ",") for token in values[1::2]):
            raise ValueError("Отсутствует запятая")
        result["values"] = [parse_value(token) for token in values[::2]]
    elif len(tokens) == 3 and command == "select":
        result["where"] = None
    else:
        if len(tokens) != 7:
            raise ValueError("Неверная структура where")
        word(tokens[3], "where")
        result["where"] = parse_condition(tokens[4:])
    return result


def parse_command(text):
    """Отклонить весь некорректный ввод до выполнения операции."""
    try:
        tokens = tokenize(text)
        return parse_tokens(tokens) if tokens else {"command": "empty"}
    except (ValueError, IndexError) as error:
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.") from error
