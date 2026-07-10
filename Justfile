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

# Install locally
install:
	uv sync --frozen

# Run larpfetch
run:
	uv run larpfetch

# Run larpfetch with args
run-args *args:
	uv run larpfetch {{ args }}

# Run all profiles
run-all:
	@for profile in nasa abomination hacker macbook server retro gamer minimal templeos haiku; do \
		echo "--- $profile ---"; \
		uv run larpfetch -p $profile --no-color; \
		echo; \
	done

# Typecheck (if using mypy/pyright)
typecheck:
	uv run pyright src/ || echo "pyright not installed, skipping"

# Show package version
version:
	@uv run python -c "from larpfetch import __version__; print(__version__)"

# Bump version in pyproject.toml
bump version:
	sed -i 's/^version = ".*"/version = "{{ version }}"/' pyproject.toml
	@echo "Version bumped to {{ version }}"

# Tag current commit
tag version:
	git tag -a v{{ version }} -m "v{{ version }}"
	@echo "Tagged v{{ version }}"

# Check for outdated deps
outdated:
	uv pip list --outdated

# Verify all profiles work
verify-profiles:
	@echo "Testing all profiles..."
	@for profile in nasa abomination hacker macbook server retro gamer minimal templeos haiku; do \
		uv run larpfetch -p $profile --no-color > /dev/null 2>&1 && echo "  ✓ $profile" || echo "  ✗ $profile"; \
	done
	@echo "Done."
