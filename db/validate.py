import sqlite3
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from db.constants import (
    DB_PATH,
    FORMS_SQL,
    ORPHAN_NOTES_SQL,
    PHRASES_SQL,
    REPORT_CLEAN,
    REPORT_FOOTER,
    REPORT_HEADER,
    REPORT_LINE,
)
from dictionary.constants import DICT_DB_PATH
from dictionary.lookup import Dictionary
from tokens import WORD_PATTERN, dialogue_words, words


@dataclass(frozen=True)
class Finding:
    check: str
    detail: str


class Validator:
    """Soft checks SQLite cannot express. Every result is advisory."""

    def __init__(self, conn: sqlite3.Connection, dictionary: Dictionary | None) -> None:
        self._conn = conn
        self._dict = dictionary
        self._forms = conn.execute(FORMS_SQL).fetchall()
        self._phrases = conn.execute(PHRASES_SQL).fetchall()
        self._known = {form.lower() for form, _, _ in self._forms}

    def run(self) -> Iterator[Finding]:
        checks = (
            self._form_shape,
            self._dates,
            self._orphan_notes,
            self._phrase_words,
            self._dialogue_context,
            self._dialogue_words,
            self._lemma_in_dictionary,
            self._form_under_lemma,
        )
        for check in checks:
            yield from check()

    def _unknown(self, candidates: Iterator[str]) -> list[str]:
        return sorted({w for w in candidates if w.lower() not in self._known})

    def _form_shape(self) -> Iterator[Finding]:
        for form, lemma, _ in self._forms:
            match = WORD_PATTERN.fullmatch(form)
            if match is None:
                yield Finding("form-shape", f"{form!r} ({lemma}) is not a single word")
            elif form != form.lower():
                yield Finding("form-shape", f"{form!r} ({lemma}) is not lowercase")

    def _dates(self) -> Iterator[Finding]:
        today = date.today()
        rows = [(f, d) for f, _, d in self._forms] + [
            (p, d) for p, _, d in self._phrases
        ]
        for label, value in rows:
            try:
                parsed = date.fromisoformat(value)
            except ValueError:
                yield Finding("date", f"{label!r} has unparseable learned_on {value!r}")
                continue
            if parsed > today:
                yield Finding("date", f"{label!r} has a future learned_on {value}")

    def _orphan_notes(self) -> Iterator[Finding]:
        for (lemma,) in self._conn.execute(ORPHAN_NOTES_SQL):
            yield Finding(
                "orphan-note", f"note on {lemma!r} but no known_forms row uses it"
            )

    def _phrase_words(self) -> Iterator[Finding]:
        for phrase, _, _ in self._phrases:
            missing = self._unknown(words(phrase))
            if missing:
                yield Finding(
                    "phrase-words",
                    f"{phrase!r} uses words not in known_forms: {', '.join(missing)}",
                )

    def _dialogue_context(self) -> Iterator[Finding]:
        for phrase, dialogue, _ in self._phrases:
            if not dialogue:
                continue
            lines = dialogue.splitlines()
            spoken = [i for i, line in enumerate(lines) if phrase in line]
            if not spoken:
                yield Finding(
                    "dialogue-context", f"{phrase!r} is absent from its dialogue"
                )
            elif spoken[0] == 0:
                yield Finding("dialogue-context", f"{phrase!r} has no turn before it")
            elif spoken[-1] == len(lines) - 1:
                yield Finding("dialogue-context", f"{phrase!r} has no turn after it")

    def _dialogue_words(self) -> Iterator[Finding]:
        for phrase, dialogue, _ in self._phrases:
            if not dialogue:
                continue
            missing = self._unknown(dialogue_words(dialogue))
            if missing:
                yield Finding(
                    "dialogue-words",
                    f"dialogue for {phrase!r} uses unknown words: {', '.join(missing)}",
                )

    def _lemma_in_dictionary(self) -> Iterator[Finding]:
        if self._dict is None:
            return
        for lemma in sorted({lemma for _, lemma, _ in self._forms}):
            if not self._dict.has_entry(lemma):
                yield Finding("unknown-lemma", f"dict.db has no entry for {lemma!r}")

    def _form_under_lemma(self) -> Iterator[Finding]:
        if self._dict is None:
            return
        for form, lemma, _ in self._forms:
            candidates = {w.lower() for w in self._dict.lemmas_for(form)}
            if candidates and lemma.lower() not in candidates:
                yield Finding(
                    "wrong-lemma",
                    f"dict.db does not list {form!r} under {lemma!r} "
                    f"(it suggests: {', '.join(sorted(candidates)[:4])})",
                )


def report(findings: list[Finding]) -> None:
    if not findings:
        print(REPORT_CLEAN, file=sys.stderr)
        return
    plural = "" if len(findings) == 1 else "s"
    print(REPORT_HEADER.format(count=len(findings), s=plural), file=sys.stderr)
    for finding in findings:
        print(
            REPORT_LINE.format(check=finding.check, detail=finding.detail),
            file=sys.stderr,
        )
    print(REPORT_FOOTER, file=sys.stderr)


def main(db_path: Path = DB_PATH, dict_path: Path = DICT_DB_PATH) -> None:
    dictionary = Dictionary(dict_path) if dict_path.exists() else None
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        report(list(Validator(conn, dictionary).run()))


if __name__ == "__main__":
    main()
