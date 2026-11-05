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
	uv publish --dry-run --trusted-publishing never

test:
	uv run python tests/check_tables.py
	uv run python tests/check_crud.py
	uv run python tests/check_decorators.py

check: lint test publish-dry-run
