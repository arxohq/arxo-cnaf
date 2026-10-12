#!/usr/bin/env python3
"""Pin the sources of package fr.pf.ajpp (CNAF wave 3, lane fr-cnaf-pf-handicap).

Reads the CSS registry (.scratch/reg-css.json, cut 2026-10-06) and the DILA
LEGI mirror, and builds:
  sources/css/<ARTICLE>.txt      - pinned text of the current version
                                   (registry alineas);
  sources/css/<ARTICLE>-<date>.txt - pinned text of in-coverage superseded
                                   versions (mirror XML);
  sources/articles.json          - accounting: versions, NOTA, coverage, gaps,
                                   per-edition fragments;
  sources/fragment-map.json      - version base fragment -> all edition
                                   fragments (for @source authoring);
  01-sources.law                  - source CSS, editions back to back,
                                    publications (one per edition, all member
                                    texts verbatim), fragments (one per pinned
                                    version per edition where that version is
                                    in force, APL pattern).

Scope: exactly 22 articles (L544-2/3/4/6/7/8/9/10, D544-1..10,
R544-1/2/3; FINISH ajpp-death; D73 transfer L755-33). In-coverage reforms pin the previous
version as a reform pair (pf-af _PRE<year> pattern):
  L544-2: 2019 version (re-exam ceiling 12mo) + current 2026 (14mo);
  L544-3: 2021 version (exceptional once-renewal, no avance) + current 2023
           (+avance, "accord" not "accord explicite");
  L544-6: 2020 version (decree amount + single majoration) + 2023-01 version
           (+SMIC revalorisation) + current 2023-07 (majoration removed);
  L544-8: 2018 + 2022 versions (beneficiary-list citations) + current 2026;
  L544-9: 2018 version (9-item non-cumul list) + current 2025;
  D544-3: 2020 version (single beyond-max branch) + current 2022 (two
           branches 1°/2°);
  D544-6: 2020 version (BMAF rates 10.63/12.63/5.315/6.315 %) + current
           2022 (SMIC formula);
  D544-8: 2020 version (same content, «Pôle emploi») + current 2024
           («opérateur France Travail»);
  D544-9: 2010 version (same 5 items, older 4° citations) + current 2022;
  R544-1: 2008 + 2022 versions (same file, older citations; no renewal
           paragraph) + current 2024 (renewal paragraph);
  R544-3: 2006 version (favourable silence, initial request) + 2022
           version (renewal derogation: unfavourable) + current 2024
           (favourable silence, request and renewal).
Pre-coverage versions (L544-2 before 2019, L544-3 before 2021, L544-4/7
2000 texts, L544-6 before 2020-09, L544-8 before 2018-06, L544-9 before
2018-06, D544-1/2 before 2020-04, D544-3 before 2020-04, D544-4/5/7
before 2006-06, D544-6/8 before 2020-09, D544-9 before 2010-05, D544-10
before 2006-06, R544-1 before 2008-05, R544-2 before 2016-01, R544-3
before 2006-06, L755-33 before 2015-10-16) are declared prev-text gaps:
package coverage starts 2021-01-01 (upstream pf-core AJPP window), rules
open there.
L544-1 (base right, SANS_OWNER, ABROGE_DIFF with future end 2027-12-12) is
NOT pinned: boundary quote in REPORT only. L544-5 is gone from the code:
out of scope.

NOTA joins the fragment only where it carries applicability of the pinned
version (L544-8 2026 entry into force; L544-9 2025 immediate entry +
birth-date scope; L544-6 2023-01 deferred entry; D544-6 2022 payments
from 2022-01-01; D544-8 2024 entry 2024-07-01; D544-6/D544-8 2020
applicability to periods from 2020-09-30). Recorded per fragment in
articles.json.

Usage:
  python3 corpus/laws/fr/pf-ajpp/tools/build_sources.py --check
  python3 corpus/laws/fr/pf-ajpp/tools/build_sources.py --write
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-ajpp"
REGISTRY = ROOT / ".scratch" / "reg-css.json"
MIRROR = ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006073189"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"

NS = "urn:fr:corpus:clir:pf-ajpp"

SCOPE = ["L544-2", "L544-3", "L544-4", "L544-6",
         "L544-7", "L544-8", "L544-9", "L544-10",
         "D544-1", "D544-2", "D544-3", "D544-4", "D544-5",
         "D544-6", "D544-7", "D544-8", "D544-9", "D544-10",
         "R544-1", "R544-2", "R544-3", "L755-33"]

# In-coverage superseded versions: num -> list of
# (legi_id, debut, fin, frag_suffix, txt_suffix, nota_in_fragment).
OLD = {
    "L544-2": [("LEGIARTI000038219306", "2019-03-11", "2026-06-14",
                 "PRE2026", "2019-03-11", False)],
    "L544-3": [("LEGIARTI000038219297", "2019-03-11", "2021-11-17",
                 "PRE2021", "2019-03-11", False),
                ("LEGIARTI000044329330", "2021-11-17", "2023-07-21",
                 "PRE2023", "2021-11-17", False)],
    "L544-6": [("LEGIARTI000041398530", "2020-09-30", "2023-01-01",
                 "PRE2023", "2020-09-30", False),
                ("LEGIARTI000044628259", "2023-01-01", "2023-07-21",
                 "PRE2023_07", "2023-01-01", True)],
    "L544-8": [("LEGIARTI000037062458", "2018-06-14", "2022-07-01",
                 "PRE2022", "2018-06-14", False),
                ("LEGIARTI000044628251", "2022-07-01", "2026-01-01",
                 "PRE2026", "2022-07-01", False)],
    "L544-9": [("LEGIARTI000037062495", "2018-06-14", "2025-12-31",
                 "PRE2026", "2018-06-14", False)],
    "D544-3": [("LEGIARTI000041824233", "2020-04-26", "2022-04-30",
                 "PRE2022", "2020-04-26", False)],
    "D544-6": [("LEGIARTI000042389604", "2020-09-30", "2022-01-01",
                 "PRE2022", "2020-09-30", True)],
    "D544-8": [("LEGIARTI000042389611", "2020-09-30", "2024-07-01",
                 "PRE2024", "2020-09-30", True)],
    "D544-9": [("LEGIARTI000022266916", "2010-05-08", "2022-10-14",
                 "PRE2022", "2010-05-08", False)],
    "R544-1": [("LEGIARTI000045775691", "2008-05-01", "2022-04-30",
                 "PRE2022", "2008-05-01", False),
                ("LEGIARTI000045709278", "2022-04-30", "2024-02-05",
                 "PRE2024", "2022-04-30", False)],
    "R544-3": [("LEGIARTI000006750755", "2006-06-04", "2022-04-30",
                 "PRE2022", "2006-06-04", False),
                ("LEGIARTI000045709272", "2022-04-30", "2024-02-05",
                 "PRE2024", "2022-04-30", False)],
}

# Current versions whose registry NOTA carries applicability.
NOTA_IN_FRAGMENT = {"L544-8", "L544-9", "D544-6", "D544-8"}

INF = "2999-01-01"


def frag_name(num: str) -> str:
    return "CSS_" + num.replace("-", "_")


def ed_name(state: str) -> str:
    return "CSS_ED" + state[:4] + "_" + state[5:7]


def mirror_xml(legi_id: str):
    """Locate the mirror XML for a version id (dump first, then increments)."""
    n = legi_id[8:18]
    d = f"{n[0:2]}/{n[2:4]}/{n[4:6]}/{n[6:8]}/{n[8:10]}"
    rel = f"article/LEGI/ARTI/{d}/{legi_id}.xml"
    cands = [("dump/" + rel, MIRROR / "dump" / rel)]
    incs = MIRROR / "increments"
    if incs.is_dir():
        for inc in sorted(incs.iterdir(), reverse=True):
            cands.append((f"increments/{inc.name}/{rel}", inc / rel))
    for label, p in cands:
        if p.exists():
            return label, p
    return None, None


def xml_blocks(xml_text: str, tag: str):
    return re.findall(rf"<{tag}>(.*?)</{tag}>", xml_text, re.S)


def clean(block: str) -> str:
    b = re.sub(r"<[^>]+>", " ", block)
    return re.sub(r"\s+", " ", b).strip()


def xml_alineas(xml_text: str):
    out = []
    for bt in xml_blocks(xml_text, "BLOC_TEXTUEL"):
        for c in re.findall(r"<CONTENU>(.*?)</CONTENU>", bt, re.S):
            b = clean(c)
            if b:
                out.append(b)
    return out


def xml_nota(xml_text: str):
    out = []
    for nb in xml_blocks(xml_text, "NOTA"):
        for c in re.findall(r"<CONTENU>(.*?)</CONTENU>", nb, re.S):
            b = clean(c)
            if b:
                out.append(b)
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

    # Collect pinned versions: current per article + in-coverage olds.
    versions = []
    for num in SCOPE:
        a = by_num[num]
        nota_lines = a.get("nota", [])
        text = "Article " + num + "\n" + "\n".join(a["alineas"])
        if num in NOTA_IN_FRAGMENT and nota_lines:
            text += "\n" + "\n".join("NOTA: " + n for n in nota_lines)
        versions.append({
            "num": num, "legi_id": a["id"], "debut": a["debut"],
            "fin": a["fin"], "etat": a["etat"], "text": text,
            "txt": f"sources/css/{num}.txt", "frag": frag_name(num),
            "nota": nota_lines,
            "nota_in_fragment": num in NOTA_IN_FRAGMENT,
            "xml_sha256": a.get("xml_sha256"),
            "xml_rel": a.get("xml_rel"),
            "gap": None,
            "versions": a.get("versions", []),
        })
        for legi_id, debut, fin, suffix, txt_date, nota_join in OLD.get(num, []):
            assert fin > debut, f"stillborn {legi_id}"
            label, path = mirror_xml(legi_id)
            assert path is not None, f"mirror XML missing: {legi_id}"
            xml_text = path.read_text(encoding="utf-8")
            alineas = xml_alineas(xml_text)
            assert alineas, f"no alineas in {legi_id}"
            old_nota = xml_nota(xml_text)
            old_text = "Article " + num + "\n" + "\n".join(alineas)
            if nota_join and old_nota:
                old_text += "\n" + "\n".join("NOTA: " + n for n in old_nota)
            xml_bytes = path.read_bytes()
            versions.append({
                "num": num, "legi_id": legi_id, "debut": debut,
                "fin": fin, "etat": "MODIFIE", "text": old_text,
                "txt": f"sources/css/{num}-{txt_date}.txt",
                "frag": frag_name(num) + "_" + suffix,
                "nota": old_nota,
                "nota_in_fragment": bool(nota_join and old_nota),
                "xml_sha256": hashlib.sha256(xml_bytes).hexdigest(),
                "xml_rel": label,
                "gap": None,
                "versions": a.get("versions", []),
            })

    debuts = sorted({v["debut"] for v in versions})
    outputs = {}

    header = (
        "// Provenance S1: daily parental-presence allowance (CSS, livre V,\n"
        "// titre IV, chapitre 4: L. 544-2/3/4/6/7/8/9/10, D. 544-1..10,\n"
        "// R. 544-1/2/3; livre VII, titre V, chapitre 5: L. 755-33).\n"
        "// Block generated by tools/build_sources.py from\n"
        "// the registry .scratch/reg-css.json (cut 2026-10-06; current\n"
        "// alineas) and the DILA LEGI mirror (old versions). Do not edit\n"
        "// by hand.\n"
        "//\n"
        "// Coverage D-01 from 2021-01-01 (upstream pf-core AJPP window);\n"
        "// in-coverage reforms pin the previous version as a reform pair\n"
        "// (pf-af _PRE<year> pattern). Pre-coverage versions are declared\n"
        "// prev-text gaps. Editions run back to back from the earliest\n"
        "// pinned debut. NOTA joins the fragment only where it carries\n"
        "// applicability (L544-8, L544-9, D544-6, D544-8 current; L544-6\n"
        "// 2023-01; D544-6/D544-8 2020); see sources/articles.json.\n"
        "// L544-1 (base right, SANS_OWNER, ABROGE_DIFF) is a boundary quote\n"
        "// in REPORT, not pinned.\n"
        "\n"
        'language "law.core" version "0.2";\n'
        'package fr.pf.ajpp version "0.1.0";\n'
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
    # each edition where that version is in force. The first in-force
    # edition keeps the version base name; later editions append
    # _ED<YYYY>_<MM>. Bound-key rule: amount rules bind every keyed
    # premise (per-child/month keys); free-key generation runs only in the
    # latest edition (see fr.pf.aeeh B-PFAEEH-TETE note pattern).

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
    frags = "\n// BEGIN GENERATED FR-PF-AJPP FRAGMENTS\n"
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
    # Depth-measure addressing (fr-cnaf D-43, pf-cf pattern): the map
    # declares the lettered-article unit, the scope as a number list, and
    # document paths relative to the map directory (sources/), so the
    # resolver finds editions/<name>.txt. Publication local_path values in
    # 01-sources.law stay package-relative for the pinning gate.
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
