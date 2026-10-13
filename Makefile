.PHONY: all validate clean lint
.DEFAULT_GOAL := all

all: polish.db validate

polish.db: db/schema.sql db/words.sql
	rm -f $@
	sqlite3 $@ < db/schema.sql
	sqlite3 $@ < db/words.sql

validate: polish.db
	@python3 -m db.validate

dict.db:
	python3 -m dictionary.build

lint:
	ruff check --fix . && ruff format .

clean:
	rm -f polish.db
