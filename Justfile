# Development tasks for larpfetch

default: check

dev:
	uv sync

test:
	uv run pytest

test-cov:
	uv run pytest --cov=larpfetch

lint:
	uv run ruff check src/ tests/

fmt:
	uv run ruff format src/ tests/

check: lint test

all: fmt lint test

install:
	uv sync --frozen

publish:
	uv build
	uv publish

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

run:
	uv run larpfetch

run-args *args:
	uv run larpfetch {{ args }}
