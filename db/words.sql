-- The vocabulary. This file is the source of truth; polish.db is generated.
--
-- Rules when adding rows (see CLAUDE.md):
--   1. Never add a word Matt has not said he knows.
--   2. confidence: 1 = often miss it, 2 = get it but pause, 3 = instant.
--      New rows default to 2. Only Matt sets 1 or 3.
--   3. Phrases and dialogue use only forms already in known_forms.
--   4. Dialogue gives one turn before the phrase and one after. Speaker labels
--      are bare uppercase names plus a colon. Write real newlines inside the
--      quotes; SQLite stores them literally and does not interpret a \n escape.

INSERT INTO known_forms (form, lemma, learned_on, source) VALUES
  ('lubię',       'lubić',        '2026-10-09', 'duolingo'),
  ('lubisz',      'lubić',        '2026-10-09', 'duolingo'),
  ('lubi',        'lubić',        '2026-10-09', 'duolingo'),
  ('lubimy',      'lubić',        '2026-10-09', 'duolingo'),
  ('lubią',       'lubić',        '2026-10-09', 'duolingo'),
  ('mam',         'mieć',         '2026-10-09', 'duolingo'),
  ('masz',        'mieć',         '2026-10-09', 'duolingo'),
  ('ma',          'mieć',         '2026-10-09', 'duolingo'),
  ('mamy',        'mieć',         '2026-10-09', 'duolingo'),
  ('macie',       'mieć',         '2026-10-09', 'duolingo'),
  ('mają',        'mieć',         '2026-10-09', 'duolingo'),
  ('jestem',      'być',          '2026-10-09', 'duolingo'),
  ('jesteś',      'być',          '2026-10-09', 'duolingo'),
  ('jest',        'być',          '2026-10-09', 'duolingo'),
  ('jem',         'jeść',         '2026-10-09', 'duolingo'),
  ('je',          'jeść',         '2026-10-09', 'duolingo'),
  ('jedzą',       'jeść',         '2026-10-09', 'duolingo'),
  ('piję',        'pić',          '2026-10-09', 'duolingo'),
  ('pije',        'pić',          '2026-10-09', 'duolingo'),
  ('ja',          'ja',           '2026-10-09', 'duolingo'),
  ('ty',          'ty',           '2026-10-09', 'duolingo'),
  ('on',          'on',           '2026-10-09', 'duolingo'),
  ('ona',         'ona',          '2026-10-09', 'duolingo'),
  ('my',          'my',           '2026-10-09', 'duolingo'),
  ('wy',          'wy',           '2026-10-09', 'duolingo'),
  ('oni',         'oni',          '2026-10-09', 'duolingo'),
  ('one',         'one',          '2026-10-09', 'duolingo'),
  ('kobieta',     'kobieta',      '2026-10-09', 'duolingo'),
  ('kobiety',     'kobieta',      '2026-10-09', 'duolingo'),
  ('kobietą',     'kobieta',      '2026-10-09', 'duolingo'),
  ('mężczyzna',   'mężczyzna',    '2026-10-09', 'duolingo'),
  ('mężczyźni',   'mężczyzna',    '2026-10-09', 'duolingo'),
  ('mężczyzną',   'mężczyzna',    '2026-10-09', 'duolingo'),
  ('chłopiec',    'chłopiec',     '2026-10-09', 'duolingo'),
  ('chłopcy',     'chłopiec',     '2026-10-09', 'duolingo'),
  ('chłopcem',    'chłopiec',     '2026-10-09', 'duolingo'),
  ('dziewczynka', 'dziewczynka',  '2026-10-09', 'duolingo'),
  ('dziewczynki', 'dziewczynka',  '2026-10-09', 'duolingo'),
  ('dziewczynką', 'dziewczynka',  '2026-10-09', 'duolingo'),
  ('dziecko',     'dziecko',      '2026-10-09', 'duolingo'),
  ('dzieci',      'dziecko',      '2026-10-09', 'duolingo'),
  ('chleb',       'chleb',        '2026-10-09', 'duolingo'),
  ('mleko',       'mleko',        '2026-10-09', 'duolingo'),
  ('wodę',        'woda',         '2026-10-09', 'duolingo'),
  ('jabłko',      'jabłko',       '2026-10-09', 'duolingo'),
  ('ciasteczka',  'ciasteczko',   '2026-10-09', 'duolingo'),
  ('i',           'i',            '2026-10-09', 'duolingo');

INSERT INTO lemma_notes (lemma, note) VALUES
  ('być',      'Takes the instrumental, not the nominative: jestem kobietą.'),
  ('chłopiec', 'Drops the -ie- when it inflects: chłopiec, chłopcem, chłopcy.'),
  ('my',       'Looks like English "my". It means "we".'),
  ('oni',      'oni = a group with at least one man. one = everything else.'),
  ('woda',     'Direct object takes the accusative: wodę, not woda.');

INSERT INTO phrases (phrase, meaning, dialogue, learned_on, source, note) VALUES
  ('Jestem kobietą.', 'I am a woman.',
   'TY: Jesteś mężczyzną?
JA: Jestem kobietą.
TY: Masz chleb?',
   '2026-10-09', 'duolingo', 'być plus the instrumental.'),

  ('Piję wodę.', 'I drink water.',
   'TY: Masz mleko?
JA: Piję wodę.
TY: Ja jem jabłko.',
   '2026-10-09', 'duolingo', 'Direct object takes the accusative.'),

  ('On je jabłko.', 'He eats an apple.',
   'TY: On ma jabłko?
JA: On je jabłko.
TY: Ona je ciasteczka.',
   '2026-10-09', 'duolingo', 'Neuter accusative looks like the nominative.');
