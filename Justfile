# Development tasks for larpfetch

default: check

# Install dev dependencies
dev:
	uv sync --extra dev

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=larpfetch --cov-report=term-missing

# Run tests verbose
test-v:
	uv run pytest -v

# Run a specific test file
test-file file:
	uv run pytest tests/{{ file }} -v

# Run a specific test
test-one name:
	uv run pytest -k "{{ name }}" -v

# Lint
lint:
	uv run ruff check src/ tests/

# Lint and auto-fix
lint-fix:
	uv run ruff check --fix src/ tests/

# Format
fmt:
	uv run ruff format src/ tests/

# Format and check
fmt-check:
	uv run ruff format --check src/ tests/

# Lint + test
check: lint test

# Format + lint + test
all: fmt lint test

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .ruff_cache htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	uv build

# Publish to PyPI (dry run)
publish-dry: build
	uv publish --dry-run

# Publish to PyPI
publish: build
	uv publish

# Current version (reads pyproject.toml)
version:
	@uv run python -c "from larpfetch import __version__; print(__version__)"

# Extract a version's changelog section from CHANGELOG.md
# Usage: just changelog-notes 1.4.0
changelog-notes version:
	@sed -n '/^## v{{ version }}/,/^## v/p' CHANGELOG.md | sed '1d;$d' | sed '/^$$/d'

# Create only the GitHub release for the current version.
# Reads the summary line + section from CHANGELOG.md automatically.
gh-release:
	@bash scripts/release.sh gh-release

# Full release: tag + push, publish to PyPI, create the GitHub release.
release:
	@bash scripts/release.sh
