# How it works

## An entry

```json
{
  "id": "moses-exo-2-10",
  "name_en": "Moses",
  "strongs": "H4872",
  "kind": "naming",
  "kjv": {
    "name": ["EXO.002.010:014"],
    "because": ["EXO.002.010:019", "EXO.002.010:027"]
  },
  "vault": {
    "name": ["V.EXO.002.010:011a"],
    "because": ["V.EXO.002.010:015a", "V.EXO.002.010:016a"]
  },
  "found_by": ["formula", "kjv"],
  "bible_data": "person:Moses_1"
}
```

- **`kjv`**: the anchor, and the part people edit. `name` is the KJV word(s)
  of the name where it's given; `because` is the first and last word of the
  reason, inclusive. IDs are book + chapter + verse, `:` + the word's number
  in the verse of the Topaz KJV (the same addresses Topaz's commentary links
  use). The KJV is a settled text, so these never change.
- **`vault`**: worked out by `tools/build.py`; don't edit it. The Hebrew or
  Greek words the anchored KJV words are aligned to, as Keyway Token Vault
  addresses: `V.` + book + chapter + verse, `:` + slot (`011a`; a letter after
  the number marks a variant or a word added later). `because` runs from the
  first aligned slot to the last. Empty where the KJV words aren't aligned
  yet.
- **`strongs`**: the name's Strong's number, with STEP's disambiguating suffix (STEPBible Data, CC BY 4.0)
  where it has one (`G2424G`).
- **`kind`**: `naming`, `renaming` or `gloss`.
- **`found_by`**: how the entry was found. `formula`: the original-language
  search below; `bdb` / `strongs` / `kjv`: a lexicon or the English agreed;
  `review`: settled by hand where the search held the case back.
- **`bible_data`** (optional): a cross-reference to the person or place in
  [bible-data](https://github.com/BradyStephenson/bible-data) (CC BY 4.0), as
  `person:<person_id>` or `place:<place_id>`, or a list when the name belongs
  to two people (Boanerges). Its place list currently stops at Exodus 13, so
  most later places aren't linked yet.
- **`note`** (optional): anything a proofreader should know. Notes beginning
  "Proofread:" mark judgement calls.

## Why the KJV is the anchor

The Hebrew and Greek side keeps changing: manuscript transcriptions add
readings, readings add slots, and the KJV's word alignment to them is still
being finished. The KJV is a settled, already-processed text, with nothing
left to discover in it. So the KJV words are fixed by hand once, and the Vault
IDs follow from the alignment: as it improves, they correct themselves, with
no entry to re-check. Topaz's commentary links are anchored the same way.

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

`tools/build.py` refuses to write the list unless every KJV anchor exists, the
reason runs forward, the derived Vault IDs exist, and at least one name word
carries the entry's Strong's number (a name written as two words, like
Jehovah-jireh, may be tagged on either). It also compares every anchor with
the KJV word it held when the entry was made (`data/anchors.json`); the KJV
shouldn't change, so a mismatch stops the build. Entries whose words aren't
aligned yet are listed rather than refused.

What counts: names that recur, where the explanation helps a reader across
many verses, are the point. One-off names explained in the same verse with
the meaning only implied are left out (Allon-bachuth, Elymas and others; see
[coverage](coverage.md)).

```sh
python3 tools/build.py --vault ../keyway-data/vault --kjv ../topaz-bible/assets/packages/eng.bible.kjv.zip
python3 tools/coverage.py
```

## KJV quotes

The quotes are the anchored KJV words exactly, so they don't depend on the
alignment. Another keyed translation quotes the words aligned to the derived
Vault slots, taking in unaligned words at the edges when they run to
punctuation ("I have gotten a man") but not otherwise ("upon this rock", not
"rock I will").

## Sources

The list is our own work: seeded on 2026-10-23 from the original-language
formula search over the Keyway Token Vault (a snapshot is in
[`sources/`](../sources)), then completed and anchored to the KJV by hand. The
README's "Built from" section lists what it rests on.

Checked against, for missing passages only: J. Fichtner, VT 6 (1956); B. O.
Long, *The Problem of Etiological Narrative in the Old Testament* (1968); M.
Garsiel, *Biblical Names* (1991); H. Marks, JBL 114 (1995), which counts "over
eighty explicit etymologies" in the Hebrew Bible's narrative books. None of
their text or data is used.
