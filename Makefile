.PHONY: test

test:
	PYTHONPATH=. .venv/bin/behave test/features
