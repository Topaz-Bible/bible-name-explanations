# Changelog

## Unreleased

- Credits tidied: a "Built from" list (KJV, Keyway Vault, STEPBible Data's
  Strong's numbers, our own search and review); the studies are listed as
  checked against, and bible-data as an optional cross-reference.
- **Anchored to KJV words** (schema `bible-name-explanations-2`). Each entry's
  `kjv` block (book.chapter.verse:word) is the fixed anchor; the `vault` block
  is derived from it through the KJV's alignment on every build, so Vault IDs
  correct themselves as the alignment improves. Quotes are the anchored KJV
  words exactly: Simeon, Sitnah, Perez, Gad, Beulah and Melchizedek are no
  longer cut short. Massah and Meribah now quote their own halves of Exodus
  17:7; Salem quotes "King of peace". `data/anchors.json` now guards the KJV
  words instead of the Vault's. Nine entries wait on alignment for some Vault
  IDs (listed by the build).
- Seven one-off, implied explanations moved to excluded candidates
  (Allon-bachuth, Ramath-lehi, Mahaneh-dan, Sela-hammahlekoth, Cabul, Bamah,
  Elymas): 110 entries.
- `data/anchors.json` and a drift check on Vault words (since replaced by the KJV anchors).

- 117 explanations (85 naming, 8 renaming, 24 glosses). Seeded from the Keyway
  names catalog; the 30 open candidates settled (26 added, 4 excluded); 17 more
  found in proofreading (Zoar, Sitnah, Esau on Jacob, Jehovah-shalom, Berachah,
  Hephzibah, Beulah, Melchizedek, Golgotha in Mark and John, and others).
- Names and reasons may sit in different verses (13 entries), and reasons may
  run across verses.
- `bible_data` links to BradyStephenson/bible-data people and places (84).
- `note` on entries; judgement calls marked "Proofread:" and gathered in
  docs/review.md.
