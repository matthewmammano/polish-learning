import json
import sqlite3
import sys
import urllib.request
from pathlib import Path

from dictionary.constants import (
    COMMIT_EVERY,
    DICT_DB_PATH,
    DUMP_URL,
    FORM_NOISE_TAGS,
    INDEXES_PATH,
    MAX_EXAMPLES,
    MAX_GLOSSES,
    SCHEMA_PATH,
)


def _glosses(senses: list[dict]) -> list[str]:
    out = [gloss for sense in senses for gloss in sense.get("glosses", [])]
    return out[:MAX_GLOSSES]


def _examples(senses: list[dict]) -> list[dict[str, str]]:
    out = []
    for sense in senses:
        for example in sense.get("examples", []):
            polish = example.get("text")
            english = example.get("english") or example.get("translation")
            if polish and english:
                out.append({"pl": polish, "en": english})
    return out[:MAX_EXAMPLES]


def _ipa(sounds: list[dict]) -> str | None:
    return next((sound["ipa"] for sound in sounds if sound.get("ipa")), None)


def _forms(raw: dict) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for entry in raw.get("forms", []):
        tags = entry.get("tags", [])
        form = entry.get("form", "")
        if form and form != "-" and not FORM_NOISE_TAGS.intersection(tags):
            found.setdefault(form.lower(), tags)
    found.setdefault(raw["word"].lower(), [])
    return found


class DictionaryBuilder:
    def __init__(self, db_path: Path) -> None:
        db_path.unlink(missing_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;")
        self._conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.count = 0

    def add(self, raw: dict) -> None:
        senses = raw.get("senses", [])
        glosses = _glosses(senses)
        if not glosses or not raw.get("word"):
            return
        cursor = self._conn.execute(
            "INSERT INTO entries (word, pos, ipa, glosses, examples) VALUES (?,?,?,?,?)",
            (
                raw["word"],
                raw.get("pos", ""),
                _ipa(raw.get("sounds", [])),
                json.dumps(glosses, ensure_ascii=False),
                json.dumps(_examples(senses), ensure_ascii=False),
            ),
        )
        self._conn.executemany(
            "INSERT OR IGNORE INTO forms (form, entry_id, tags) VALUES (?,?,?)",
            [
                (form, cursor.lastrowid, json.dumps(tags, ensure_ascii=False))
                for form, tags in _forms(raw).items()
            ],
        )
        self.count += 1
        if self.count % COMMIT_EVERY == 0:
            self._conn.commit()
            print(f"{self.count:,} entries", file=sys.stderr, flush=True)

    def finish(self) -> None:
        self._conn.commit()
        self._conn.executescript(INDEXES_PATH.read_text(encoding="utf-8"))
        self._conn.close()


def main() -> None:
    builder = DictionaryBuilder(DICT_DB_PATH)
    with urllib.request.urlopen(DUMP_URL) as stream:
        for line in stream:
            if line.strip():
                builder.add(json.loads(line))
    builder.finish()
    print(f"{DICT_DB_PATH}: {builder.count:,} entries")


main()
