.PHONY: test

test:
	uv run python -m unittest discover test/unit
	uv run behave test/features
