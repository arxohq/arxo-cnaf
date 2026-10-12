#!/usr/bin/env python3
"""Pin the sources of package fr.pf.cf (CNAF wave 3, lane fr-cnaf-pf-small).

Reads the CSS registry (.scratch/reg-css.json, cut 2026-10-06) and builds:
  sources/css/<ARTICLE>.txt  - pinned text of the current version (registry alineas);
  sources/css/R522-2-2011.txt, R522-4-2014.txt, D522-2-2017.txt - superseded
                               versions from the mirror dump (reform pairs);
  sources/articles.json      - accounting: versions, NOTA, coverage, gaps,
                               per-edition fragments; edition documents are
                               map-relative ("editions/<name>.txt"), top-level
                               "document" is the current edition for the
                               program window (depth pilot);
  sources/fragment-map.json  - version base fragment -> all edition fragments
                               (for @source authoring);
  01-sources.law              - source CSS, editions back to back, publications
                                (one per edition, all member texts verbatim),
                                fragments (one per pinned version per edition
                                where that version is in force, APL pattern:
                                a rule fires only when an @source fragment of
                                its article belongs to the edition open at
                                legal_time).

Scope: exactly 17 articles (L522-1/2/3, R522-1/2/3/4, D522-1/2 plus the DOM
CF transfer L755-16/16-1, R755-1/2/3/4, D755-6/6-1). Coverage D-01 from
2021-01-01; the three superseded metropolitan versions cover the 2021-2022
windows (R522-2/R522-4 until 2022-10-29) and the January-March 2018 foreign
window (D522-2 at 58,33 % until 2018-04-01). All eight DOM current versions
cover the whole program window, so no DOM predecessor is pinned. Editions
are monthly: debuts sharing a YYYY-MM form one edition starting at the
earliest debut (2017-04-01 DOM + 2017-04-15 D522-2-PRE2018 share
CSS_ED2017_04; existing edition/fragment names are preserved).

NOTA is part of the fragment ONLY where it carries applicability (R522-3:
2014-01-01 application; D522-2 both versions: 2018-04-01 application).
Recorded per fragment in articles.json.

Usage:
  python3 corpus/laws/fr/pf-cf/tools/build_sources.py --check
  python3 corpus/laws/fr/pf-cf/tools/build_sources.py --write
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-cf"
REGISTRY = ROOT / ".scratch" / "reg-css.json"
MIRROR = ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006073189"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"

NS = "urn:fr:corpus:clir:pf-cf"

SCOPE = ["L522-1", "L522-2", "L522-3", "R522-1", "R522-2", "R522-3",
         "R522-4", "D522-1", "D522-2",
         "L755-16", "L755-16-1",
         "R755-1", "R755-2", "R755-3", "R755-4",
         "D755-6", "D755-6-1"]

# Superseded versions pinned from the mirror dump (fixed paths).
OLD = {
    "R522-2": {
        "legi_id": "LEGIARTI000024665358",
        "debut": "2011-11-01", "fin": "2022-10-29",
        "xml": ("dump/article/LEGI/ARTI/00/00/24/66/53/"
                "LEGIARTI000024665358.xml"),
        "txt": "sources/css/R522-2-2011.txt",
        "frag": "CSS_R522_2_PRE2022",
    },
    "R522-4": {
        "legi_id": "LEGIARTI000028878986",
        "debut": "2014-04-01", "fin": "2022-10-29",
        "xml": ("dump/article/LEGI/ARTI/00/00/28/87/89/"
                "LEGIARTI000028878986.xml"),
        "txt": "sources/css/R522-4-2014.txt",
        "frag": "CSS_R522_4_PRE2022",
    },
    # D522-2 before the 2018-04-01 majoré rate (58,33 % vs 62,48 %):
    # normative content differs, January-March 2018 foreign cases need it.
    "D522-2": {
        "legi_id": "LEGIARTI000034427374",
        "debut": "2017-04-15", "fin": "2018-04-01",
        "xml": ("dump/article/LEGI/ARTI/00/00/34/42/73/"
                "LEGIARTI000034427374.xml"),
        "txt": "sources/css/D522-2-2017.txt",
        "frag": "CSS_D522_2_PRE2018",
    },
}

# Articles whose NOTA carries applicability and joins the fragment text.
NOTA_IN_FRAGMENT = {"R522-3", "D522-2"}


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



DSS_DIR = PKG / "sources" / "dss-plafonds"
EDITION_OPEN = "[@2018-01-01, infinity)"


def _source_block(src, kind, number, label_fr, label_en):
    out = [f"source {src} {{", f"    kind {kind};", "    jurisdiction FR;"]
    if number:
        out.append(f'    number "{number}";')
    out += [f'    label fr official "{label_fr}";', f'    label en unofficial "{label_en}";', "}", ""]
    return out


def _text_block(edition, src, ed_label_fr, ed_label_en, text, uri, retrieved, local_path, fragment, frag_kind, locator):
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return [
        f"edition {edition} of {src} {{", "    language fr;", "    officiality official;",
        "    materialization_status PINNED_UNOFFICIAL_COPY;", f"    in_force {EDITION_OPEN};",
        f'    label fr official "{ed_label_fr}";', f'    label en unofficial "{ed_label_en}";', "}", "",
        f"publication {edition}_TEXT of {edition} {{", '    media_type "text/plain; charset=utf-8";',
        f'    uri "{uri}";', f"    retrieved_at {retrieved};", f'    content_hash "sha256:{digest}";',
        f'    local_path "{local_path}";', "}", "",
        f'@id("{NS}#{fragment}")', f"pub fragment {fragment} in {edition} {{", f"    kind {frag_kind};",
        f'    locator "{locator}";', f'    text fr official """{text}""";', f'    content_hash "sha256:{digest}";',
        "}", ""]


def dss_blocks():
    """D-83: срезы инструкций DSS (плафоны CF и montant majoré) — байты fr.css.revalorisation."""
    manifest = json.loads((DSS_DIR / "manifest.json").read_text(encoding="utf-8"))
    out = ["// ---- published ceilings, D-83 (sources/dss-plafonds/, tools/pin_plafonds_dss.py) ----", ""]
    declared = set()
    for row in manifest["texts"]:
        text = (PKG / row["slice"]).read_text(encoding="utf-8")
        src = row["source"]
        if src not in declared:
            declared.add(src)
            out += _source_block(src, "regulation", None, row["label_fr"], row["label_en"])
        kind = {"cf": "CF", "majore": "MAJORE", "reconduction": "RECONDUCTION"}[row["kind"]]
        what = {"cf": ("plafonds de ressources du complément familial (base et majorations publiées)",
                       "complement familial resource ceilings (published base and increments)"),
                "majore": ("plafonds de ressources du montant majoré (base et majorations publiées)",
                           "increased-amount resource ceilings (published base and increments)"),
                "reconduction": ("reconduction à l'identique des plafonds 2016 sur 2017",
                                 "identical carry-over of the 2016 ceilings to 2017")}[row["kind"]]
        fragment = f"{src}_{kind}"
        out += _text_block(
            fragment + "_ED", src,
            f"{row['instruction'].upper().replace('-', ' ')} : {what[0]} (octets de fr.css.revalorisation, lignes {row['line_from']}-{row['line_to']})",
            f"{row['instruction']}: {what[1]} (bytes of fr.css.revalorisation, lines {row['line_from']}-{row['line_to']})",
            text, row["uri"], row["retrieved_at"], row["slice"], fragment, "table",
            f"instruction/{row['instruction']}/lines/{row['line_from']}-{row['line_to']}")
    return out

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

    # Editions are monthly snapshots (ed_name keys on YYYY-MM): debuts that
    # share a month form ONE edition starting at the earliest debut. This
    # keeps existing edition/fragment names stable when a new pinned debut
    # (DOM 2017-04-01) joins an occupied month (D522-2-PRE2018 2017-04-15):
    # CSS_ED2017_04 widens to [@2017-04-01, @2018-01-01), no rename.
    # Membership of an edition [s, e) is "in force at s, or debuting inside
    # [s, e)" (member() below): without the second limb the mid-month
    # D522-2-PRE2018 bare fragment would move editions and strand existing
    # @source anchors. The widened ED2017_04 therefore carries PRE2018 from
    # 2017-04-01 although the version starts 2017-04-15; no rule can observe
    # the 14-day overhang (the sole citing rule is effective from
    # 2018-01-01, no tests read the window).
    months = {}
    for v in versions:
        months.setdefault(v["debut"][:7], []).append(v["debut"])
    debuts = sorted(min(ds) for ds in months.values())
    outputs = {}

    header = (
        "// Provenance S1: complement familial (CSS, livre V, titre II,\n"
        "// chapitre II, plus livre VII, titre V, chapitre 5 DOM: L755-16/16-1,\n"
        "// R755-1/2/3/4, D755-6/6-1). Block generated by tools/build_sources.py\n"
        "// from the registry .scratch/reg-css.json (cut 2026-10-06; alineas\n"
        "// and versions from the DILA LEGI mirror) plus three superseded\n"
        "// metropolitan version XMLs from the mirror dump (old R522-2/R522-4\n"
        "// with the arrete mechanism in the last alinea; old D522-2 with the\n"
        "// 58,33 % majore rate). All DOM current versions cover the program\n"
        "// window, so no DOM predecessor is pinned.\n"
        "// Do not edit by hand.\n"
        "//\n"
        "// Coverage D-01 from 2021-01-01; the superseded versions cover the\n"
        "// 2021-2022 windows (R522-2/R522-4 until 2022-10-29) and the\n"
        "// January-March 2018 foreign window (D522-2 58,33 %). Editions run\n"
        "// back to back from the earliest pinned debut; editions are monthly\n"
        "// (shared YYYY-MM debuts form one edition at the earliest debut).\n"
        "// NOTA joins the fragment only where it carries applicability\n"
        "// (R522-3, D522-2); DOM NOTAs restate version debuts or pre-window\n"
        "// history and stay outside fragments; see sources/articles.json.\n"
        "// BMAF and L755-3 euro figures are NOT pinned here (DSS_PENDING for\n"
        "// L755-3): they arrive as case inputs with provenance. The yearly\n"
        "// published ceilings (base, increments; D-83) are pinned in the blocks at\n"
        "// the end of the file (sources/dss-plafonds/; tools/pin_plafonds_dss.py).\n"
        "// The PASS arretes are pinned by the package fr.css.pass (D-84).\n"
        "\n"
        'language "law.core" version "0.2";\n'
        'package fr.pf.cf version "0.1.0";\n'
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

    def member(v_debut, v_fin, start, nxt):
        if in_force(v_debut, v_fin, start):
            return True
        if nxt is None:
            return v_debut >= start
        return start <= v_debut < nxt

    ed_starts = [st for _, st, _ in editions]
    ed_ends = ed_starts[1:] + [None]
    frag_rows = []  # (edition, frag_name, version)
    for v in versions:
        first = True
        for est, nxt in zip(ed_starts, ed_ends):
            if member(v["debut"], v["fin"], est, nxt):
                if first:
                    fname = v["frag"]
                    first = False
                else:
                    fname = f"{v['frag']}_ED{est[:4]}_{est[5:7]}"
                frag_rows.append((ed_name(est), fname, v))

    pubs = ""
    frags = "\n// BEGIN GENERATED FR-PF-CF FRAGMENTS\n"
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
    extra = "\n".join(dss_blocks())
    outputs["01-sources.law"] = (header + pubs + frags + "\n" + extra).encode("utf-8")
    # Depth-measure addressing (finish-depth pilot): document paths in the
    # map are relative to the map directory. articles.json lives inside
    # sources/, so the resolver (boundaries.act_source: declaration.parent /
    # document) needs "editions/<name>.txt"; the previous
    # "sources/editions/<name>.txt" resolved to sources/sources/... and the
    # act measured NO_SOURCE. Top-level "document" pins the current edition
    # for the program window (coverage from 2021-01-01, cutoff 2026-10-06):
    # the last back-to-back edition, open at the cutoff. Publication
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
