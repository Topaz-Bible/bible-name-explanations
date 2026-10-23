# Bible Name Explanations

**Every place where the Bible itself explains a name, as open data.**

*"She called his name Moses: and she said, Because I drew him out of the water." (Exodus 2:10)*

Scripture often gives the reason for a name: a mother's words at a birth, a
place named for what happened there, a name changed (Abram to Abraham), or a
New Testament writer translating a name outright ("Cephas, which is by
interpretation, A stone"). This repository records each of those places.

It records **what the text says, not where a name really comes from.** Many of
these explanations are wordplay: Moses is more likely an Egyptian name, and
Babel's Akkadian meaning is "gate of god". Lexicons cover etymology; this list
covers the Bible's own explanations.

| | |
|---:|---|
| **110** | explanations: 79 namings, 8 renamings, 23 translated in the text ([the list](docs/list.md)) |
| **13** | where the name and its reason sit in different verses |
| **83** | cross-referenced to a person or place in [bible-data](https://github.com/BradyStephenson/bible-data) |

## What's here

| File | What it is |
|---|---|
| [`docs/list.md`](docs/list.md) | **For readers.** Every explanation, with the reason quoted from the KJV |
| [`docs/review.md`](docs/review.md) | **For proofreading.** Every entry as a short block, judgement calls first |
| [`data/explanations.json`](data/explanations.json) | The data: one entry per explanation, anchored to KJV words, with the Vault (original-language) IDs worked out from them |
| [`data/explanations.csv`](data/explanations.csv) | The same with references and text, one row each, for spreadsheets |
| [`data/candidates.json`](data/candidates.json) | Passages still to check, and [`docs/coverage.md`](docs/coverage.md), where each stands |
| [`docs/how-it-works.md`](docs/how-it-works.md) | The fields, how entries are found and checked, and what counts |
| [`tools/`](tools) | `build.py` checks every entry and writes the list and CSV; `coverage.py` updates the coverage page |

## Anchored to the KJV, read in any translation

Each entry is anchored to **KJV word positions**: `EXO.002.010:014` is Exodus
2:10, word 14 of the KJV. The KJV is a settled text, so the anchors never
change, and the quotes in the list are exactly those words.

From the anchors, the build works out the matching Hebrew or Greek words, as
**token IDs in the Keyway Token Vault** (`V.EXO.002.010:011a`), through the
KJV's word alignment. Any translation aligned to the Vault can then quote the
reason in its own wording.

## Kinds

- **naming**: a name given with its reason (Reuben, Moses, Ichabod, Jesus in Matthew 1:21)
- **renaming**: a name changed, with a reason (Abraham, Israel, Mara, Peter)
- **gloss**: the text translates or reads a name (Emmanuel, Cephas, Tabitha, Golgotha, Siloam; Nabal's "as his name is, so is he"). A few titles glossed in the text are included too: Messias, Rabbi, Rabboni, Abba.

## Keeping up with the Vault

The Token Vault grows: as manuscript readings are added, new slots appear and
words can move, and the KJV's alignment to it keeps improving. None of that
touches the KJV anchors. Each build works out the Vault IDs again from the
current alignment, so they correct themselves; the build lists the entries
whose IDs changed, and those whose words aren't aligned yet. Expect this
often.

[`data/anchors.json`](data/anchors.json) records the KJV word behind every
anchor, so if the KJV itself were ever re-issued, the build would stop.

## Corrections and additions

Know a passage we've missed, or a range that's wrong? [Open an issue](https://github.com/Topaz-Bible/bible-name-explanations/issues)
with the verse. Candidates waiting to be checked are in
[`data/candidates.json`](data/candidates.json).

## Built from

- **The King James Version** (Topaz's tokenized edition): the anchors and the quotes.
- **The Keyway Token Vault** and the KJV's word alignment to it: the Hebrew and Greek words.
- **Strong's numbers with STEP's disambiguating suffixes** (`H3130G`), from
  [STEPBible Data](https://github.com/STEPBible/STEPBible-Data), Tyndale House,
  Cambridge, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **Our own work**: the original-language search for naming formulas, the
  entries settled by hand, and the KJV anchors.

Checked against, for missing passages only (no text or data taken): Fichtner
(1956), Long (1968), Garsiel (1991), Marks (1995). The `bible_data` field is an
optional cross-reference to [bible-data](https://github.com/BradyStephenson/bible-data)
(CC BY 4.0) for anyone joining the two; nothing in this list comes from it.

## Licence

The data and lists are dedicated to the public domain under [CC0 1.0](LICENSE).
Use them for anything, no permission or attribution needed, though a link back
to [topaz.bible](https://topaz.bible) is appreciated. KJV quotations are in the
public domain outside the United Kingdom.

Built for the [Topaz Bible](https://topaz.bible), where tapping a name shows
what the text says about it.
