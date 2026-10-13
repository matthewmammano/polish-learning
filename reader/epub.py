import re
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote
from xml.etree import ElementTree

from reader.constants import (
    BLOCK_TAGS,
    CONTAINER_NS,
    CONTAINER_PATH,
    DC_NS,
    OPF_NS,
    SKIP_CONTENT_TAGS,
    XHTML_MEDIA_TYPES,
)

BLANK_RUN = re.compile(r"\n{3,}")
TRAILING_SPACE = re.compile(r"[ \t]+\n")


@dataclass(frozen=True)
class EpubBook:
    title: str
    text: str


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in SKIP_CONTENT_TAGS:
            self._skip_depth += 1
        elif tag in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_CONTENT_TAGS and self._skip_depth:
            self._skip_depth -= 1
        elif tag in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self._parts.append(data)

    @property
    def text(self) -> str:
        return "".join(self._parts)


def _extract(markup: str) -> str:
    parser = _TextExtractor()
    parser.feed(markup)
    return parser.text


def _opf_path(archive: zipfile.ZipFile) -> str:
    container = ElementTree.fromstring(archive.read(CONTAINER_PATH))
    rootfile = container.find(f".//{CONTAINER_NS}rootfile")
    if rootfile is None or not rootfile.get("full-path"):
        raise ValueError("EPUB has no rootfile in container.xml")
    return rootfile.get("full-path")


def _title(opf: ElementTree.Element) -> str:
    node = opf.find(f".//{DC_NS}title")
    return node.text.strip() if node is not None and node.text else "untitled"


def _spine_hrefs(opf: ElementTree.Element) -> list[str]:
    manifest = {
        item.get("id"): item.get("href")
        for item in opf.iter(f"{OPF_NS}item")
        if item.get("media-type") in XHTML_MEDIA_TYPES
    }
    return [
        manifest[ref.get("idref")]
        for ref in opf.iter(f"{OPF_NS}itemref")
        if ref.get("idref") in manifest
    ]


def read_epub(path: Path) -> EpubBook:
    with zipfile.ZipFile(path) as archive:
        opf_path = _opf_path(archive)
        opf = ElementTree.fromstring(archive.read(opf_path))
        base = PurePosixPath(opf_path).parent
        chapters = []
        for href in _spine_hrefs(opf):
            name = str(base / unquote(href.split("#")[0]))
            chapters.append(archive.read(name).decode("utf-8", "replace"))
        title = _title(opf)
    body = "\n".join(_extract(chapter) for chapter in chapters)
    return EpubBook(
        title, BLANK_RUN.sub("\n\n", TRAILING_SPACE.sub("\n", body)).strip()
    )


def read_text_source(path: Path) -> EpubBook:
    if path.suffix.lower() == ".epub":
        return read_epub(path)
    return EpubBook(path.stem, path.read_text(encoding="utf-8"))
