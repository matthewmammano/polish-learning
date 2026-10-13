PRAGMA foreign_keys = ON;

CREATE TABLE known_forms (
  form        TEXT NOT NULL,
  lemma       TEXT NOT NULL,
  learned_on  TEXT NOT NULL,
  source      TEXT NOT NULL CHECK (source IN ('duolingo', 'maya', 'other')),
  confidence  INTEGER NOT NULL DEFAULT 2 CHECK (confidence BETWEEN 1 AND 3),
  note        TEXT,
  PRIMARY KEY (form, lemma)
) WITHOUT ROWID;

CREATE TABLE lemma_notes (
  lemma  TEXT PRIMARY KEY,
  note   TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE phrases (
  id           INTEGER PRIMARY KEY,
  phrase       TEXT NOT NULL UNIQUE,
  meaning      TEXT NOT NULL,
  dialogue     TEXT,
  learned_on   TEXT NOT NULL,
  source       TEXT NOT NULL CHECK (source IN ('duolingo', 'maya', 'other')),
  note         TEXT
);
