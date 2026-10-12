#!/usr/bin/env python3
"""Pin the sources of package fr.pf.af (CNAF wave 1, lane fr-cnaf-pf-af).

Reads the CSS registry (.scratch/reg-css.json, cut 2026-10-06) and builds:
  sources/css/<ARTICLE>.txt  - pinned text of the current version (registry alineas);
  sources/css/R521-1-2008.txt, D521-3-2015.txt - superseded versions from the
                               mirror dump (reform pairs);
  sources/articles.json      - accounting: versions, NOTA, coverage, gaps,
                               per-edition fragments;
  sources/fragment-map.json  - version base fragment -> all edition fragments
                               (for @source authoring);
  01-sources.law              - source CSS, editions back to back, publications
                                (one per edition, all member texts verbatim),
                                fragments (one per pinned version per edition
                                where that version is in force, APL pattern:
                                a rule fires only when an @source fragment of
                                its article belongs to the edition open at
                                legal_time).

Scope: exactly 15 articles (L521-1/2/3, R521-1..4, D521-1..4, L755-11/12,
D755-5, D755-5-1). Coverage D-01 from 2021-01-01; earlier pinned versions
exist because foreign cases require them (Catala 2019-2022, OpenFisca
2015-2026). D755-5-1 arrives via the FINISH DOM transfer (D-73); its single
VIGUEUR version (debut 2015-07-01, dump XML) covers the whole window, so no
predecessor is pinned and its debut introduces no new edition.

NOTA is part of the fragment ONLY where it carries applicability (R521-1 both
versions: transitional cohorts of decrees 2008-409 and 2026-138; L521-2:
ordonnance 2019-950 application). Recorded per fragment in articles.json.

Usage:
  python3 corpus/laws/fr/pf-af/tools/build_sources.py --check
  python3 corpus/laws/fr/pf-af/tools/build_sources.py --write
"""

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-af"
REGISTRY = ROOT / ".scratch" / "reg-css.json"
MIRROR = ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006073189"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"

NS = "urn:fr:corpus:clir:pf-af"

SCOPE = ["L521-1", "L521-2", "L521-3", "R521-1", "R521-2", "R521-3", "R521-4",
         "D521-1", "D521-2", "D521-3", "D521-4", "L755-11", "L755-12", "D755-5",
         "D755-5-1"]

# Superseded versions pinned from the mirror dump (fixed paths).
OLD = {
    "R521-1": {
        "legi_id": "LEGIARTI000018735853",
        "debut": "2008-04-30", "fin": "2026-03-01",
        "xml": ("dump/article/LEGI/ARTI/00/00/18/73/58/"
                "LEGIARTI000018735853.xml"),
        "txt": "sources/css/R521-1-2008.txt",
        "frag": "CSS_R521_1_PRE2026",
    },
    "D521-3": {
        "legi_id": "LEGIARTI000030678079",
        "debut": "2015-07-01", "fin": "2022-01-01",
        "xml": ("dump/article/LEGI/ARTI/00/00/30/67/80/"
                "LEGIARTI000030678079.xml"),
        "txt": "sources/css/D521-3-2015.txt",
        "frag": "CSS_D521_3_PRE2022",
    },
    # L521-2 before the 2021-09-30 ASE wording: only al. 4 differs from the
    # current text, by a bare cross-reference update (ord. 45-174 articles
    # 15/16/16 bis/28 -> CJPM L. 323-1); normative content identical
    # (alinea diff verified 2026-10-06). Rules on L. 521-2 cite both versions.
    "L521-2": {
        "legi_id": "LEGIARTI000052043015",
        "debut": "2015-03-22", "fin": "2021-09-30",
        "xml": ("increments/LEGI_20250804-215726/article/LEGI/ARTI/00/00/52/"
                "04/30/LEGIARTI000052043015.xml"),
        "txt": "sources/css/L521-2-2015.txt",
        "frag": "CSS_L521_2_PRE2021",
    },
}

# Articles whose NOTA carries applicability and joins the fragment text.
NOTA_IN_FRAGMENT = {"R521-1", "L521-2"}

# CNAF letter LR-2026-051 (inbox 2026-10-06): application dates and examples
# of the 14->18 majoration reform (decree 2026-138). Pinned as official PDF
# bytes plus extracted layout text; fragments slice exact .txt line ranges
# (1-based, inclusive).
LR_URL = ("https://www.caf.fr/sites/default/files/medias/cnaf/Nous_connaitre/"
          "qui%20sommes%20nous/Textes%20de%20r%C3%A9f%C3%A9rence/Circulaires/"
          "2026/LR-2026-051.pdf")
LR_PDF = "sources/cnaf-lr-2026-051.pdf"
LR_TXT = "sources/cnaf-lr-2026-051.txt"
LR_FRAGS = [
    ("CNAF_LR_2026_051_SYNTHESE", "guidance",
     "lettre-reseau/LR-2026-051/synthese", 52, 57),
    ("CNAF_LR_2026_051_RESUME", "guidance",
     "lettre-reseau/LR-2026-051/en-resume", 135, 142),
]


def lr_block() -> str:
    pdf = (PKG / LR_PDF).read_bytes()
    txt = (PKG / LR_TXT).read_bytes()
    lines = txt.decode("utf-8").split("\n")
    pdf_h = "sha256:" + hashlib.sha256(pdf).hexdigest()
    txt_h = "sha256:" + hashlib.sha256(txt).hexdigest()
    b = ["\n// BEGIN GENERATED FR-PF-AF CNAF DOCUMENTS\n"]
    b.append("source CNAF_LR_2026_051 {\n"
             "    kind guidance;\n"
             "    jurisdiction FR;\n"
             '    label fr official "Lettre au réseau CNAF n° LR-2026-051 du 26 février 2026 : report de l’âge ouvrant droit à la majoration des allocations familiales";\n'
             '    label en unofficial "CNAF network letter LR-2026-051 of 26 February 2026: rise of the age opening the family-allowance age supplement";\n'
             "}\n")
    for ed, window, label_fr, label_en in (
            ("CNAF_LR_2026_051_PDF", "[@2026-03-01, infinity)",
             "LR-2026-051 : bytes officiels du PDF (caf.fr, circulaire CNAF)",
             "LR-2026-051: official PDF bytes (caf.fr, CNAF circular)"),
            ("CNAF_LR_2026_051_TEXT", "[@2026-03-01, infinity)",
             "LR-2026-051 : texte de mise en page extrait du PDF officiel",
             "LR-2026-051: layout text extracted from the official PDF")):
        b.append(f"\nedition {ed} of CNAF_LR_2026_051 {{\n"
                 "    language fr;\n"
                 "    officiality official;\n"
                 "    materialization_status PINNED_OFFICIAL_BYTES;\n"
                 f"    in_force {window};\n"
                 f'    label fr official "{label_fr}";\n'
                 f'    label en unofficial "{label_en}";\n'
                 "}\n")
    b.append(f"\npublication CNAF_LR_2026_051_PDF_BYTES of CNAF_LR_2026_051_PDF {{\n"
             '    media_type "application/pdf";\n'
             f'    uri "{LR_URL}";\n'
             f"    retrieved_at {RETRIEVED_AT};\n"
             f'    content_hash "{pdf_h}";\n'
             f'    local_path "{LR_PDF}";\n'
             "}\n")
    b.append(f"\npublication CNAF_LR_2026_051_TEXT_TXT of CNAF_LR_2026_051_TEXT {{\n"
             '    media_type "text/plain; charset=utf-8";\n'
             f'    uri "{LR_URL}";\n'
             f"    retrieved_at {RETRIEVED_AT};\n"
             f'    content_hash "{txt_h}";\n'
             f'    local_path "{LR_TXT}";\n'
             "}\n")
    for fid, kind, locator, a, zz in LR_FRAGS:
        text = "\n".join(lines[a - 1:zz])
        fh = "sha256:" + hashlib.sha256((text + "\n").encode("utf-8")).hexdigest()
        b.append(f"\n@id(\"{NS}#{fid}\")\n"
                 f"pub fragment {fid} in CNAF_LR_2026_051_TEXT {{\n"
                 f"    kind {kind};\n"
                 f'    locator "{locator}";\n'
                 f'    text fr official """{text}\n'
                 '""";\n'
                 f'    content_hash "{fh}";\n'
                 "}\n")
    b.append("\n// END GENERATED FR-PF-AF CNAF DOCUMENTS\n")
    return "".join(b)


def frag_name(num: str) -> str:
    return "CSS_" + num.replace("-", "_")


def ed_name(state: str) -> str:
    return "CSS_ED" + state[:4] + "_" + state[5:7]


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
    for num, spec in OLD.items():
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
        "// Provenance S1: allocations familiales (CSS, livre V, titre II,\n"
        "// chapitre 1er; DOM: livre VII, chapitre V). Block generated by\n"
        "// tools/build_sources.py from the registry .scratch/reg-css.json\n"
        "// (cut 2026-10-06; alineas and versions from the DILA LEGI mirror)\n"
        "// plus two superseded version XMLs from the mirror dump (old R521-1\n"
        "// with 14 ans, old D521-3 with the arrete mechanism in III).\n"
        "// Do not edit by hand.\n"
        "//\n"
        "// Coverage D-01 from 2021-01-01; earlier pinned versions exist\n"
        "// because foreign cases require them (Catala 2019-2022, OpenFisca\n"
        "// 2015-2026). Editions run back to back from the earliest pinned debut.\n"
        "// NOTA joins the fragment only where it carries applicability\n"
        "// (R521-1 both versions, L521-2); see sources/articles.json.\n"
        "// BMAF euro figures and yearly applicable plafond values are published\n"
        "// by DSS instructions DSS/2B/2026/46 and DSS/2B/2025/177, pinned in\n"
        "// fr.css.revalorisation (phase W0-06); they arrive here as case inputs\n"
        "// with provenance. The text of decree 2026-138 itself is NOT pinned\n"
        "// (owner input D-Q4); its application dates and the majoration examples\n"
        "// arrive via the pinned CNAF letter LR-2026-051 (source CNAF_LR_2026_051\n"
        "// below, edition in force from 2026-03-01).\n"
        "\n"
        'language "law.core" version "0.2";\n'
        'package fr.pf.af version "0.1.0";\n'
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
    frags = "\n// BEGIN GENERATED FR-PF-AF FRAGMENTS\n"
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
        gap = None
        if v["num"] == "L521-2" and v["legi_id"] == by_num["L521-2"]["id"]:
            gap = "prev-text-unpinned"
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
            "gap": gap,
            "versions": v["versions"],
        })
    outputs["01-sources.law"] = (header + pubs + frags + lr_block()).encode("utf-8")
    # W4 source map (D-43/CF shape): unit declared at the top and per
    # edition, scopes as article-number lists (early editions hold only
    # the norms already in force there), document paths relative to
    # sources/articles.json, top document = the current pinned edition.
    ed_scopes = {}
    for _ed, _fname, _v in frag_rows:
        ed_scopes.setdefault(_ed, set()).add(_v["num"])
    outputs["sources/articles.json"] = (
        json.dumps({"cutoff": "2026-10-06", "coverage_start": "2021-01-01",
                    "scope": list(SCOPE),
                    "unit": "fr_code_lettered_article",
                    "pinned_versions": len(versions),
                    "fragments": len(frag_rows),
                    "document": f"editions/{editions[-1][0]}.txt",
                    "editions": [{"edition": name,
                                   "unit": "fr_code_lettered_article",
                                   "scope": sorted(ed_scopes.get(name, set())),
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
    # contiguity: editions cover [first debut, infinity) without holes.
    for i in range(len(debuts) - 1):
        pass  # windows are adjacent by construction from sorted debuts
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
