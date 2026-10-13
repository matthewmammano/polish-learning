import argparse
import sys
from pathlib import Path

from dictionary.constants import DICT_DB_PATH
from dictionary.lookup import Dictionary
from reader.ansi import render_ansi
from reader.constants import DB_PATH
from reader.epub import read_text_source
from reader.html_page import render_html
from reader.vocab import Vocabulary, summary


def main() -> None:
    parser = argparse.ArgumentParser(prog="reader")
    parser.add_argument("source", type=Path, help=".txt or .epub")
    parser.add_argument("--html", type=Path, help="write a standalone HTML page")
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--dict", type=Path, default=DICT_DB_PATH)
    args = parser.parse_args()

    book = read_text_source(args.source)
    vocab = Vocabulary(args.db)

    if not args.html:
        print(render_ansi(book.text, vocab))
        print(f"\n{summary(book.text, vocab)}", file=sys.stderr)
        return

    dictionary = Dictionary(args.dict) if args.dict.exists() else None
    args.html.write_text(
        render_html(book.text, vocab, book.title, dictionary), encoding="utf-8"
    )
    note = "" if dictionary else "  (no dict.db, definitions off)"
    print(f"{args.html}  ·  {summary(book.text, vocab)}{note}")


main()
