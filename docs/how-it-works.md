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
  "found_by": ["formula", "kjv"],
  "bible_data": "person:Moses_1"
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
- **`bible_data`** (optional): the person or place in
  [bible-data](https://github.com/BradyStephenson/bible-data) (CC BY 4.0), as
  `person:<person_id>` or `place:<place_id>`, or a list when the name belongs
  to two people (Boanerges). Its place list currently stops at Exodus 13, so
  most later places aren't linked yet.
- **`note`** (optional): anything a proofreader should know. Notes beginning
  "Proofread:" mark judgement calls.

Token IDs are Keyway Token Vault addresses: `V.` + book + chapter + verse, `:`
+ slot. Slots number the original-language words of a verse (`001a`, `002a`;
a letter after the number marks a variant or a word added later).

## Across verses

The name and its reason may sit in different verses: Isaac is named in
Genesis 21:3, and Sarah's "God hath made me to laugh" is 21:6. A reason may
also run on across verses: `because` then starts in one verse and ends in a
later one, and the build reads every verse between.

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
aren't names ("Talitha cumi", "Corban"). Titles glossed in the text (Messias,
Rabbi, Rabboni, Abba) are included. Excluded candidates and why are listed in
[coverage](coverage.md).

## Checks

`tools/build.py` refuses to write the list unless every token ID exists in
the Vault, at least one name token carries the entry's Strong's number (a
name written as two words, like Jehovah-jireh, may be tagged on either), and
every reason runs forward. It also compares every token ID with the word it
pointed at when the entry was made (`data/anchors.json`) and stops, naming the
entries, if any has changed. Re-check those entries, then build with
`--accept`.

What counts: names that recur, where the explanation helps a reader across
many verses, are the point. One-off names explained in the same verse with
the meaning only implied are left out (Allon-bachuth, Elymas and others; see
[coverage](coverage.md)).

```sh
python3 tools/build.py --vault ../keyway-data/vault --kjv ../topaz-bible/assets/packages/eng.bible.kjv.zip
python3 tools/coverage.py
```

## KJV quotes

The quotes are generated from the KJV's word alignment, so they're only as
complete as it is. Untagged words at a quote's edge are taken in when they run
to punctuation ("I have gotten a man"), but not otherwise ("upon this rock",
not "rock I will"). Where alignment gaps trim a quote, the entry's note says
so (Simeon, Perez, Sitnah, Beulah, Gad).

## Sources

Seeded on 2026-10-23 from the Keyway names catalog
([`sources/`](../sources)), with 17 entries settled by hand. Studies
consulted for completeness: J. Fichtner, VT 6 (1956); B. O. Long, *The Problem
of Etiological Narrative in the Old Testament* (1968); M. Garsiel, *Biblical
Names* (1991); H. Marks, JBL 114 (1995), which counts "over eighty explicit
etymologies" in the Hebrew Bible's narrative books. Only verse references are
checked against them; none of their text is used.
