#!/usr/bin/env python3
"""Pin the sources of package fr.pf.asf (CNAF wave 3, lane fr-cnaf-pf-small).

Reads the CSS registry (.scratch/reg-css.json, cut 2026-10-06) and builds:
  sources/css/<ARTICLE>.txt  - pinned text of the current version (registry alineas);
  sources/css/L523-1-2019.txt, L523-1-2018.txt, R523-7-20*.txt - superseded
                               versions from the mirror dump (reform pairs);
  sources/articles.json      - accounting: versions, NOTA, coverage, gaps,
                               per-edition fragments; edition documents are
                               map-relative ("editions/<name>.txt"), top-level
                               "document" is the current edition for the
                               program window (W4 depth layout, CF pilot D-43);
  sources/fragment-map.json  - version base fragment -> all edition fragments
                               (for @source authoring);
  01-sources.law              - source CSS, editions back to back, publications
                                (one per edition, all member texts verbatim),
                                fragments (one per pinned version per edition
                                where that version is in force, APL pattern:
                                a rule fires only when an @source fragment of
                                its article belongs to the edition open at
                                legal_time).

Scope: exactly 19 articles (L523-1/2/3, R523-1/2/3/3-1/3-2/4/5/6/7/8,
D523-1/2/3; DOM extension L755-17, D755-7, D755-8). Coverage D-01 from
2021-01-01; the superseded versions cover the 2021 windows (L523-1
predecessor 2019-12-28/2021-12-25, I. 1-4 word-identical per D-15; R523-7
2018-2022 at 37,50/28,13 %) and the 2015-2018 foreign windows (R523-7
yearly rates 2014-2018; L523-1 2018-2019 for the differential anchor).
The three DOM versions (L755-17 from 2015-10-16, D755-7 from 2018-07-01,
D755-8 from 1995-11-11) cover the whole program window with no future
versions; no DOM predecessors pinned. Own predecessor pin: this package
pins L523-1 2019-12-28 itself (pf-core is NOT edited; the pfcore-prev
line owns the pf-core anchors). 2021 cases compute: rules effective from
2021-01-01 at the latest, fragments in the 2021 editions.

NOTA is part of the fragment ONLY where it carries applicability
(R523-3-2, D523-1, D523-2: 2018 application; R523-7: 2022-11-01
application). Recorded per fragment in articles.json.

Usage:
  python3 corpus/laws/fr/pf-asf/tools/build_sources.py --check
  python3 corpus/laws/fr/pf-asf/tools/build_sources.py --write
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-asf"
REGISTRY = ROOT / ".scratch" / "reg-css.json"
MIRROR = ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006073189"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"

NS = "urn:fr:corpus:clir:pf-asf"

SCOPE = ["L523-1", "L523-2", "L523-3", "R523-1", "R523-2", "R523-3",
         "R523-3-1", "R523-3-2", "R523-4", "R523-5", "R523-6", "R523-7",
         "R523-8", "D523-1", "D523-2", "D523-3",
         "L755-17", "D755-7", "D755-8"]

# Superseded versions pinned from the mirror dump (fixed paths).
OLD = {
    # L523-1 predecessor (I. 1-4 word-identical to the current text, D-15):
    # own pin for this package's differential anchor; pf-core is untouched.
    "L523-1-PREV": {
        "num": "L523-1",
        "legi_id": "LEGIARTI000041398664",
        "debut": "2019-12-28", "fin": "2021-12-25",
        "xml": ("dump/article/LEGI/ARTI/00/00/41/39/86/"
                "LEGIARTI000041398664.xml"),
        "txt": "sources/css/L523-1-2019.txt",
        "frag": "CSS_L523_1_PREV",
    },
    # L523-1 2018-2019 (differential anchor for the 2018-04 foreign case).
    "L523-1-2018": {
        "num": "L523-1",
        "legi_id": "LEGIARTI000033728739",
        "debut": "2018-04-01", "fin": "2019-12-28",
        "xml": ("dump/article/LEGI/ARTI/00/00/33/72/87/"
                "LEGIARTI000033728739.xml"),
        "txt": "sources/css/L523-1-2018.txt",
        "frag": "CSS_L523_1_PRE2019",
    },
    # R523-7 yearly rates before 2022-11-01 (37,50/28,13 % until then).
    "R523-7-2014": {
        "num": "R523-7",
        "legi_id": "LEGIARTI000028878999",
        "debut": "2014-04-01", "fin": "2015-04-01",
        "xml": ("dump/article/LEGI/ARTI/00/00/28/87/89/"
                "LEGIARTI000028878999.xml"),
        "txt": "sources/css/R523-7-2014.txt",
        "frag": "CSS_R523_7_PRE2015",
    },
    "R523-7-2015": {
        "num": "R523-7",
        "legi_id": "LEGIARTI000030381064",
        "debut": "2015-04-01", "fin": "2016-04-03",
        "xml": ("dump/article/LEGI/ARTI/00/00/30/38/10/"
                "LEGIARTI000030381064.xml"),
        "txt": "sources/css/R523-7-2015.txt",
        "frag": "CSS_R523_7_PRE2016",
    },
    "R523-7-2016": {
        "num": "R523-7",
        "legi_id": "LEGIARTI000032363885",
        "debut": "2016-04-03", "fin": "2017-04-15",
        "xml": ("dump/article/LEGI/ARTI/00/00/32/36/38/"
                "LEGIARTI000032363885.xml"),
        "txt": "sources/css/R523-7-2016.txt",
        "frag": "CSS_R523_7_PRE2017",
    },
    "R523-7-2017": {
        "num": "R523-7",
        "legi_id": "LEGIARTI000034427380",
        "debut": "2017-04-15", "fin": "2018-04-01",
        "xml": ("dump/article/LEGI/ARTI/00/00/34/42/73/"
                "LEGIARTI000034427380.xml"),
        "txt": "sources/css/R523-7-2017.txt",
        "frag": "CSS_R523_7_PRE2018",
    },
    "R523-7-2018": {
        "num": "R523-7",
        "legi_id": "LEGIARTI000038249358",
        "debut": "2018-04-01", "fin": "2022-11-01",
        "xml": ("dump/article/LEGI/ARTI/00/00/38/24/93/"
                "LEGIARTI000038249358.xml"),
        "txt": "sources/css/R523-7-2018.txt",
        "frag": "CSS_R523_7_PRE2022",
    },
}

# Articles whose NOTA carries applicability and joins the fragment text.
NOTA_IN_FRAGMENT = {"R523-3-2", "D523-1", "D523-2", "R523-7"}


def frag_name(num: str) -> str:
    return "CSS_" + num.replace("-", "_")


def ed_name(state: str) -> str:
    return "CSS_ED" + state[:4] + "_" + state[5:7]


def edition_names(debuts):
    """Unique edition name per debut; day-disambiguated on same-month collision."""
    out = {}
    used = set()
    for st in debuts:
        base = ed_name(st)
        name = base if base not in used else base + "_" + st[8:10]
        assert name not in used, f"edition collision even by day: {st}"
        used.add(name)
        out[st] = name
    return out


def old_xml_alineas(xml_rel: str):
    """Extract alineas from a mirror-dump version XML (<br/> separated)."""
    p = MIRROR / xml_rel
    raw = p.read_text(encoding="utf-8")
    m = re.search(r"<BLOC_TEXTUEL>.*?</BLOC_TEXTUEL>", raw, re.S)
    assert m, f"no BLOC_TEXTUEL in {xml_rel}"
    body = m.group(0)
    body = re.sub(r"</p\s*>", "\n\n", body)
    body = re.sub(r"(<br\s*/>\s*){2,}", "\n\n", body)
    body = re.sub(r"<br\s*/>", " ", body)
    body = re.sub(r"<[^>]+>", "", body)
    parts = [re.sub(r"\s+", " ", t).strip()
             for t in body.split("\n\n")]
    parts = [t for t in parts if t]
    assert parts, f"no alineas in {xml_rel}"
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
            "txt": f"sources/css/{num}.txt", "frag": frag_name(num),
            "nota": nota_lines,
            "nota_in_fragment": num in NOTA_IN_FRAGMENT,
            "versions": [
                {"id": v["id"], "debut": v["debut"], "fin": v["fin"],
                 "etat": v["etat"]} for v in a.get("versions", [])],
            "xml_sha256": a.get("xml_sha256"),
            "xml_rel": a.get("xml_rel"),
        })
    for key, spec in OLD.items():
        num = spec.get("num", key)
        alineas, nota = old_xml_alineas(spec["xml"])
        text = "Article " + num + "\n" + "\n".join(alineas)
        nota_lines = [nota] if nota else []
        if nota_lines:
            text += "\n" + "\n".join("NOTA: " + n for n in nota_lines)
        versions.append({
            "num": num, "legi_id": spec["legi_id"], "debut": spec["debut"],
            "fin": spec["fin"], "etat": "MODIFIE", "text": text,
            "txt": spec["txt"], "frag": spec["frag"],
            "nota": nota_lines,
            "nota_in_fragment": True,
            "versions": [],
            "xml_sha256": hashlib.sha256(
                (MIRROR / spec["xml"]).read_bytes()).hexdigest(),
            "xml_rel": spec["xml"],
        })

    debuts = sorted({v["debut"] for v in versions})
    outputs = {}

    header = (
        "// Provenance S1: allocation de soutien familial (CSS, livre V, titre II,\n"
        "// chapitre III; DOM extension livre VII, titre V, chapitre 5, section 4). Block\n"
        "// generated by tools/build_sources.py from the registry\n"
        "// .scratch/reg-css.json (cut 2026-10-06; alineas and versions from\n"
        "// the DILA LEGI mirror) plus seven superseded version XMLs from\n"
        "// the mirror dump (old L523-1 I. 1-4 word-identical, D-15; old\n"
        "// R523-7 with the yearly rates 31,50-37,50 / 23,63-28,13 %).\n"
        "// Do not edit by hand.\n"
        "//\n"
        "// Coverage D-01 from 2021-01-01; the superseded versions cover the\n"
        "// 2021 windows (L523-1 predecessor until 2021-12-25, R523-7 2018\n"
        "// version until 2022-11-01) and the 2015-2018 foreign windows.\n"
        "// Editions run back to back from the earliest pinned debut. NOTA\n"
        "// joins the fragment only where it carries applicability\n"
        "// (R523-3-2, D523-1, D523-2, R523-7); see sources/articles.json.\n"
        "// they arrive as case inputs with provenance.\n"
        "\n"
        'language "law.core" version "0.2";\n'
        'package fr.pf.asf version "0.1.0";\n'
        f'namespace "{NS}";\n'
        "\n"
        "source CSS {\n"
        "    kind code;\n"
        "    jurisdiction FR;\n"
        '    label fr official "Code de la sécurité sociale";\n'
        '    label en unofficial "French Social Security Code";\n'
        "}\n"
    )
    ed_of = edition_names(debuts)
    editions = []
    for i, st in enumerate(debuts):
        nxt = debuts[i + 1] if i + 1 < len(debuts) else None
        window = f"[@{st}, @{nxt})" if nxt else f"[@{st}, infinity)"
        editions.append((ed_of[st], st, window))
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
                    fname = f"{v['frag']}_{ed_of[est][4:]}"
                frag_rows.append((ed_of[est], fname, v))

    pubs = ""
    frags = "\n// BEGIN GENERATED FR-PF-ASF FRAGMENTS\n"
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
    # contain later norms; coverage is not backdated). Day-disambiguated
    # edition names (CSS_ED2018_07 vs CSS_ED2018_07_27) are preserved.
    # Publication local_path values in 01-sources.law stay package-relative
    # ("sources/editions/...") for the pinning gate; source bytes, fragment
    # IDs, edition windows and provenance untouched.
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
    print(f"articles: 19, pinned versions: {len(versions)}, "
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

