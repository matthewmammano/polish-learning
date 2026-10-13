import re
from collections.abc import Iterator

WORD_PATTERN = re.compile(r"[^\W\d_]+")
SPEAKER_PATTERN = re.compile(r"^[A-ZĄĆĘŁŃÓŚŹŻ]+\s*:", re.MULTILINE)


def tokenize(text: str) -> Iterator[tuple[str, bool]]:
    position = 0
    for match in WORD_PATTERN.finditer(text):
        if match.start() > position:
            yield text[position : match.start()], False
        yield match.group(), True
        position = match.end()
    if position < len(text):
        yield text[position:], False


def words(text: str) -> Iterator[str]:
    for match in WORD_PATTERN.finditer(text):
        yield match.group()


def dialogue_words(text: str) -> Iterator[str]:
    """Words of a dialogue, ignoring JA:/MAYA: speaker labels."""
    return words(SPEAKER_PATTERN.sub("", text))
