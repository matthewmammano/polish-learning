from reader.constants import ANSI_RESET, ANSI_STYLES
from reader.vocab import Vocabulary
from tokens import tokenize


def render_ansi(text: str, vocab: Vocabulary) -> str:
    out = []
    for chunk, is_word in tokenize(text):
        style = ANSI_STYLES[vocab.status(chunk)] if is_word else ""
        out.append(f"{style}{chunk}{ANSI_RESET}" if style else chunk)
    return "".join(out)
