#!/usr/bin/env python3
"""Pin the sources of package fr.minima.ressources (CNAF wave 4, W4-RSA).

Reads the CASF registry (.scratch/reg-LEGITEXT000006074069.json, cut
2026-10-06) and builds:
  sources/casf/<ARTICLE>[-<TAG>].txt - pinned text of each version in force
                               at some point in [2021-01-01, +inf);
  sources/articles.json      - accounting: versions, NOTA, coverage, gaps,
                               per-edition fragments; edition documents are
                               map-relative ("editions/<name>.txt"), top-level
                               "document" is the current edition for the
                               program window (W4 depth layout, CF pilot D-43);
  sources/fragment-map.json  - version base fragment -> all edition fragments
                               (for @source authoring);
  01-sources.law              - source CASF, editions back to back from
                                2021-01-01 (D-01), publications (one per
                                edition, all member texts verbatim),
                                fragments (one per pinned version per edition
                                where that version is in force, APL pattern:
                                a rule fires only when an @source fragment of
                                its article belongs to the edition open at
                                legal_time).

Scope: exactly 20 CASF articles (R. 262-4, R. 262-4-1, R. 262-4-2,
R. 262-6, R. 262-7, R. 262-9, R. 262-10, R. 262-10-1, R. 262-11,
R. 262-12, R. 262-13, R. 262-14, R. 262-18 .. R. 262-25).

NOTA joins the fragment only where it carries applicability (R. 262-7:
decree 2025-185 applies from 01.03.2025; R. 262-9: decree 2023-1378
applies to resources from 01.01.2024); see sources/articles.json.
DSN amounts, declared resources and the euro flat-rate base (L. 262-2
amount, decree, unpinned) arrive as case inputs with provenance
(B-RSA-MF-EURO, DSS_PENDING for the 1 April factor).

Usage:
  python3 corpus/laws/fr/minima-ressources/tools/build_sources.py --check
  python3 corpus/laws/fr/minima-ressources/tools/build_sources.py --write
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "minima-ressources"
REGISTRY = ROOT / ".scratch" / "reg-LEGITEXT000006074069.json"
MIRROR = ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006074069"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"
COVERAGE_START = "2021-01-01"

NS = "urn:fr:corpus:clir:minima-ressources"

SCOPE = ["R262-4", "R262-4-1", "R262-4-2", "R262-6", "R262-7", "R262-9",
         "R262-10", "R262-10-1", "R262-11", "R262-12", "R262-13",
         "R262-14", "R262-18", "R262-19", "R262-20", "R262-21", "R262-22",
         "R262-23", "R262-24", "R262-25"]

# Superseded versions pinned from the mirror dump: version in force at
# some point in [2021-01-01, +inf) but no longer current. TAG joins the
# working-copy filename and the base fragment name.
# (num, legi_id, debut, fin, tag)
OLD = [
    ("R262-4", "LEGIARTI000033979143", "2017-01-01", "2025-02-28", "PRE2025"),
    ("R262-7", "LEGIARTI000033979130", "2017-01-01", "2025-02-28", "PRE2025"),
    ("R262-9", "LEGIARTI000031694445", "2016-01-01", "2023-12-31", "PRE2024"),
    ("R262-11", "LEGIARTI000042497096", "2020-11-06", "2021-03-25", "PRE202103"),
    ("R262-11", "LEGIARTI000043281883", "2021-03-25", "2022-03-21", "PRE202203"),
    ("R262-11", "LEGIARTI000045386056", "2022-03-21", "2023-12-31", "PRE2024"),
    ("R262-11", "LEGIARTI000048841536", "2023-12-31", "2025-02-28", "PRE2025"),
    ("R262-12", "LEGIARTI000033979125", "2017-01-01", "2023-12-31", "PRE2024"),
    ("R262-12", "LEGIARTI000048841529", "2023-12-31", "2026-06-27", "PRE2026"),
    ("R262-13", "LEGIARTI000038893113", "2019-11-01", "2025-02-28", "PRE2025"),
    ("R262-13", "LEGIARTI000051258433", "2025-02-28", "2025-06-01", "PRE202506"),
    ("R262-18", "LEGIARTI000034624191", "2017-07-01", "2025-02-28", "PRE2025"),
    ("R262-19", "LEGIARTI000038787285", "2019-07-08", "2025-02-28", "PRE2025"),
]

# Articles whose NOTA carries applicability and joins the fragment text.
NOTA_IN_FRAGMENT = {"R262-7", "R262-9"}


def frag_name(num: str) -> str:
    return "CASF_" + num.replace("-", "_")


def ed_name(state: str) -> str:
    return "CASF_ED" + state[:4] + "_" + state[5:7]


def xml_rel_for(legi_id: str) -> str:
    digits = legi_id.replace("LEGIARTI", "")
    pairs = [digits[i:i + 2] for i in range(0, 12, 2)][:5]
    return "dump/article/LEGI/ARTI/" + "/".join(pairs) + f"/{legi_id}.xml"


def find_xml(legi_id: str) -> Path:
    rel = xml_rel_for(legi_id)
    p = MIRROR / rel
    if p.exists():
        return p
    hits = sorted((MIRROR / "increments").rglob(legi_id + ".xml"))
    assert hits, f"version XML absent from mirror: {legi_id}"
    return hits[-1]


def old_xml_alineas(legi_id: str):
    """Extract alineas from a mirror version XML (<br/> separated)."""
    p = find_xml(legi_id)
    raw = p.read_text(encoding="utf-8")
    m = re.search(r"<BLOC_TEXTUEL>.*?</BLOC_TEXTUEL>", raw, re.S)
    assert m, f"no BLOC_TEXTUEL in {legi_id}"
    body = m.group(0)
    body = re.sub(r"</p\s*>", "\n\n", body)
    body = re.sub(r"(<br\s*/>\s*){2,}", "\n\n", body)
    body = re.sub(r"<br\s*/>", " ", body)
    body = re.sub(r"<[^>]+>", "", body)
    parts = [re.sub(r"\s+", " ", t).strip()
             for t in body.split("\n\n")]
    parts = [t for t in parts if t]
    assert parts, f"no alineas in {legi_id}"
    nota = ""
    n = re.search(r"<NOTA>.*?</NOTA>", raw, re.S)
    if n:
        nota = re.sub(r"\s+", " ",
                      re.sub(r"<[^>]+>", " ", n.group(0))).strip()
    return parts, nota


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

    # Collect pinned versions: current per article + superseded from XML.
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
            "txt": f"sources/casf/{num}.txt", "frag": frag_name(num),
            "nota": nota_lines,
            "nota_in_fragment": num in NOTA_IN_FRAGMENT,
            "xml_sha256": a.get("xml_sha256"),
            "xml_rel": a.get("xml_rel"),
        })
    for num, legi_id, debut, fin, tag in OLD:
        alineas, nota = old_xml_alineas(legi_id)
        text = "Article " + num + "\n" + "\n".join(alineas)
        nota_lines = [nota] if nota else []
        if nota_lines:
            text += "\n" + "\n".join("NOTA: " + n for n in nota_lines)
        p = find_xml(legi_id)
        versions.append({
            "num": num, "legi_id": legi_id, "debut": debut,
            "fin": fin, "etat": "MODIFIE", "text": text,
            "txt": f"sources/casf/{num}-{tag}.txt",
            "frag": frag_name(num) + "_" + tag,
            "nota": nota_lines,
            "nota_in_fragment": bool(nota_lines),
            "xml_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "xml_rel": str(p.relative_to(MIRROR)),
        })

    starts = sorted({v["debut"] for v in versions if v["debut"] >= COVERAGE_START}
                    | {COVERAGE_START})
    outputs = {}

    header = (
        "// Provenance S1: quarterly resources of the RSA (CASF, livre II,\n"
        "// titre VI, chapitre II, section 2). Block generated by\n"
        "// tools/build_sources.py from the registry .scratch/reg-LEGITEXT000006074069.json\n"
        "// (cut 2026-10-06; alineas from the DILA LEGI mirror) plus\n"
        "// superseded version XMLs from the mirror dump (pre-2025 quarter\n"
        "// R262-4/R262-7, pre-2024 forfait R262-9, R262-11/12/13/18/19 chains).\n"
        "// Do not edit by hand.\n"
        "//\n"
        "// Coverage D-01 from 2021-01-01. Editions run back to back from\n"
        "// the coverage start; every pinned version gets a fragment in each\n"
        "// edition where it is in force.\n"
        "// NOTA joins the fragment only where it carries applicability\n"
        "// (R262-7: decree 2025-185 from 01.03.2025; R262-9: decree 2023-1378\n"
        "// for resources from 01.01.2024); see sources/articles.json.\n"
        "// DSN amounts, declared resources, the L. 262-2 euro base and the\n"
        "// 1 April factor arrive as case inputs with provenance (DSS_PENDING).\n"
        "\n"
        'language "law.core" version "0.2";\n'
        'package fr.minima.ressources version "0.1.0";\n'
        f'namespace "{NS}";\n'
        "\n"
        "source CASF {\n"
        "    kind code;\n"
        "    jurisdiction FR;\n"
        '    label fr official "Code de l\'action sociale et des familles";\n'
        '    label en unofficial "French Social Action and Families Code";\n'
        "}\n"
    )
    editions = []
    for i, st in enumerate(starts):
        nxt = starts[i + 1] if i + 1 < len(starts) else None
        window = f"[@{st}, @{nxt})" if nxt else f"[@{st}, infinity)"
        editions.append((ed_name(st), st, window))
    for name, st, window in editions:
        header += (
            f"\n"
            f"edition {name} of CASF {{\n"
            f"    language fr;\n"
            f"    officiality official;\n"
            f"    materialization_status PINNED_UNOFFICIAL_COPY;\n"
            f"    in_force {window};\n"
            f'    label fr official "Code de l\'action sociale et des familles, état en vigueur à compter du {st}";\n'
            f'    label en unofficial "French Social Action and Families Code: pinned scope as in force from {st}";\n'
            f"}}\n"
        )

    # Per-edition fragments (APL pattern): a rule participates in the
    # computation only when one of its @source fragments belongs to the
    # edition open at legal_time, so every pinned version gets a fragment in
    # each edition where that version is in force. First edition keeps the
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
    frags = "\n// BEGIN GENERATED FR-MINIMA-RESSOURCES FRAGMENTS\n"
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
        })
    outputs["01-sources.law"] = (header + pubs + frags).encode("utf-8")
    # Depth-measure addressing (FINISH-W4 layout, CF pilot D-43): document
    # paths in the map are relative to the map directory. articles.json
    # lives inside sources/, so the resolver (boundaries.act_source:
    # declaration.parent / document) needs "editions/<name>.txt"; the
    # previous "sources/editions/<name>.txt" resolved to
    # sources/sources/... and the act measured NO_SOURCE. Top-level
    # "document" pins the current edition for the program window (coverage
    # from 2021-01-01, cutoff 2026-10-06): the last back-to-back edition,
    # open at the cutoff. Per-edition "scope" lists exactly the member
    # article numbers of that edition document (early editions do not
    # contain later norms; coverage is not backdated). The CASF
    # "Article R262-*" headers share the lettered-article shape with the
    # CSS/CCH precedents (D-43: APL already uses this convention).
    # Publication local_path values in 01-sources.law stay package-relative
    # ("sources/editions/...") for the pinning gate; source bytes, fragment
    # IDs, edition windows and provenance untouched.
    current_edition = editions[-1][0]
    outputs["sources/articles.json"] = (
        json.dumps({"cutoff": "2026-10-06", "coverage_start": COVERAGE_START,
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
            old = p.read_bytes() if p.exists() else None
            if old != blob:
                p.write_bytes(blob)
                print(f"write {rel} ({len(blob)} bytes)")
        print(f"versions={len(versions)} fragments={len(frag_rows)} "
              f"editions={len(editions)}")
        return
    # --check: every output must already match.
    bad = []
    for rel, blob in outputs.items():
        p = PKG / rel
        if not p.exists() or p.read_bytes() != blob:
            bad.append(rel)
    if bad:
        print("STALE: " + " ".join(bad))
        sys.exit(1)
    print(f"current: versions={len(versions)} fragments={len(frag_rows)} "
          f"editions={len(editions)}")


if __name__ == "__main__":
    main()
