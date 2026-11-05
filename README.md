# Примитивная база данных

Арсений Веткасов, M-26-555.
[Репозиторий](https://github.com/vetkasov/python2-vetkasov-M-26-555).

## Этап 1. Подготовка

Проект начат с пустой рабочей папки командой
`uv init --package --name primitive_db --python 3.12 .`.
Первый рабочий коммит с приветствием сохранён тегом `v2/01-package`.
На текущем шаге добавлен цикл с командами `help` и `exit`.
Внешняя зависимость приложения — `prompt`; `ruff` установлен для разработки.

```bash
uv sync
uv run database
```

Равнозначные способы запуска: `uv run project`,
`uv run python -m primitive_db.main`, `make run`.
Команды пишутся строчными. `help` повторяет справку, `exit` завершает работу.
Ctrl+C и конец ввода также завершают цикл.

## Проверка и установка пакета

```bash
make lint
make build
make publish-dry-run
uv tool install dist/*.whl
database
```

Makefile использует `uv build --clear`: устаревшие сборки из dist удаляются
перед новой сборкой. `uv publish --dry-run --trusted-publishing never`
проверяет пакет без загрузки; автоматический поиск OIDC-токена отключён.
Фиктивные токены и пароли не используются. В интерактивном терминале uv
может запросить учётные данные даже при dry-run; проверку выполняем
без управляющего терминала, с закрытым вводом, без передачи учётных данных.

Имя дистрибутива — `project-2-vetkasov-m-26-555`, импортируемый пакет —
`primitive_db`; для этого явно настроен `module-name` сборщика uv.
Python >=3.12, зависимости зафиксированы в uv.lock.
Пути data/ и db_meta.json заранее добавлены в .gitignore.

Подготовка завершена. Новая последовательная история развивается в ветке ver2;
прежняя реализация сохранена отдельно.

## Демонстрации подготовки

[![01: пакет и приветствие](https://asciinema.org/a/E45WEByPo0QRzsRl.svg)](https://asciinema.org/a/E45WEByPo0QRzsRl)

[![02: подготовка и help/exit](https://asciinema.org/a/Si2gHbeePkOx2aCB.svg)](https://asciinema.org/a/Si2gHbeePkOx2aCB)

Локальные записи: demo/01-package.cast и demo/02-preparation.cast.
В публичных копиях скрыты домашние пути и адрес автора, удалены поля окружения.
Команды и результаты выполнения сохранены.

## Этап 2. Управление таблицами

```text
create_table users name:str age:int is_active:bool
list_tables
drop_table users
```

Схема хранится в db_meta.json как словарь «таблица → столбец → тип».
ID:int всегда первый. Имена регистрозависимы, состоят из латиницы, цифр и _.
Типы — только int, str, bool. Файлы записей создаются при первом insert
на следующем этапе. При удалении таблицы файл физически удаляется, если есть.
Ошибка сохранения схемы не удаляет файл записей.

Проверки: `uv run python tests/check_tables.py`.

[![03: управление таблицами](https://asciinema.org/a/stYf1EwL6AHJBDdW.svg)](https://asciinema.org/a/stYf1EwL6AHJBDdW)

Локальная запись: demo/03-tables.cast.

## Этап 3. CRUD

```text
insert into users values ("Sergei", 28, true)
select from users
select from users where age = 28
update users set age = 29 where name = "Sergei"
delete from users where ID = 1
info users
```

Одна команда insert добавляет одну запись в одну таблицу. Строки только
в кавычках; числа и bool — без кавычек. Булевы значения любого регистра,
ключевые слова команд только строчными. where — одно равенство; update
изменяет один столбец. Несколько групп values и лишние токены запрещены.
ID генерируется автоматически как max существующих ID + 1; изменять ID нельзя.
Все пользовательские поля обязательны. Пробелы и запятые внутри строк
сохраняются; поддерживаются экранированные кавычки и обратный слеш.

Данные хранятся в data/<имя>.json. Чтобы имена users и Users различались
на macOS, заглавные буквы в именах файлов кодируются как %XX; например,
Users хранится в data/%55sers.json, а users — в data/users.json.

Проверки: `uv run python tests/check_crud.py`.

[![04: CRUD](https://asciinema.org/a/2Usx0bbE0PljE3XA.svg)](https://asciinema.org/a/2Usx0bbE0PljE3XA)

Локальная запись: demo/04-crud.cast. Подтверждение удаления и кэш
будут добавлены на следующем этапе.
