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

Следующий этап — управление таблицами. Таблицы, CRUD и декораторы
ещё не реализованы в этой версии. Старый проект сохранён отдельно;
новая последовательная история развивается в ветке ver2.

## Демонстрации подготовки

[![01: пакет и приветствие](https://asciinema.org/a/E45WEByPo0QRzsRl.svg)](https://asciinema.org/a/E45WEByPo0QRzsRl)

[![02: подготовка и help/exit](https://asciinema.org/a/Si2gHbeePkOx2aCB.svg)](https://asciinema.org/a/Si2gHbeePkOx2aCB)

Локальные записи: demo/01-package.cast и demo/02-preparation.cast.
В публичных копиях скрыты домашние пути и адрес автора, удалены поля окружения.
Команды и результаты выполнения сохранены.
