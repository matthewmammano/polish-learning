from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DB_PATH = PACKAGE_DIR.parent / "polish.db"
SCHEMA_PATH = PACKAGE_DIR / "schema.sql"
FORMS_PATH = PACKAGE_DIR / "forms.tsv"
NOTES_PATH = PACKAGE_DIR / "notes.tsv"
PHRASES_PATH = PACKAGE_DIR / "phrases.md"

FORMS_SQL = "SELECT form, lemma, learned_on FROM known_forms ORDER BY lemma, form"
PHRASES_SQL = "SELECT phrase, dialogue, learned_on FROM phrases ORDER BY id"
ORPHAN_NOTES_SQL = """
SELECT n.lemma
FROM lemma_notes n
WHERE NOT EXISTS (SELECT 1 FROM known_forms k WHERE k.lemma = n.lemma)
ORDER BY n.lemma
"""

REPORT_HEADER = "{count} warning{s} from db/validate.py"
REPORT_CLEAN = "db/validate.py: no warnings"
REPORT_LINE = "  [{check}] {detail}"
REPORT_FOOTER = (
    "\nThese are advisory. The build succeeded. Do not fix a warning by adding\n"
    "words to db/forms.tsv that Matt has not said he knows (CLAUDE.md rule 1)."
)

DEFAULT_CONFIDENCE = 2
PHRASE_HEADING = "## "
PHRASE_FIELD = "- "
DIALOGUE_FENCE = "```"

INSERT_FORM_SQL = """
INSERT INTO known_forms
  (form, lemma, confidence, source, learned_on, last_right, last_tested, note)
VALUES
  (:form, :lemma, :conf, :source, :learned_on, :last_right, :last_tested, :note)
"""
INSERT_NOTE_SQL = "INSERT INTO lemma_notes (lemma, note) VALUES (:lemma, :note)"
INSERT_PHRASE_SQL = """
INSERT INTO phrases (phrase, meaning, dialogue, confidence, source, learned_on, note)
VALUES (:phrase, :meaning, :dialogue, :conf, :source, :learned_on, :note)
"""
