"""Приветствие и командный цикл первого этапа."""

import prompt


def print_help():
    """Показать команды, доступные на этапе подготовки."""
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def welcome():
    """Запрашивать команды до exit, конца ввода или прерывания."""
    print("Первая попытка запустить проект!")
    print_help()

    while True:
        try:
            command = prompt.string("Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if command == "exit":
            break
        if command == "help":
            print_help()
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
