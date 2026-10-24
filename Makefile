.PHONY: all validate clean lint
.DEFAULT_GOAL := all

all: polish.db validate

polish.db: db/schema.sql db/forms.tsv db/notes.tsv db/phrases.md
	@uv run python -m db.build

validate: polish.db
	@uv run python -m db.validate

dict.db:
	uv run python -m dictionary.build

lint:
	uv run ruff check --fix . && uv run ruff format .

clean:
	rm -f polish.db
