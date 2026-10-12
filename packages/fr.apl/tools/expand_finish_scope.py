#!/usr/bin/env python3
"""Expand FINISH scope input into manifest scope rows (fr.apl, housing + family-housing).

Reads corpus/laws/fr/apl/sources/finish-scope-input.json (hand-authored from
frozen 2026-10-06 slices) and emits the 744 manifest scope rows
(sources/finish-scope-rows.json) for root merge into source-manifest.json,
plus the manifest_additions (documents/edition_of/texts/declared) the merge
must carry. Does NOT mutate the manifest itself; does NOT fetch bytes.
(744 = 743 housing/family-housing + 1 DOM owner transfer L755-21-1.)

Edition mapping (CCH): each edition key maps to the version whose window
[debut, fin) covers the edition date (fin 2999-01-01 = infinity; inverted
windows and skip:true versions ignored). No covering version (article
created later) -> no row for that edition (matches the trimmed @source
lists in modules 13/15/21). Fragment name: CCH_<num with - as _> plus
_ED<suffix> for non-base editions. CSS: one base row per article.

Usage (root/reviewer, deferred -- never run by the no-checks author):
  python3 corpus/laws/fr/apl/tools/expand_finish_scope.py --check   # validate only
  python3 corpus/laws/fr/apl/tools/expand_finish_scope.py --write   # emit finish-scope-rows.json
Then merge rows + manifest_additions into sources/source-manifest.json,
copy XMLs per analysis/finish-source-copy-plan.json, and run the deferred
queue (fetch --check, sync fragments, law gen pinning, checks).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
INPUT = PACKAGE / "sources" / "finish-scope-input.json"
OUTPUT = PACKAGE / "sources" / "finish-scope-rows.json"


def frag_base(code: str, num: str) -> str:
    return f"{code}_{num.replace('-', '_')}"


def edition_suffix(key: str) -> str:
    if key == "cch":
        return ""
    assert key.startswith("cch_"), key
    return "_ED" + key[4:]


def covering(versions: list, date: str):
    cands = [v for v in versions
             if not v.get("skip") and v["deb"] <= date
             and (v["fin"] == "2999-01-01" or v["fin"] > date)]
    if len(cands) > 1:
        raise SystemExit(f"overlapping versions covering {date}: {cands}")
    return cands[0] if cands else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    rows: list = []
    skipped: list = []
    for art in data["articles_cch"]:
        base = frag_base("CCH", art["num"])
        for ed in data["cch_editions"]:
            v = covering(art["ver"], ed["date"])
            if v is None:
                skipped.append(f"{art['num']}@{ed['key']}")
                continue
            rows.append({
                "dump": v["dump"],
                "dir": "cch",
                "id": v["id"],
                "num": art["num"],
                "fragment": base + edition_suffix(ed["key"]),
                "edition": ed["key"],
            })
    for art in data["articles_css"]:
        p = art["pinned"]
        rows.append({
            "dump": p["dump"],
            "dir": "css",
            "id": p["id"],
            "num": art["num"],
            "fragment": frag_base("CSS", art["num"]),
            "edition": "css",
        })
    # Determinism + collision guards.
    frags = [r["fragment"] for r in rows]
    assert len(frags) == len(set(frags)), "duplicate fragments emitted"
    print(f"articles_cch={len(data['articles_cch'])} articles_css={len(data['articles_css'])} rows={len(rows)} skipped={len(skipped)}")
    for s in skipped:
        print(f"  skip {s}")
    if args.write:
        OUTPUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {OUTPUT}")
    elif not args.check:
        ap.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
