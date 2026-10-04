# Reddit Conlang Code Registry (RCCR)

RCCR is a small CSV registry and validator for BCP 47 private-use tags tied to
script or language entries in RNUR. The canonical data file is
`data/registry.csv`; the rules are described in `RCCR-TS-01.md` (version
1.1.0, status Draft).

## Data model and current entries

Each CSV row has these columns:

```text
Tag, Kind, Name, Author, Conscript_Tag, Real_Language,
RNUR_Start, RNUR_End, Status, Notes
```

Tags use `art-x-<slug>` for a constructed language and
`art-x-sx-<slug>` for a conscript. A conscript may point to the language tag
it writes through `Conscript_Tag`. `Real_Language` records an existing
language tag or the reserved values `NONE`/`MULTIPLE`. A language row is
admitted only when it has no existing BCP 47 primary subtag or ISO 639 code.

The checked-in registry currently has nine rows: seven conscripts and two
constructed languages. All nine are marked
`Provisional Lease / Pending Upstream Ratification`. The CSV is a registry
snapshot; this repository does not allocate code points or host a tag lookup
service.

RCCR records code-point ranges, not RNUR set numbers. Runtime resolution to an
RNUR set is outside this repository. It also does not provide fonts, shaping,
rendering, or text conversion.

## Validate

Requirements: Python 3.9 or newer (`str.removeprefix` is used); no
third-party Python package is required.

```powershell
py tools/rccr_check.py
```

The checker verifies tag grammar and uniqueness, kind and relationship rules,
language admission, code-point syntax/order, and containment in a Unicode
Private Use Area. If it finds a local RNUR checkout, it also checks each
registered range against `rnur/data/set1_master.csv` and compares status
strings. Without RNUR, it prints a note and skips that cross-check; it does
not fetch data from the network.

The checker exits with status 0 when the registry passes and 1 when it finds
invalid rows or a missing/empty registry. There is no separate automated test
suite in this repository.

## Files

- `data/registry.csv` — current tag-to-range records.
- `RCCR-TS-01.md` — draft architecture, schema, and admission rules.
- `tools/rccr_check.py` — syntax, consistency, PUA, and optional RNUR checks.
- `UNIDATA/Sources.txt` — provenance notes.
