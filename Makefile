.PHONY: test

test:
	uv run ruff check .
	uv run mypy .
	uv run pytest --cov=lib --cov-report=term-missing --cov-fail-under=80 test/unit
	uv run behave test/features
