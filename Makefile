.PHONY: install run lint format build publish-dry-run check

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

check: lint publish-dry-run
