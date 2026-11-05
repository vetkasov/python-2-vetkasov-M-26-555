"""Обработка ошибок, подтверждение, время выполнения и кэш в замыкании."""

import time

import prompt


def preserve_metadata(wrapper, function):
    """Сохранить имя и docstring без дополнительных библиотек."""
    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__
    return wrapper


def handle_db_errors(function):
    """Сообщить об ошибке операции и вернуть управление командному циклу."""

    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (EOFError, KeyboardInterrupt):
            raise
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(str(error))
        except OSError as error:
            print(f"Ошибка работы с файлами: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return preserve_metadata(wrapper, function)


def confirm_action(action_name):
    """Запросить y перед удалением; любой другой ответ отменяет действие."""

    def decorate(function):
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ',
                empty=True,
            )
            if answer != "y":
                print("Операция отменена.")
                return None
            return function(*args, **kwargs)

        return preserve_metadata(wrapper, function)

    return decorate


def log_time(function):
    """Измерить длительность функции монотонными часами."""

    def wrapper(*args, **kwargs):
        started = time.monotonic()
        try:
            return function(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - started
            print(f"Функция {function.__name__} выполнилась за {elapsed:.3f} секунд.")

    return preserve_metadata(wrapper, function)


def create_cacher():
    """Вернуть cache_result с собственным словарём в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Вычислить отсутствующее значение; ошибки не сохранять в кэше."""
        if key not in cache:
            result = value_func()
            if result is None:
                return None
            cache[key] = result
        return cache[key]

    return cache_result
