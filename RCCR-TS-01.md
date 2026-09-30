# RCCR-TS-01: Conlang Code Registry Architecture Specification

**Version:** 1.1.0

**Status:** Draft

**Author:** RCCR Core Architecture Group

---

## 1. Abstract & Rationale

A Private Use Area code point answers *where*, never *what*. Given the
sequence `U+EF30 U+EF31 U+EF32`, no consumer can determine which writing
system those glyphs belong to, which language they spell, or who drew them.
The information exists only in the head of whoever allocated them.

The Reddit Neographical Unicode Registry (RNUR) solves the *allocation*
problem: it assigns conflict-free PUA coordinates to original scripts,
conlangs and neographies.

RCCR solves the *identity* problem, and it solves it in two independent
halves. A **conscript** is a writing system &mdash; a design of shapes &mdash;
and every conscript encoded in the RNUR gets a tag. A **conlang** is a
constructed language &mdash; a design of words and grammar &mdash; and a
conlang gets a language tag *only if nothing else already names it*.

That asymmetry is the whole point of §5.

RCCR deliberately reuses BCP 47 rather than inventing a syntax. The web
already routes on `art-x-*` tags; a conlang registry with its own tag grammar
would be invisible to every existing consumer.

## 2. Scope

RCCR covers:

- the tag grammar for conscript and conlang identifiers;
- the registry mapping tags to RNUR code point ranges;
- the **admission criterion** that decides who receives which kind of tag;
- the provenance record for each entry.

RCCR does **not** cover:

- glyph allocation, PUA segmentation, set layering or eviction &mdash; that is
  [RNUR-TS-01](https://github.com/nexustribarixa-redaamakrane/rnur);
- fonts, shaping or rendering;
- the SuperUnicode codepoint space itself.

## 3. Relationship to RNUR

RCCR holds no allocation authority. Every registry row **MUST** cite a code
point range that exists in the cited RNUR release. RNUR knows nothing about
tags; a script may exist in RNUR with no RCCR tag, and that is explicitly
allowed. The registry is opt-in, not a mirror.

### 3.1 RCCR has no set layer

RNUR addresses glyphs by a **coordinate pair** `(Set_Number, Code_Point)`. Its
set layers exist because the PUA is a scarce, finite, contested resource:
two creators who both want `U+E000` need somewhere to go, so RNUR gives them
Set 2 and Set 3.

**RCCR has no sets, and will never acquire one.** The `art-x-` private
subtree of BCP 47 is not finite. Tag space is not a contended resource:
`art-x-zurjon` and `art-x-anything-else` can coexist without a single
collision, because the tag namespace itself performs the disambiguation that
RNUR's set layers perform for code points.

Adding a set layer to RCCR would be a category error &mdash; it would import
a scarcity model to solve a problem that does not exist, and every new set
would be a new thing to keep in sync for no benefit. Accordingly the registry
schema (§6) has **no set column at all**.

The consequence that does matter: a bare code point is ambiguous in RNUR,
because `U+EF30` in Set 1 and `U+EF30` in Set 2 are different allocations.
RCCR resolves this at **runtime** rather than by recording a set. See §4.

## 4. The Resolution Invariant

RNUR evicts an allocation to the *identical* code point in a higher set when
an upstream authority claims its sector:

```text
Set 1   U+EF30   <Zurjon>      ->      Set 2   U+EF30   <Zurjon>
```

The **code point** is preserved; the **set** changes. A text stream that
records only `U+EF30` is therefore unaffected by an eviction &mdash; what
changes is which set a layout engine must consult to learn that `U+EF30`
means a Zurjon glyph today.

**RCCR invariant:** a tag never encodes a set, and a registry row never
records one. Resolution of `art-x-zurjon` to a live coordinate is a runtime
operation against the current RNUR release. A document tagged `art-x-zurjon`
renders correctly before and after an eviction.

This is the reason the set column is absent rather than merely deprecated.

### 4.1 Graduation

RNUR's Graduation Rule &mdash; a script stays locked in Set 1 as a historical
record once a proposal is filed with the Unicode Consortium &mdash; has a
direct RCCR consequence. If an original conlang is eventually encoded in a
real Unicode block, the `art-x-` tag is **retained** and re-pointed at the
Unicode block. The tag outlives both the PUA allocation and possibly the
registry format.

This is the strongest argument for BCP 47 over a bespoke syntax: an `art-x-`
tag minted today remains meaningful if its glyphs graduate out of the PUA
entirely.

## 5. Admission Criterion

RCCR mints **two different things**, and admits them under **two different
rules**. Conflating them is the most common way a registry like this rots,
so the distinction is normative.

### 5.1 Conscript tags (`art-x-sx-*`) &mdash; broad

> A conscript encoded in the RNUR receives a conscript tag, **unless another
> authority controls it.**

A writing system is a design artefact. Even one that exists to write English
or Illongo is a distinct, nameable object, and giving it a tag costs nothing
and shadows nothing: no BCP 47 tag identifies a *script design*.

The only exclusion is **authority**. Where SPUCE (or another upstream body)
holds the allocation, that body is the naming authority and RCCR stays out of
its sectors entirely. This is why the SPUCE sectors mirrored into RNUR Set 1
&mdash; Enochian, Litterae Ignotae, Theban &mdash; carry **no** RCCR tag of
any kind, conscript included. They are recorded in RNUR; they are not ours to
name.

### 5.2 Conlang tags (`art-x-*`) &mdash; narrow

> A language receives a conlang tag **only if it is a conlang** &mdash; that
> is, only if it is an artificial or constructed language with no existing
> BCP 47 primary language subtag and no ISO 639 code.

This is the load-bearing constraint of the entire registry. BCP 47 and
ISO 639 already assign authoritative tags to roughly 8,000 natural languages.
A registry that minted `art-x-` tags for them would create a **second,
competing** namespace for languages that already have one, and text tagged
`art-x-hiligaynon` would be strictly less useful than text tagged `hil`.

So a real language is never given an `art-x-` tag, even when RNUR encodes a
genuinely novel orthography for it. Sulat is a real orthography of Hiligaynon;
it gets `art-x-sx-sulat` as a conscript, while the language keeps `hil`.
Franklin is a phonetic alphabet for English; it gets `art-x-sx-franklin`,
while the language keeps `en`. Loopiform targets the Romance family; it gets
`art-x-sx-loopiform`, while its languages keep their own tags.

The test is therefore not *"is this language exotic?"* but **"does a tag for
this language already exist?"**

### 5.3 Auditability

Because the criterion is a rule about *absence*, it is only trustworthy if the
registry records the evidence. Every conscript row therefore carries a
`Real_Language` column naming the existing BCP 47 tag that forecloses a conlang
tag &mdash; or `NONE` when the language is itself a conlang, or `MULTIPLE`
when a family of existing tags is implicated. A reviewer can verify each
exclusion by looking up one column.

## 6. Tag Grammar

All RCCR tags are BCP 47 language tags conforming to RFC 5646, rooted at the
`art` primary subtag and confined to the private-use subtree:

```abnf
rccr-tag      = "art-x-" rccr-body
rccr-body     = "sx-" rccr-slug / rccr-slug
rccr-slug     = 1*12(ALPHA / DIGIT) *("-" 1*12(ALPHA / DIGIT))
```

Per-subtag length is capped at 12. RFC 5646 recommends that subtag length
"should" not exceed 8, but that recommendation is addressed to *registered*
subtags; anything following `x-` is private use and is unconstrained, and
real conlang and script names exceed 8 characters routinely &mdash;
`loopiform` is 9 and `placeholder` is 11. The cap therefore exists only to
catch typos, and 12 is the shortest bound that admits every name currently in
the registry.

Slugs are lower case; tags are matched case-insensitively per BCP 47 and
normalised to lower case on registration.

### 6.1 The `sx` marker

BCP 47 has no subtag for a writing system as distinct from a language. RFC
5646 routes script identity through ISO 15924 script subtags, but those come
from a registry this project is not a member of; claiming ISO 15924-style
entries for invented scripts would assert script-code status that does not
exist.

RCCR therefore reserves the infix `sx` inside the private subtree:

| Form | Kind | Minted when |
| :--- | :--- | :--- |
| `art-x-sx-<slug>` | conscript | Always (§5.1), subject to the authority exclusion |
| `art-x-<slug>` | conlang | Only for conlangs (§5.2) |

The two namespaces are **disjoint by construction**; a slug can never be both.
A single allocation may back both &mdash; `art-x-zurjon` and
`art-x-sx-zurjon` cite the same range. That is normal, not an error.

## 7. Registry Format

`data/registry.csv` is UTF-8, comma-separated, with a header row. Fields
containing commas are double-quoted.

| Column | Type | Description |
| :--- | :--- | :--- |
| `Tag` | tag | The assigned BCP 47 tag. Unique across the file. |
| `Kind` | enum | `conscript` or `language`. |
| `Name` | text | Human-readable name of the script or language. |
| `Author` | text | Designer or steward; `NONE` where unattributed. |
| `Conscript_Tag` | tag \| `NONE` | Languages: the writing system used. Conscripts: `NONE`. |
| `Real_Language` | tag \| `NONE` \| `MULTIPLE` | The existing BCP 47 tag that forecloses a conlang tag. `NONE` when the row's language is itself a conlang. |
| `RNUR_Start` | codepoint | Inclusive start, `U+XXXX` form. |
| `RNUR_End` | codepoint | Inclusive end, `U+XXXX` form. |
| `Status` | text | Mirrors the RNUR status string for the allocation. |
| `Notes` | text | Free text; caveats and the §5 reasoning. |

`RNUR_Start` and `RNUR_End` describe an **allocation range**, not a character
inventory; the per-character repertoire lives in the RNUR release's
`UNIDATA/<set>/UnicodeData.txt`. RCCR does not duplicate it. There is no set
column, per §3.1.

## 8. Validation

`tools/rccr_check.py` enforces, and MUST pass before any registry revision is
published:

1. Every `Tag` parses under the §6 grammar and is lower case.
2. Every `Tag` is unique.
3. Every `Kind` is `conscript` or `language`.
4. Every `Conscript_Tag` that is not `NONE` resolves to a `conscript` row.
5. Every `Real_Language` that is not `NONE`/`MULTIPLE` parses as a plausible
   BCP 47 tag.
6. Rule 5 of §5.2 &mdash; a `language` row must have `Real_Language=NONE`
   (it is a conlang), and a `conscript` row must not be a conlang row.
7. Every range lies wholly within Unicode PUA space
   (`U+E000..U+F8FF`, `U+F0000..U+FFFFD`, `U+100000..U+10FFFD`).
8. `RNUR_Start <= RNUR_End`.
9. When a local RNUR checkout is available, every `(start, end)` pair matches
   a range in `rnur/data/set1_master.csv` and `Status` matches too.

Rule 9 is what keeps the two registries honest. Without it RCCR would drift
silently every time RNUR re-leased a block.

## 9. Versioning

RCCR versions as `MAJOR.MINOR.PATCH`.

- **MAJOR** &mdash; a backwards-incompatible change to the tag grammar (§6)
  or the registry schema (§7). Existing tags are never invalidated.
- **MINOR** &mdash; new entries, or new columns.
- **PATCH** &mdash; corrections to `Name`, `Author`, `Status` or `Notes` for
  existing tags.

Adding a tag is always a MINOR revision. Removing a tag is a MAJOR revision
and is expected to be contentious: a published tag is a promise to text
already in the wild.

### 9.1 Revision history

- **1.0.0** &mdash; initial draft: tag grammar, registry, SPUCE sectors
  mirrored, language tags minted for every registered entry.
- **1.1.0** &mdash; §5 Admission Criterion introduced. Language tags
  restricted to conlangs (§5.2); SPUCE sectors removed entirely (§5.1); the
  set layer and its column removed from the registry (§3.1, §4).

## 10. Open Issues

- **Orthography of a real language.** A community orthography for a real
  language is taggable as a conscript but leaves the language on its existing
  tag. Where a community orthography is *standard enough* to warrant its own
  language tag, the answer is presumably a registered extension subtags for
  `hil` and friends, not a private `art-x-` tag. Deferred to IETF.
- **Multi-script conlangs.** A conlang with several registered conscripts has
  no way to express "default". Candidates: a `Default` boolean column, or a
  reserved `art-x-sx-default` sentinel. Deferred.
- **Subtag depth.** `art-x-` is currently flat. Dialect and orthography
  distinctions may eventually need `art-x-<conlang>-<variant>`; the grammar
  already permits it, the registry does not yet use it.
