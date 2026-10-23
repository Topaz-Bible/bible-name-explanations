# How it works

## An entry

```json
{
  "id": "moses-exo-2-10",
  "name_en": "Moses",
  "strongs": "H4872",
  "kind": "naming",
  "name": ["V.EXO.002.010:011a"],
  "because": ["V.EXO.002.010:013a", "V.EXO.002.010:016a"],
  "found_by": ["formula", "kjv"]
}
```

- **`name`**: the token(s) of the name where it's given. A name written as two
  words (Ebenezer, Beer-sheba) lists both.
- **`because`**: the first and last token of the reason, inclusive.
- **`strongs`**: the name's Strong's number, with STEP's disambiguating suffix
  where it has one (`G2424G`).
- **`kind`**: `naming`, `renaming` or `gloss`.
- **`found_by`**: how the entry was found. `formula`: the original-language
  search below; `bdb` / `strongs` / `kjv`: a lexicon or the English agreed;
  `review`: settled by hand where the search held the case back.

Token IDs are Keyway Token Vault addresses: `V.` + book + chapter + verse, `:`
+ slot. Slots number the original-language words of a verse (`001a`, `002a`;
a letter after the number marks a variant or a word added later).

## Across verses

The name and its reason may sit in different verses: Isaac is named in
Genesis 21:3, and Sarah's "God hath made me to laugh" is 21:6. The reason
itself stays within one verse for now; reasons that run on across verses are
on the list to support.

## How entries are found

1. **Formulas in the original languages**, searched over the Vault:
   - Hebrew naming: "and she called his name … for …" (וַתִּקְרָא שְׁמוֹ … כִּי), "saying …",
     "therefore the name of it was called …" (עַל־כֵּן קָרָא).
   - Greek glosses: "which is, being interpreted" (ὅ ἐστιν μεθερμηνευόμενον),
     "which is by interpretation", "which is called".
2. **Lexicon pointers**: BDB's notes ("name explained as if from …") and
   Strong's ("with a play upon …").
3. **The English as a cross-check**: KJV phrases like "called his name" and
   "by interpretation".
4. **Review**: candidates the formulas hold back (where the reason starts and
   ends is unclear, the reason is in another verse) are settled by hand and
   marked `review`.

Not counted: "call upon the name of the LORD", naming without a reason
("called his name Obed"), Adam naming the animals, and glossed words that
aren't names ("Talitha cumi", "Corban"). Titles glossed in the text (Rabboni,
Abba) are candidates; see [coverage](coverage.md).

## Checks

`tools/build.py` refuses to write the list unless every token ID exists in
the Vault, every name token carries the entry's Strong's number, and every
reason runs forward within one verse.

```sh
python3 tools/build.py --vault ../keyway-data/vault --kjv ../topaz-bible/assets/packages/eng.bible.kjv.zip
python3 tools/coverage.py
```

## Sources

Seeded on 2026-10-23 from the Keyway names catalog
([`sources/`](../sources)), with 17 entries settled by hand. Studies
consulted for completeness: J. Fichtner, VT 6 (1956); B. O. Long, *The Problem
of Etiological Narrative in the Old Testament* (1968); M. Garsiel, *Biblical
Names* (1991); H. Marks, JBL 114 (1995), which counts "over eighty explicit
etymologies" in the Hebrew Bible's narrative books. Only verse references are
checked against them; none of their text is used.
