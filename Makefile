.PHONY: all validate clean lint
.DEFAULT_GOAL := all

all: polish.db validate

polish.db: db/schema.sql db/forms.tsv db/notes.tsv db/phrases.md
	@python3 -m db.build

validate: polish.db
	@python3 -m db.validate

dict.db:
	python3 -m dictionary.build

lint:
	ruff check --fix . && ruff format .

clean:
	rm -f polish.db
