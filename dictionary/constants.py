from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DICT_DB_PATH = PACKAGE_DIR.parent / "dict.db"
SCHEMA_PATH = PACKAGE_DIR / "schema.sql"
INDEXES_PATH = PACKAGE_DIR / "indexes.sql"

DUMP_URL = "https://kaikki.org/dictionary/Polish/kaikki.org-dictionary-Polish.jsonl"

FORM_NOISE_TAGS = frozenset({"table-tags", "inflection-template"})
MAX_GLOSSES = 4
MAX_EXAMPLES = 3
COMMIT_EVERY = 20_000

MAX_CANDIDATES = 4

LOOKUP_SQL = """
SELECT e.word, e.pos, e.ipa, e.glosses, e.examples, f.tags
FROM forms f
JOIN entries e ON e.id = f.entry_id
WHERE f.form = ?1
ORDER BY
  e.word = ?2 DESC,
  e.word = ?1 DESC,
  e.pos = 'character',
  f.tags LIKE '%error-unrecognized-form%',
  json_array_length(e.examples) DESC,
  json_array_length(e.glosses) DESC,
  f.tags = '[]',
  e.id
LIMIT ?3
"""

LEMMAS_SQL = """
SELECT DISTINCT e.word
FROM forms f
JOIN entries e ON e.id = f.entry_id
WHERE f.form = ?
"""

ENTRY_EXISTS_SQL = "SELECT 1 FROM entries WHERE word IN (?, ?, ?) LIMIT 1"
