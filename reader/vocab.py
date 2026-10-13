import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from reader.constants import (
    CONFIDENCE_STATUS,
    KNOWN_FORMS_SQL,
    STATUS_LABELS,
    Status,
)
from tokens import tokenize


@dataclass(frozen=True)
class KnownForm:
    form: str
    lemma: str
    confidence: int


class Vocabulary:
    """Read-only view of known_forms, keyed by lowercased surface form."""

    def __init__(self, db_path: Path) -> None:
        self._entries: dict[str, list[KnownForm]] = {}
        with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
            for form, lemma, confidence in conn.execute(KNOWN_FORMS_SQL):
                entry = KnownForm(form.lower(), lemma, confidence)
                self._entries.setdefault(entry.form, []).append(entry)

    def status(self, word: str) -> Status:
        entries = self._entries.get(word.lower())
        if not entries:
            return Status.NEW
        return CONFIDENCE_STATUS[max(e.confidence for e in entries)]

    def lemma(self, word: str) -> str | None:
        """The lemma to show for a form, or None when it is ambiguous or unknown."""
        entries = self._entries.get(word.lower(), [])
        return entries[0].lemma if len(entries) == 1 else None


def coverage(text: str, vocab: Vocabulary) -> Counter[Status]:
    return Counter(vocab.status(word) for word, is_word in tokenize(text) if is_word)


def summary(text: str, vocab: Vocabulary) -> str:
    counts = coverage(text, vocab)
    total = sum(counts.values())
    known = total - counts[Status.NEW]
    parts = [f"{total:,} words"]
    parts += [
        f"{counts[status]:,} {STATUS_LABELS[status]}"
        for status in Status
        if counts[status]
    ]
    parts.append(f"{100 * known // max(total, 1)}% known")
    return "  ·  ".join(parts)
