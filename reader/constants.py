from enum import Enum
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "polish.db"

KNOWN_FORMS_SQL = "SELECT form, lemma, confidence FROM known_forms"


class Status(Enum):
    SOLID = "solid"
    LEARNING = "learning"
    WEAK = "weak"
    NEW = "new"


CONFIDENCE_STATUS = {3: Status.SOLID, 2: Status.LEARNING, 1: Status.WEAK}

STATUS_LABELS = {
    Status.SOLID: "solid",
    Status.LEARNING: "learning",
    Status.WEAK: "weak",
    Status.NEW: "unknown",
}

ANSI_RESET = "\033[0m"
ANSI_STYLES = {
    Status.SOLID: "",
    Status.LEARNING: "\033[33m",
    Status.WEAK: "\033[35m",
    Status.NEW: "\033[1;31m",
}

CONTAINER_PATH = "META-INF/container.xml"
CONTAINER_NS = "{urn:oasis:names:tc:opendocument:xmlns:container}"
OPF_NS = "{http://www.idpf.org/2007/opf}"
DC_NS = "{http://purl.org/dc/elements/1.1/}"
XHTML_MEDIA_TYPES = frozenset({"application/xhtml+xml", "text/html"})
SKIP_CONTENT_TAGS = frozenset({"script", "style", "head", "title"})
BLOCK_TAGS = frozenset(
    {
        "p",
        "div",
        "br",
        "li",
        "tr",
        "section",
        "blockquote",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }
)

HTML_RULE_COLORS = {
    Status.LEARNING: "#9a7a12",
    Status.WEAK: "#a2601f",
    Status.NEW: "#9c3327",
}
HTML_WASH_COLORS = {
    Status.LEARNING: "#f9f0cd",
    Status.WEAK: "#fae3cd",
    Status.NEW: "#f8dcd8",
}
HTML_DARK_WASH_COLORS = {
    Status.LEARNING: "#3a3414",
    Status.WEAK: "#3d2a16",
    Status.NEW: "#3d211d",
}

HTML_BASE_CSS = """
:root { --ink:#1c1d22; --paper:#fbfbfc; --faint:#6d7079; --line:#d9d9de; --sheet:#fff; }
@media (prefers-color-scheme:dark) {
  :root { --ink:#e6e5e2; --paper:#16171a; --faint:#8b8e96; --line:#32343a; --sheet:#1e2024; }
}
body { margin:0; background:var(--paper); color:var(--ink);
  font:1.25rem/1.85 Charter,"Bitstream Charter","Sitka Text",Cambria,Georgia,serif; }
main { max-width:38rem; padding:3rem 1.25rem 60vh; }
h1 { font:600 1.05rem/1.4 system-ui,sans-serif; color:var(--faint); margin:0 0 .4rem; }
.stats { font:0.82rem/1.7 system-ui,sans-serif; color:var(--faint); margin:0 0 2.5rem; }
.text { white-space:pre-wrap; }
w { cursor:pointer; }
.learning, .weak, .new { border-radius:1px; padding:0 .08em; }
w.active { outline:2px solid var(--ink); outline-offset:1px; }
#panel { position:fixed; left:0; right:0; bottom:0; background:var(--sheet);
  border-top:1px solid var(--line); padding:1rem 1.25rem 1.25rem;
  max-height:45vh; overflow-y:auto; display:none; }
#panel.open { display:block; }
#panel .inner { max-width:38rem; margin:0 auto; }
#panel .lemma { font-size:1.5rem; }
#panel .meta { font:0.8rem/1.6 system-ui,sans-serif; color:var(--faint); margin:.15rem 0 .7rem; }
#panel ol { font-size:1rem; margin:0; padding-left:1.4rem; }
#panel .ex { font-size:.95rem; margin:.8rem 0 0; padding-left:.8rem;
  border-left:1px solid var(--line); }
#panel .ex i { color:var(--faint); font-style:normal; font-size:.85rem; }
#panel .miss { font:0.95rem system-ui,sans-serif; color:var(--faint); }
#panel .sense + .sense { border-top:1px solid var(--line);
  margin-top:1rem; padding-top:1rem; }
#panel .mine { font:0.62rem system-ui,sans-serif; text-transform:uppercase;
  letter-spacing:.09em; border:1px solid var(--line); border-radius:2px;
  padding:.1rem .35rem; vertical-align:middle; color:var(--faint); }
#panel .say, #panel .arrow { font:0.65rem system-ui,sans-serif;
  text-transform:uppercase; letter-spacing:.09em; border:1px solid var(--line);
  border-radius:2px; background:none; color:var(--faint); padding:.18rem .45rem;
  cursor:pointer; vertical-align:middle; }
#panel .say:hover, #panel .arrow:hover { color:var(--ink); border-color:var(--ink); }
#panel .say:disabled, #panel .arrow:disabled { opacity:.45; cursor:default; }
#panel .arrow { font-size:.9rem; line-height:1; padding:.1rem .4rem; }
#panel .head { display:flex; align-items:center; gap:.5rem; flex-wrap:wrap;
  margin:0 0 .9rem; }
#panel .phrase { font-size:1.5rem; margin-right:.25rem; }
#panel .count { font:0.7rem system-ui,sans-serif; color:var(--faint); }
#panel .word { font:0.7rem system-ui,sans-serif; text-transform:uppercase;
  letter-spacing:.09em; color:var(--faint); margin:0 0 .5rem; }
#panel .cols { display:flex; gap:1.5rem; align-items:flex-start; }
#panel .col { flex:1 1 0; min-width:0; }
#panel .col + .col { border-left:1px solid var(--line); padding-left:1.5rem; }
#panel.multi .inner { max-width:64rem; }
@media (max-width:46rem) { #panel .cols { flex-direction:column; }
  #panel .col + .col { border-left:0; padding-left:0; border-top:1px solid var(--line);
    padding-top:1rem; } }
kbd { font:0.75rem system-ui,sans-serif; border:1px solid var(--line);
  border-bottom-width:2px; padding:.05rem .3rem; }
"""

HTML_SCRIPT = r"""
const NAV_SELECTOR = 'w.weak, w.new';
const SPEAK_LANG = 'pl';
const SPEAK_RATE = 0.65;
const MAX_COLUMNS = 3;
const MISSING = 'Not in the dictionary. Likely a proper name or an archaic form.';
const defs = JSON.parse(document.getElementById('defs').textContent);
if ('speechSynthesis' in window) speechSynthesis.getVoices();
const panel = document.getElementById('panel');
const inner = panel.querySelector('.inner');
const words = [...document.querySelectorAll('.text w')];
const unknown = [...document.querySelectorAll(NAV_SELECTOR)];
let anchor = null;
let span = [];
let column = 0;
let cursor = -1;

function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

function polishVoice() {
  return speechSynthesis.getVoices().find(v => v.lang.toLowerCase().startsWith(SPEAK_LANG));
}

function speak(text, button) {
  const voice = polishVoice();
  if (!voice) {
    button.textContent = 'no polish voice';
    button.disabled = true;
    return;
  }
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.voice = voice;
  utterance.lang = voice.lang;
  utterance.rate = SPEAK_RATE;
  utterance.onerror = e => { button.textContent = 'error: ' + e.error; };
  speechSynthesis.cancel();
  speechSynthesis.speak(utterance);
}

function sense(s) {
  const tags = s.tags.length ? s.tags.join(', ') : '';
  const bits = [s.pos, s.ipa, tags].filter(Boolean).join('  ·  ');
  const badge = s.known ? ' <span class=mine>learned</span>' : '';
  return '<div class=sense>' +
    '<p class=lemma>' + esc(s.lemma) + badge + '</p>' +
    '<p class=meta>' + esc(bits) + '</p>' +
    '<ol>' + s.glosses.map(g => '<li>' + esc(g) + '</li>').join('') + '</ol>' +
    s.examples.map(e => '<p class=ex>' + esc(e.pl) + '<br><i>' + esc(e.en) + '</i></p>').join('') +
    '</div>';
}

function definition(el) {
  const d = defs[el.dataset.w];
  return '<div class=col><p class=word>' + esc(el.textContent) + '</p>' +
    (d ? d.map(sense).join('') : '<p class=miss>' + MISSING + '</p>') + '</div>';
}

function spanText() {
  const range = document.createRange();
  range.setStartBefore(span[0]);
  range.setEndAfter(span[span.length - 1]);
  return range.toString().replace(/\s+/g, ' ').trim();
}

function page(step) {
  const last = Math.max(span.length - MAX_COLUMNS, 0);
  column = Math.min(Math.max(column + step, 0), last);
  render();
}

function render() {
  const visible = span.slice(column, column + MAX_COLUMNS);
  const text = spanText();
  const paged = span.length > MAX_COLUMNS;
  const nav = paged
    ? '<button class="arrow prev" type=button>&lsaquo;</button>' +
      '<button class="arrow next" type=button>&rsaquo;</button>' +
      '<span class=count>' + (column + 1) + '-' + (column + visible.length) +
      ' of ' + span.length + '</span>'
    : '';
  inner.innerHTML = '<p class=head><span class=phrase>' + esc(text) + '</span>' +
    '<button class=say type=button>' + (span.length > 1 ? 'say all' : 'say') +
    '</button>' + nav + '</p>' +
    '<div class=cols>' + visible.map(definition).join('') + '</div>';
  const button = inner.querySelector('.say');
  if (!('speechSynthesis' in window)) {
    button.textContent = 'no speech api';
    button.disabled = true;
  } else {
    button.addEventListener('click', () => speak(text, button));
  }
  if (paged) {
    inner.querySelector('.prev').disabled = column === 0;
    inner.querySelector('.next').disabled = column + MAX_COLUMNS >= span.length;
    inner.querySelector('.prev').addEventListener('click', () => page(-1));
    inner.querySelector('.next').addEventListener('click', () => page(1));
  }
  panel.classList.add('open');
  panel.classList.toggle('multi', span.length > 1);
}

function show(el, extend) {
  if (!extend || !anchor) anchor = el;
  const edges = [words.indexOf(anchor), words.indexOf(el)];
  span = words.slice(Math.min(...edges), Math.max(...edges) + 1);
  column = 0;
  cursor = unknown.indexOf(el);
  words.forEach(w => w.classList.remove('active'));
  span.forEach(w => w.classList.add('active'));
  render();
  el.scrollIntoView({block: 'center', behavior: 'smooth'});
}

document.querySelector('.text').addEventListener('click', e => {
  if (e.target.tagName !== 'W') return;
  if (e.shiftKey) getSelection().removeAllRanges();
  show(e.target, e.shiftKey);
});

document.addEventListener('keydown', e => {
  const open = panel.classList.contains('open');
  if (e.key === 'Escape') {
    panel.classList.remove('open');
    words.forEach(w => w.classList.remove('active'));
    span = [];
    anchor = null;
  } else if (e.key === 'n' && unknown.length) {
    show(unknown[(cursor + 1) % unknown.length], false);
  } else if (e.key === 'p' && unknown.length) {
    show(unknown[(cursor - 1 + unknown.length) % unknown.length], false);
  } else if (e.key === 's' && open) {
    inner.querySelector('.say').click();
  } else if (e.key === 'ArrowLeft' && open) {
    page(-1);
  } else if (e.key === 'ArrowRight' && open) {
    page(1);
  }
});
"""
