import csv
import sqlite3
from pathlib import Path

from db.constants import (
    DB_PATH,
    DEFAULT_CONFIDENCE,
    DIALOGUE_FENCE,
    FORMS_PATH,
    INSERT_FORM_SQL,
    INSERT_NOTE_SQL,
    INSERT_PHRASE_SQL,
    NOTES_PATH,
    PHRASE_FIELD,
    PHRASE_HEADING,
    PHRASES_PATH,
    SCHEMA_PATH,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_phrases(path: Path) -> list[dict[str, str]]:
    phrases: list[dict[str, str]] = []
    dialogue: list[str] | None = None
    for line in path.read_text().splitlines():
        if line.startswith(DIALOGUE_FENCE):
            if dialogue is None:
                dialogue = []
            else:
                phrases[-1]["dialogue"] = "\n".join(dialogue)
                dialogue = None
        elif dialogue is not None:
            dialogue.append(line)
        elif line.startswith(PHRASE_HEADING):
            phrases.append({"phrase": line.removeprefix(PHRASE_HEADING).strip()})
        elif line.startswith(PHRASE_FIELD) and phrases:
            key, _, value = line.removeprefix(PHRASE_FIELD).partition(":")
            phrases[-1][key.strip()] = value.strip()
    return phrases


def form_params(record: dict[str, str]) -> dict[str, str | int | None]:
    return {
        "form": record["form"],
        "lemma": record["lemma"],
        "conf": int(record.get("conf") or DEFAULT_CONFIDENCE),
        "source": record["source"],
        "learned_on": record["learned_on"],
        "last_right": record.get("last_right") or None,
        "last_tested": record.get("last_tested") or None,
        "note": record.get("note") or None,
    }


def phrase_params(record: dict[str, str]) -> dict[str, str | int | None]:
    return {
        "phrase": record["phrase"],
        "meaning": record["meaning"],
        "dialogue": record.get("dialogue") or None,
        "conf": int(record.get("conf") or DEFAULT_CONFIDENCE),
        "source": record["source"],
        "learned_on": record["learned_on"],
        "note": record.get("note") or None,
    }


def build(db_path: Path = DB_PATH) -> None:
    db_path.unlink(missing_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text())
        conn.executemany(INSERT_FORM_SQL, map(form_params, read_tsv(FORMS_PATH)))
        conn.executemany(INSERT_NOTE_SQL, read_tsv(NOTES_PATH))
        conn.executemany(
            INSERT_PHRASE_SQL, map(phrase_params, read_phrases(PHRASES_PATH))
        )


def main() -> None:
    build()
    print(f"built {DB_PATH.name}")


if __name__ == "__main__":
    main()
