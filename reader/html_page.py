import html
import json

from dictionary.lookup import Dictionary
from reader.constants import (
    HTML_BASE_CSS,
    HTML_DARK_WASH_COLORS,
    HTML_RULE_COLORS,
    HTML_SCRIPT,
    HTML_WASH_COLORS,
    Status,
)
from reader.vocab import Vocabulary, summary
from tokens import tokenize


def _stylesheet() -> str:
    light = "".join(
        f".{status.value}{{background:{HTML_WASH_COLORS[status]};"
        f"border-bottom:2px solid {HTML_RULE_COLORS[status]}}}"
        for status in HTML_RULE_COLORS
    )
    dark = "".join(
        f".{status.value}{{background:{HTML_DARK_WASH_COLORS[status]}}}"
        for status in HTML_DARK_WASH_COLORS
    )
    return f"{HTML_BASE_CSS}{light}@media(prefers-color-scheme:dark){{{dark}}}"


def _markup(text: str, vocab: Vocabulary) -> tuple[str, set[str]]:
    body: list[str] = []
    seen: set[str] = set()
    for chunk, is_word in tokenize(text):
        if not is_word:
            body.append(html.escape(chunk))
            continue
        key = chunk.lower()
        seen.add(key)
        status = vocab.status(chunk)
        css = "" if status is Status.SOLID else f" class={status.value}"
        body.append(f'<w data-w="{key}"{css}>{html.escape(chunk)}</w>')
    return "".join(body), seen


def _definitions(
    words: set[str], vocab: Vocabulary, dictionary: Dictionary | None
) -> str:
    if dictionary is None:
        return "{}"
    found = {}
    for word in sorted(words):
        senses = dictionary.lookup(word, vocab.lemma(word))
        if senses:
            found[word] = [sense.as_payload() for sense in senses]
    return json.dumps(found, ensure_ascii=False).replace("</", r"<\/")


def render_html(
    text: str, vocab: Vocabulary, title: str, dictionary: Dictionary | None = None
) -> str:
    body, words = _markup(text, vocab)
    hint = (
        "click a word  ·  shift-click for a span  ·  <kbd>n</kbd> next unknown"
        "  ·  <kbd>p</kbd> previous  ·  <kbd>\u2190</kbd><kbd>\u2192</kbd> page"
        "  ·  <kbd>s</kbd> say it  ·  <kbd>esc</kbd> close"
    )
    return (
        "<!doctype html><html lang=pl><head><meta charset=utf-8>"
        '<meta name=viewport content="width=device-width,initial-scale=1">'
        f"<title>{html.escape(title)}</title><style>{_stylesheet()}</style></head><body>"
        f"<main><h1>{html.escape(title)}</h1>"
        f"<p class=stats>{summary(text, vocab)}<br>{hint}</p>"
        f"<div class=text>{body}</div></main>"
        f"<aside id=panel><div class=inner></div></aside>"
        f'<script type="application/json" id=defs>{_definitions(words, vocab, dictionary)}</script>'
        f"<script>{HTML_SCRIPT}</script></body></html>"
    )
