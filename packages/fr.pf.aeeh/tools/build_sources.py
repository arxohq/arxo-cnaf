#!/usr/bin/env python3
"""Pin the sources of package fr.pf.aeeh (CNAF wave 3, lane fr-cnaf-pf-handicap).

Reads the CSS registry (.scratch/reg-css.json, cut 2026-10-06) and builds:
  sources/css/<ARTICLE>.txt  - pinned text of the current version (registry alineas);
  sources/articles.json      - accounting: versions, NOTA, coverage, gaps,
                               per-edition fragments; edition documents are
                               map-relative ("editions/<name>.txt"), top-level
                               "document" is the current edition for the
                               program window (CF depth pattern, D-43);
  sources/fragment-map.json  - version base fragment -> all edition fragments
                               (for @source authoring);
  01-sources.law              - source CSS, editions back to back, publications
                                (one per edition, all member texts verbatim),
                                fragments (one per pinned version per edition
                                where that version is in force, APL pattern:
                                a rule fires only when an @source fragment of
                                its article belongs to the edition open at
                                legal_time).

Scope: 21 articles (L541-1/2/3/4/5, D541-1/2/3/4, R541-1..10,
L755-20, D755-11: DOM transfer, D-73).
The L/D articles are stable across the coverage window (L541-1/2/3 since
2005-02-12, D541-1/2/4 since 2006-01-01, D541-3 since 2009-06-01, L541-4
since 2012-01-01, L541-5 since 2021-01-01, L755-20 since 2015-10-16,
D755-11 since 2006-01-01: both DOM versions cover the whole window, no
predecessors). The R articles carry two
in-coverage reforms, both pinned as superseded versions (OLD):
  R541-1-PRE2022 (2005-12-20..2022-01-31: last alinea without the death
    extension added by decree 2022-85),
  R541-4-PRE2022 (2019-01-01..2022-01-31: no section V death extension),
  R541-4-PRE2026 (2022-01-31..2026-04-01: I/II structure before decree
    2026-227; durations identical to the current text).
The OpenFisca 2012-01 cases run on the same pinned rates (D. 541-1/2 in
force since 2006); amount rules open at 2006-01-01 for them. R541 rules
open at 2021-01-01 (coverage D-01).

NOTA is part of the fragment ONLY where it carries applicability (L541-5:
entry into force 2021-01-01 by loi 2020-1576 art. 32 V; R541-4: 2019
transitional note and 2026 demandes-from-2026-04-01 note). The R541-1
guide-barème location note is informational and stays out. Recorded per
fragment in articles.json.

Editions: the 5 pre-2022 starts are kept (no new pre-2021 splits: R541
pre-coverage debuts change no modelled norm for the 2012 cases); the
in-coverage debuts 2022-01-31 and 2026-04-01 become CSS_ED2022_01 and
CSS_ED2026_04.

The sixth-category complement equals the MTP amount (L. 341-4, external):
case input (B-PFAEEH-MTP). BMAF euro figures are unpinned arretes
(D-Q4 / DSS_PENDING): case inputs (B-PFAEEH-BMAF-EURO). The R541-2
evaluation guide, the category expense amounts and the declaration/urgency
arretes are unpinned: retained case inputs (B-PFAEEH-GUIDE-EVALUATION,
B-PFAEEH-SEUILS-ARRETE, B-PFAEEH-MODELE-ARRETE, B-PFAEEH-DELAI-URGENCE).

Usage:
  python3 corpus/laws/fr/pf-aeeh/tools/build_sources.py --check
  python3 corpus/laws/fr/pf-aeeh/tools/build_sources.py --write
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-aeeh"
REGISTRY = ROOT / ".scratch" / "reg-css.json"
MIRROR_CSS = ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006073189"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"

NS = "urn:fr:corpus:clir:pf-aeeh"

SCOPE = ["L541-1", "L541-2", "L541-3", "L541-4", "L541-5",
         "D541-1", "D541-2", "D541-3", "D541-4",
         "R541-1", "R541-2", "R541-3", "R541-4", "R541-5",
         "R541-6", "R541-7", "R541-8", "R541-9", "R541-10",
         "L755-20", "D755-11"]

# (num, legi_id, debut, fin, txt, frag): in-window superseded versions,
# read from the pinned mirror dump (same layout as the registry xml_rel).
OLD = [
    ("R541-1", "LEGIARTI000006750709", "2005-12-20", "2022-01-31",
     "sources/css/R541-1-2005.txt", "CSS_R541_1_PRE2022"),
    ("R541-4", "LEGIARTI000038014051", "2019-01-01", "2022-01-31",
     "sources/css/R541-4-2019.txt", "CSS_R541_4_PRE2022"),
    ("R541-4", "LEGIARTI000045087763", "2022-01-31", "2026-04-01",
     "sources/css/R541-4-2022.txt", "CSS_R541_4_PRE2026"),
]

# Articles whose NOTA carries applicability and joins the fragment text.
NOTA_IN_FRAGMENT = {"L541-5", "R541-4"}

# Pre-2022 edition starts, kept verbatim (existing fragments keep their
# names; R541 pre-coverage debuts open no new editions). In-coverage
# debuts (>= 2021-01-01) always open editions.
PRE2022_EDITIONS = frozenset(
    {"2005-02-12", "2006-01-01", "2009-06-01", "2012-01-01", "2021-01-01"})


def frag_name(num: str) -> str:
    return "CSS_" + num.replace("-", "_")


def ed_name(state: str) -> str:
    return "CSS_ED" + state[:4] + "_" + state[5:7]


def xml_alineas(xml_path: Path):
    raw = xml_path.read_text(encoding="utf-8")
    m = re.search(r"<BLOC_TEXTUEL>.*?</BLOC_TEXTUEL>", raw, re.S)
    assert m, f"no BLOC_TEXTUEL in {xml_path}"
    body = m.group(0)
    body = re.sub(r"</p\s*>", "\n\n", body)
    body = re.sub(r"(<br\s*/>\s*){2,}", "\n\n", body)
    body = re.sub(r"<br\s*/>", " ", body)
    body = re.sub(r"<[^>]+>", "", body)
    parts = [re.sub(r"\s+", " ", t).strip() for t in body.split("\n\n")]
    parts = [t for t in parts if t]
    assert parts, f"no alineas in {xml_path}"
    nota = ""
    n = re.search(r"<NOTA>.*?</NOTA>", raw, re.S)
    if n:
        nota = re.sub(r"\s+", " ",
                      re.sub(r"<[^>]+>", " ", n.group(0))).strip()
    return parts, nota


def mirror_xml(legi_id: str) -> Path:
    n = legi_id.replace("LEGIARTI", "")
    d = "/".join([n[0:2], n[2:4], n[4:6], n[6:8], n[8:10]])
    return MIRROR_CSS / "dump" / f"article/LEGI/ARTI/{d}/{legi_id}.xml"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    assert args.check or args.write, "give --check or --write"

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_num = {a["num"]: a for a in reg["articles"]}
    missing = [n for n in SCOPE if n not in by_num]
    assert not missing, f"scope absent from registry: {missing}"

    # Collect pinned versions: current per article (no superseded: stable).
    versions = []  # (num, legi_id, debut, fin, alineas, nota, txt_rel, frag)
    for num in SCOPE:
        a = by_num[num]
        nota_lines = a.get("nota", [])
        text = ("Article " + num + "\n" + "\n".join(a["alineas"]))
        if num in NOTA_IN_FRAGMENT and nota_lines:
            text += "\n" + "\n".join("NOTA: " + n for n in nota_lines)
        versions.append({
            "num": num, "legi_id": a["id"], "debut": a["debut"],
            "fin": a["fin"], "etat": a["etat"], "text": text,
            "txt": f"sources/css/{num}.txt", "frag": frag_name(num),
            "nota": nota_lines,
            "nota_in_fragment": num in NOTA_IN_FRAGMENT,
            "versions": [
                {"id": v["id"], "debut": v["debut"], "fin": v["fin"],
                 "etat": v["etat"]} for v in a.get("versions", [])],
            "xml_sha256": a.get("xml_sha256"),
            "xml_rel": a.get("xml_rel"),
        })

    for (num, legi_id, debut, fin, txt, frag) in OLD:
        p = mirror_xml(legi_id)
        assert p.exists(), f"old XML missing: {p}"
        alineas, nota = xml_alineas(p)
        text = "Article " + num + "\n" + "\n".join(alineas)
        nota_lines = [nota] if nota else []
        if num in NOTA_IN_FRAGMENT and nota_lines:
            text += "\n" + "\n".join("NOTA: " + n for n in nota_lines)
        versions.append({
            "num": num, "legi_id": legi_id, "debut": debut,
            "fin": fin, "etat": "MODIFIE", "text": text,
            "txt": txt, "frag": frag,
            "nota": nota_lines,
            "nota_in_fragment": num in NOTA_IN_FRAGMENT,
            "versions": [],
            "xml_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "xml_rel": str(p.relative_to(ROOT)),
        })

    debuts = sorted(PRE2022_EDITIONS
                    | {v["debut"] for v in versions
                       if v["debut"] >= "2021-01-01"})
    outputs = {}

    header = (
        "// Provenance S1: disabled-child education allowance (CSS, livre V,\n"
        "// titre IV, chapitre 1er: L. 541-1..5, D. 541-1..4, R. 541-1..10;\n"
        "// livre VII, titre V, chapitre 5: L. 755-20, D. 755-11, DOM transfer).\n"
        "// Block generated by tools/build_sources.py from the registry\n"
        "// .scratch/reg-css.json (cut 2026-10-06; alineas and versions from\n"
        "// the DILA LEGI mirror) plus 3 in-window superseded R versions\n"
        "// from the mirror dump (R541-1-PRE2022, R541-4-PRE2022/PRE2026).\n"
        "// Do not edit by hand.\n"
        "//\n"
        "// Coverage D-01 from 2021-01-01; amount rules open at 2006-01-01\n"
        "// (D. 541-1/2/4 debut) for the OpenFisca 2012-01 cases, which run on\n"
        "// the same pinned rates; R541 rules open at 2021-01-01. Editions:\n"
        "// the 5 pre-2022 starts plus CSS_ED2022_01 (2022-01-31) and\n"
        "// CSS_ED2026_04 (2026-04-01). NOTA joins the fragment only where it\n"
        "// carries applicability (L541-5, R541-4); see sources/articles.json.\n"
        "// BMAF euro figures are NOT pinned (owner input D-Q4 /\n"
        "// DSS_PENDING): they arrive as case inputs with provenance.\n"
        "\n"
        'language "law.core" version "0.2";\n'
        'package fr.pf.aeeh version "0.1.0";\n'
        f'namespace "{NS}";\n'
        "\n"
        "source CSS {\n"
        "    kind code;\n"
        "    jurisdiction FR;\n"
        '    label fr official "Code de la sécurité sociale";\n'
        '    label en unofficial "French Social Security Code";\n'
        "}\n"
    )
    editions = []
    for i, st in enumerate(debuts):
        nxt = debuts[i + 1] if i + 1 < len(debuts) else None
        window = f"[@{st}, @{nxt})" if nxt else f"[@{st}, infinity)"
        editions.append((ed_name(st), st, window))
    for name, st, window in editions:
        header += (
            f"\n"
            f"edition {name} of CSS {{\n"
            f"    language fr;\n"
            f"    officiality official;\n"
            f"    materialization_status PINNED_UNOFFICIAL_COPY;\n"
            f"    in_force {window};\n"
            f'    label fr official "Code de la sécurité sociale, état en vigueur à compter du {st}";\n'
            f'    label en unofficial "French Social Security Code: pinned scope as in force from {st}";\n'
            f"}}\n"
        )

    # Per-edition fragments (APL pattern): a rule participates in the
    # computation only when one of its @source fragments belongs to the
    # edition open at legal_time, so every pinned version gets a fragment in
    # each edition where that version is in force. Debut edition keeps the
    # bare base name; later editions append _ED<YYYY>_<MM>.
    INF = "2999-01-01"

    def in_force(v_debut, v_fin, e_start):
        fin = None if v_fin in (None, "", INF) else v_fin
        return v_debut <= e_start and (fin is None or e_start < fin)

    ed_starts = [st for _, st, _ in editions]
    frag_rows = []  # (edition, frag_name, version)
    for v in versions:
        first = True
        for est in ed_starts:
            if in_force(v["debut"], v["fin"], est):
                if first:
                    fname = v["frag"]
                    first = False
                else:
                    fname = f"{v['frag']}_ED{est[:4]}_{est[5:7]}"
                frag_rows.append((ed_name(est), fname, v))

    pubs = ""
    frags = "\n// BEGIN GENERATED FR-PF-AEEH FRAGMENTS\n"
    accounting = []
    frag_map = {}
    # Edition-concatenated publication bytes: the §194 gate pairs fragments
    # with publications by edition (substring), so each edition gets ONE
    # publication file holding every member fragment text verbatim.
    ed_members = {}
    for ed, fname, v in frag_rows:
        ed_members.setdefault(ed, []).append((fname, v))
        frag_map.setdefault(v["frag"], []).append((ed, fname))
    for ed in [e[0] for e in editions]:
        members = ed_members.get(ed, [])
        members.sort(key=lambda fv: (fv[1]["num"], fv[1]["debut"]))
        body = "".join(m["text"] + "\n" for _, m in members).encode("utf-8")
        rel = f"sources/editions/{ed}.txt"
        outputs[rel] = body
        digest = "sha256:" + hashlib.sha256(body).hexdigest()
        pubs += (
            f"\n"
            f"publication {ed}_TEXT of {ed} {{\n"
            f'    media_type "text/plain; charset=utf-8";\n'
            f'    uri "{DUMP_URL}";\n'
            f"    retrieved_at {RETRIEVED_AT};\n"
            f'    content_hash "{digest}";\n'
            f'    local_path "{rel}";\n'
            f"}}\n"
        )
    rows_by_version = {}
    for ed, fname, v in frag_rows:
        rows_by_version.setdefault(id(v), []).append((ed, fname))
    for v in versions:
        blob = (v["text"] + "\n").encode("utf-8")
        outputs[v["txt"]] = blob
        digest = "sha256:" + hashlib.sha256(blob).hexdigest()
        vrows = rows_by_version[id(v)]
        for ed, fname in vrows:
            frags += (
                f"\n"
                f'@id("{NS}#{fname}")\n'
                f"pub fragment {fname} in {ed} {{\n"
                f"    kind article;\n"
                f'    locator "article/{v["num"]}";\n'
                f'    text fr official """{v["text"]}\n'
                f'""";\n'
                f'    content_hash "{digest}";\n'
                f"}}\n"
            )
        accounting.append({
            "num": v["num"],
            "legi_id": v["legi_id"],
            "etat": v["etat"],
            "version_debut": v["debut"],
            "version_fin": v["fin"],
            "fragment": v["frag"],
            "edition_fragments": [
                {"edition": ed, "fragment": fn} for ed, fn in vrows],
            "working_copy": v["txt"],
            "content_hash": digest,
            "xml_sha256": v["xml_sha256"],
            "xml_rel": v["xml_rel"],
            "nota": v["nota"],
            "nota_in_fragment": v["nota_in_fragment"],
            "gap": None,
            "versions": v["versions"],
        })
    outputs["01-sources.law"] = (header + pubs + frags).encode("utf-8")
    # Depth-map metadata, CF pattern (D-43): the depth reader resolves the
    # edition document relative to sources/articles.json (its own
    # directory), so map entries (this file and per-edition "document")
    # need "editions/<name>.txt"; the previous "sources/editions/<name>.txt"
    # resolved to sources/sources/... and the act measured NO_SOURCE.
    # Top-level "document" pins the current edition for the program window
    # (coverage from 2021-01-01, cutoff 2026-10-06): the last back-to-back
    # edition, open at the cutoff. Top-level "scope" is the SCOPE number
    # list and each edition carries its exact ed_members numbers (never the
    # whole scope: early editions hold no later norms). Publication
    # local_path values in 01-sources.law stay package-relative
    # ("sources/editions/...") for the pinning gate; source bytes untouched.
    current_edition = editions[-1][0]
    outputs["sources/articles.json"] = (
        json.dumps({"cutoff": "2026-10-06", "coverage_start": "2021-01-01",
                    "scope": SCOPE, "unit": "fr_code_lettered_article",
                    "pinned_versions": len(versions),
                    "fragments": len(frag_rows),
                    "document": f"editions/{current_edition}.txt",
                    "editions": [{"edition": name,
                                   "unit": "fr_code_lettered_article",
                                   "scope": sorted({v["num"] for _, v in ed_members.get(name, [])}),
                                   "document": f"editions/{name}.txt"}
                                  for name, _st, _window in editions],
                    "articles": accounting},
                   ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    outputs["sources/fragment-map.json"] = (
        json.dumps({base: [fn for _, fn in rows]
                    for base, rows in frag_map.items()},
                   ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    if args.write:
        for rel, blob in outputs.items():
            p = PKG / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(blob)
        print(f"WROTE {len(outputs)} files, {len(versions)} pinned versions, "
              f"{len(frag_rows)} edition fragments")
        return 0
    errors = []
    for rel, blob in outputs.items():
        p = PKG / rel
        if not p.exists():
            errors.append(f"missing {rel}")
        elif p.read_bytes() != blob:
            errors.append(f"drift {rel}")
    print(f"articles: {len(SCOPE)}, pinned versions: {len(versions)}, "
          f"fragments: {len(frag_rows)}, editions: {len(debuts)}, "
          f"declared prev-text gaps: "
          f"{sum(1 for a in accounting if a['gap'])}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print("  " + e)
        return 1
    print("SOURCES OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
