<p align="center">
  <b>RCCR</b> &mdash; Reddit Conlang Code Registry
</p>

# Reddit Conlang Code Registry (RCCR)

The official, open-source registry that assigns **BCP 47 tags** to conlangs
and conscripts encoded in the
[RNUR](https://github.com/nexustribarixa-redaamakrane/rnur)
(Reddit Neographical Unicode Registry).

RCCR answers one question: *given a piece of text, which writing system and
which language produced it?* RNUR answers a different one: *given a script,
which PUA code points does it occupy?*

---

## What gets a tag

RCCR mints two different things, under two different rules.

### Conscript tags &mdash; broad

> A conscript encoded in the RNUR gets a conscript tag, **unless another
> authority controls it**.

A writing system is a design artefact. Even one that exists only to write
English or Illongo is a distinct, nameable object, and tagging it shadows
nothing &mdash; no BCP 47 tag identifies a *script design*.

The one exclusion is **authority**. Where SPUCE holds the allocation, SPUCE
names it and RCCR stays out. That is why the SPUCE sectors mirrored into RNUR
Set&nbsp;1 &mdash; Enochian, Litterae Ignotae, Theban &mdash; carry no RCCR
tag of any kind.

### Conlang tags &mdash; narrow

> A language gets a conlang tag **only if it is a conlang** &mdash; only if it
> is artificial, with no existing BCP 47 primary subtag and no ISO 639 code.

This is the load-bearing rule. BCP 47 and ISO 639 already authoritatively tag
some 8,000 natural languages. Minting `art-x-` tags for them would create a
second, competing namespace and make `art-x-hiligaynon` strictly less useful
than plain `hil`.

So a real language never gets an `art-x-` tag, even when RNUR encodes a novel
orthography for it. The test is not *"is this language exotic?"* but **"does
a tag for this language already exist?"**

Every conscript row records the existing tag that forecloses a conlang tag, in
the `Real_Language` column, so each exclusion is auditable:

| Conscript | For | Conlang tag? |
| :--- | :--- | :--- |
| `art-x-sx-franklin` | English (`en`) | No &mdash; `en` exists |
| `art-x-sx-placeholder` | English (`en`) | No &mdash; `en` exists |
| `art-x-sx-sulat` | Hiligaynon (`hil`) | No &mdash; `hil` exists |
| `art-x-sx-western` | loanwords in Illongo (`hil`) | No &mdash; `hil` exists |
| `art-x-sx-loopiform` | Romance family | No &mdash; each has its own tag |
| `art-x-sx-zurjon` | the conlang **Zurjon** | **Yes** &mdash; `art-x-zurjon` |
| `art-x-sx-foldian` | the conlang **Foldian** | **Yes** &mdash; `art-x-foldian` |

## Tag scheme

```text
art-x-<slug>        a conlang        (only if nothing else names it)
art-x-sx-<slug>     a conscript      (any RNUR-encoded conscript)
```

All tags sit in the IANA private-use subtree of `art` (ISO 639-5 "artificial
languages"). RFC 5646 assigns no meaning to anything after `x-`, so this
subtree is ours to structure.

`sx` marks a conscript. BCP 47 has no conscript subtag, and claiming an
ISO 15924-style code for an invented script would assert registry status that
does not exist &mdash; so the marker lives inside the private subtree instead.
The two namespaces are disjoint by construction: a slug can never be both.

## No set layer

RNUR addresses glyphs by a coordinate **pair** `(Set_Number, Code_Point)`.
**RCCR has no sets, and will never acquire one.**

RNUR's set layers exist because the PUA is scarce and contested: two creators
who both want `U+E000` need somewhere to go. The `art-x-` subtree is not
scarce. `art-x-zurjon` and `art-x-anything-else` cannot collide, because the
tag namespace itself does the disambiguation. Adding sets to RCCR would
import a scarcity model to solve a problem that does not exist.

So the registry records a **code point range and no set**. That resolves the
one real ambiguity &mdash; `U+EF30` in Set 1 and `U+EF30` in Set 2 are
different allocations &mdash; at *runtime* instead:

```text
Set 1   U+EF30   <Zurjon>      ->      Set 2   U+EF30   <Zurjon>
             code point preserved, set changed
```

RNUR's eviction moves an allocation to the **identical code point** in a
higher set. So text tagged `art-x-zurjon` renders correctly both before and
after an eviction, because the tag resolves through whatever set is current.
The tag is the stable identity; the coordinate is a runtime lookup.

The same logic gives tags a life beyond the PUA. If a conlang graduates into a
real Unicode block, the `art-x-` tag is retained and re-pointed &mdash;
which is the strongest argument for BCP 47 over a bespoke syntax.

## Repository structure

```text
rccr/
├── README.md               # This file
├── RCCR-TS-01.md           # Normative architecture specification
├── data/
│   └── registry.csv        # The registry: one row per assigned tag
├── UNIDATA/
│   └── Sources.txt         # Provenance, in RNUR/Unicode data style
└── tools/
    └── rccr_check.py       # Validates registry syntax and cross-references
```

## Validation

```bash
python tools/rccr_check.py
```

Enforces the grammar, tag uniqueness, conscript back-references, the §5.2
admission criterion, and PUA containment. When a local RNUR checkout is
present it also verifies every code point range and status string against
`rnur/data/set1_master.csv`, so the two registries cannot drift apart
silently.

```text
cross-checked 9 rows against ...\rnur\data\set1_master.csv
OK: 9 tags valid (7 conscript, 2 conlang)
```

## Related

- **RNUR** &mdash; glyph allocation and the PUA coordinate matrix.
  <https://github.com/nexustribarixa-redaamakrane/rnur>
- **SUTR-7 (SUCEM)** &mdash; places ACR (this registry's abstract characters),
  SUCS, SUTF and SUST in the SuperUnicode Character Encoding Model.
