PYTHON ?= uv run python

.PHONY: test
test:
	uv run pytest

.PHONY: compile
compile:
	uv run python -m compileall yotta
