import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from dictionary.constants import (
    ENTRY_EXISTS_SQL,
    LEMMAS_SQL,
    LOOKUP_SQL,
    MAX_CANDIDATES,
)


@dataclass(frozen=True)
class Definition:
    lemma: str
    pos: str
    ipa: str | None
    glosses: list[str]
    examples: list[dict[str, str]]
    tags: list[str]
    known: bool

    def as_payload(self) -> dict:
        return {
            "lemma": self.lemma,
            "pos": self.pos,
            "ipa": self.ipa,
            "glosses": self.glosses,
            "examples": self.examples,
            "tags": self.tags,
            "known": self.known,
        }


class Dictionary:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)

    def lookup(self, form: str, lemma: str | None = None) -> list[Definition]:
        """Every sense of a form, the already-learned lemma sorted first."""
        rows = self._conn.execute(
            LOOKUP_SQL, (form.lower(), lemma, MAX_CANDIDATES)
        ).fetchall()
        return [self._definition(row, lemma) for row in rows]

    @staticmethod
    def _definition(row: tuple, lemma: str | None) -> Definition:
        word, pos, ipa, glosses, examples, tags = row
        # kaikki suffixes some headwords, e.g. "i/languages M to Z"
        word = word.partition("/")[0]
        return Definition(
            lemma=word,
            pos=pos,
            ipa=ipa,
            glosses=json.loads(glosses),
            examples=json.loads(examples),
            tags=json.loads(tags),
            known=word == lemma,
        )

    def lemmas_for(self, form: str) -> set[str]:
        return {row[0] for row in self._conn.execute(LEMMAS_SQL, (form.lower(),))}

    def has_entry(self, word: str) -> bool:
        variants = (word, word.lower(), word.capitalize())
        return self._conn.execute(ENTRY_EXISTS_SQL, variants).fetchone() is not None
