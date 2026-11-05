.PHONY: install run lint format build publish-dry-run test check

install:
	uv sync

run:
	uv run project

lint:
	uv run ruff check .

format:
	uv run ruff format .

build:
	uv build --clear

publish-dry-run: build
	bash -o pipefail -c \
	  'uv publish --dry-run --trusted-publishing never < /dev/null 2>&1 | cat'

test:
	uv run python .github/checks/check_tables.py
	uv run python .github/checks/check_crud.py
	uv run python .github/checks/check_decorators.py

check: lint test publish-dry-run
