#!/usr/bin/env python3
"""
rccr_check.py — validate the Reddit Conlang Code Registry.

Enforces RCCR-TS-01.md section 8. Run from anywhere:

    python tools/rccr_check.py

Exits 0 if the registry is valid, 1 otherwise.

Rule 9 (cross-checking against RNUR) is skipped with a notice when no local
RNUR checkout can be found, since RCCR is developed independently of it.
"""

import csv
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(REPO, "data", "registry.csv")

# RNUR lives beside this repo in the usual working layout; also try a couple
# of common alternatives.
RNUR_CANDIDATES = [
    os.path.join(os.path.dirname(REPO), "rnur"),
    os.path.join(REPO, "..", "rnur"),
    os.path.join(os.path.expanduser("~"), "Documents", "rnur"),
]

# RFC 5646 private-use subtree, with the RCCR 'sx' conscript marker.
# Subtag cap is 12, not RFC 5646's recommended 8: that recommendation binds
# registered subtags, and the x- subtree is unconstrained. See RCCR-TS-01.md
# section 6 -- 'loopiform' (9) and 'placeholder' (11) both exceed 8.
TAG_RE = re.compile(r"^art-x-(?:sx-)?[a-z0-9]{1,12}(?:-[a-z0-9]{1,12})*$")

# Unicode Private Use Areas, inclusive.
PUA_RANGES = [
    (0xE000, 0xF8FF),
    (0xF0000, 0xFFFFD),
    (0x100000, 0x10FFFD),
]

RESERVED = {"NONE", "MULTIPLE"}


def parse_cp(text, where, errors):
    m = re.fullmatch(r"U\+([0-9A-Fa-f]{4,6})", text.strip())
    if not m:
        errors.append(f"{where}: malformed codepoint {text!r} (expected U+XXXX)")
        return None
    return int(m.group(1), 16)


def in_pua(cp):
    return any(lo <= cp <= hi for lo, hi in PUA_RANGES)


def find_rnur():
    for path in RNUR_CANDIDATES:
        csv_path = os.path.join(path, "data", "set1_master.csv")
        if os.path.isfile(csv_path):
            return csv_path
    return None


def load_rnur(path, errors):
    """Index RNUR Set 1 by (start, end) -> status string."""
    index = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                lo = int(row["Start_Code_Point"].removeprefix("U+"), 16)
                hi = int(row["End_Code_Point"].removeprefix("U+"), 16)
            except (KeyError, ValueError, AttributeError):
                errors.append(f"rnur: unparsable row {row!r}")
                continue
            index[(lo, hi)] = (row.get("Status", "").strip(),
                               row.get("Script_Name", "").strip())
    return index


def main():
    errors = []
    warnings = []

    if not os.path.isfile(REGISTRY):
        print(f"FATAL: registry not found at {REGISTRY}", file=sys.stderr)
        return 1

    with open(REGISTRY, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    if not rows:
        print("FATAL: registry is empty", file=sys.stderr)
        return 1

    by_tag = {}
    for i, row in enumerate(rows, start=2):  # +1 header, +1 to 1-index
        tag = (row.get("Tag") or "").strip()
        kind = (row.get("Kind") or "").strip()
        where = f"row {i} ({tag or '<no tag>'})"

        # 1. syntax
        if not tag:
            errors.append(f"{where}: empty Tag")
        elif not TAG_RE.match(tag):
            errors.append(f"{where}: does not match the RFC 5646 art-x- grammar")

        # 2. uniqueness
        if tag in by_tag:
            errors.append(f"{where}: duplicate tag (first seen on row {by_tag[tag]})")
        else:
            by_tag[tag] = i

        # 3. kind
        if kind not in ("conscript", "language"):
            errors.append(f"{where}: Kind must be 'conscript' or 'language', got {kind!r}")

        # 5. Real_Language shape
        real = (row.get("Real_Language") or "").strip()
        if real and real not in RESERVED and not re.match(
            r"^[a-z]{2,12}(-[a-z0-9]{1,12})*$", real
        ):
            errors.append(f"{where}: Real_Language {real!r} is not a plausible BCP 47 tag")

        # 6. Admission Criterion (RCCR-TS-01.md section 5.2)
        if kind == "language" and real not in ("NONE", ""):
            errors.append(
                f"{where}: a language row must have Real_Language=NONE; "
                f"{real!r} already exists in BCP 47/ISO 639, so this must be a "
                f"conscript row instead (section 5.2)"
            )
        if kind == "conscript" and (row.get("Conscript_Tag") or "").strip() not in ("NONE", ""):
            errors.append(f"{where}: a conscript row must have Conscript_Tag=NONE")

        # 7/8. range inside PUA, start <= end
        lo = parse_cp(row.get("RNUR_Start", ""), where, errors)
        hi = parse_cp(row.get("RNUR_End", ""), where, errors)
        if lo is not None and hi is not None:
            if lo > hi:
                errors.append(f"{where}: RNUR_Start {lo:#x} > RNUR_End {hi:#x}")
            elif not (in_pua(lo) and in_pua(hi)):
                errors.append(f"{where}: range {lo:#x}-{hi:#x} is not wholly inside Unicode PUA")

    # 4. Conscript_Tag must resolve to a conscript row
    for i, row in enumerate(rows, start=2):
        ref = (row.get("Conscript_Tag") or "").strip()
        if ref in ("NONE", ""):
            continue
        if ref not in by_tag:
            errors.append(f"row {i} ({row['Tag']}): Conscript_Tag {ref!r} does not exist")
        else:
            target = rows[by_tag[ref] - 2]
            if (target.get("Kind") or "").strip() != "conscript":
                errors.append(
                    f"row {i} ({row['Tag']}): Conscript_Tag {ref!r} points at a "
                    f"{(target.get('Kind') or '').strip()!r} row, not a conscript"
                )

    # 9. cross-check against RNUR
    rnur_path = find_rnur()
    if rnur_path is None:
        warnings.append("no local RNUR checkout found; skipped the Set 1 cross-check")
    else:
        rnur = load_rnur(rnur_path, errors)
        checked = 0
        for i, row in enumerate(rows, start=2):
            lo = parse_cp(row.get("RNUR_Start", ""), f"row {i}", [])
            hi = parse_cp(row.get("RNUR_End", ""), f"row {i}", [])
            if lo is None or hi is None:
                continue
            hit = rnur.get((lo, hi))
            if hit is None:
                errors.append(
                    f"row {i} ({row['Tag']}): {lo:#x}-{hi:#x} does not match any "
                    f"range in RNUR set1_master.csv"
                )
                continue
            checked += 1
            rnur_status, script = hit
            if rnur_status and (row.get("Status") or "").strip() != rnur_status:
                warnings.append(
                    f"row {i} ({row['Tag']}): Status {row['Status']!r} != "
                    f"RNUR {rnur_status!r}"
                )
        if checked:
            print(f"cross-checked {checked} rows against {rnur_path}")

    for w in warnings:
        print(f"note: {w}")

    if errors:
        print(f"\nFAIL: {len(errors)} problem(s) in {os.path.relpath(REGISTRY, REPO)}")
        for e in errors:
            print(f"  - {e}")
        return 1

    conscripts = sum(1 for r in rows if r["Kind"] == "conscript")
    langs = len(rows) - conscripts
    print(f"OK: {len(rows)} tags valid ({conscripts} conscript, {langs} conlang)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
