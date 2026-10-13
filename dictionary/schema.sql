CREATE TABLE entries (
  id       INTEGER PRIMARY KEY,
  word     TEXT NOT NULL,
  pos      TEXT NOT NULL,
  ipa      TEXT,
  glosses  TEXT NOT NULL,
  examples TEXT NOT NULL
);

CREATE TABLE forms (
  form     TEXT NOT NULL,
  entry_id INTEGER NOT NULL REFERENCES entries(id),
  tags     TEXT NOT NULL,
  PRIMARY KEY (form, entry_id)
) WITHOUT ROWID;
