.PHONY: test

test:
	uv run ruff check .
	uv run mypy .
	uv run python -m unittest discover test/unit
	uv run behave test/features
