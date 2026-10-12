#!/usr/bin/env python3
"""Pin the sources of package fr.css.ajpa (CNAF wave 3, lane fr-cnaf-pf-handicap).

Reads the CSS registry (.scratch/reg-css.json, cut 2026-10-06) and the DILA
LEGI mirror, and builds:
  sources/css/<ARTICLE>.txt      - pinned text of the current version
                                   (registry alineas);
  sources/css/<ARTICLE>-<date>.txt - pinned text of in-coverage superseded
                                   versions (mirror XML);
  sources/articles.json          - accounting: versions, NOTA, coverage, gaps,
                                   per-edition fragments, unit/scope/document
                                   declarations (D-43, map-relative paths);
  sources/fragment-map.json      - version base fragment -> all edition
                                   fragments (for @source authoring);
  01-sources.law                  - source CSS, editions back to back,
                                    publications (one per edition, all member
                                    texts verbatim), fragments (one per pinned
                                    version per edition where that version is
                                    in force, APL pattern).

Scope: exactly 9 articles (L168-8..16, allocation journalière du proche
aidant). In-coverage reforms pin the previous version as a reform pair
(pf-af _PRE<year> pattern):
  L168-9: 2019 version (decree amount + single majoration + modulation)
           + 2022-01 version (+SMIC revalorisation, NOTA deferred entry)
           + 2023-07 version (modulation only, 66-day career cap)
           + current 2025 (monthly max, duration ceiling + renewal);
  L168-10: 2019 version (10-item non-cumul list without the 2025 birth-leave
           item wording) + current 2025 (NOTA birth scope).
Pre-coverage versions are declared prev-text gaps: package coverage starts
2021-01-01 (L168-11 NOTA: service/control attribution in force then; same
window as the AJPP lane). In particular the 2019 L168-8 extended channel
(L544-8 persons, public agents, removed 2020-12-16) and the 2019 L168-11
service text are NOT pinned: boundary B-PFAJPA-AVANT2021.
The stillborn L168-9 version LEGIARTI000045061968 (MODIFIE_MORT_NE,
2024-01-01 to 2023-07-21, never in force) is NOT pinned: boundary note.
D168/R168 decree mechanics (daily SMIC euro figure, monthly max days,
duration ceiling, flat-day counts, recovery deadlines) are NOT pinned:
inventory PENDING_WAVE (unassigned); they arrive as case inputs with
provenance (B-PFAJPA-*) or DSS/CNAF/blind readings.

NOTA joins the fragment only where it carries applicability of the pinned
version (L168-9 2022 deferred entry + 2025 entry; L168-10 2025 immediate
entry + birth-date scope; L168-11 2021 entry). Recorded per fragment in
articles.json.

Usage:
  python3 corpus/laws/fr/ajpa/tools/build_sources.py --check
  python3 corpus/laws/fr/ajpa/tools/build_sources.py --write
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "ajpa"
REGISTRY = ROOT / ".scratch" / "reg-css.json"
MIRROR = ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006073189"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"

NS = "urn:fr:corpus:clir:css-ajpa"

SCOPE = ["L168-8", "L168-9", "L168-10", "L168-11", "L168-12",
         "L168-13", "L168-14", "L168-15", "L168-16"]

# In-coverage superseded versions: num -> list of
# (legi_id, debut, fin, frag_suffix, txt_suffix, nota_in_fragment).
OLD = {
    "L168-9": [("LEGIARTI000039787616", "2019-12-28", "2022-01-01",
                 "PRE2022", "2019-12-28", False),
                ("LEGIARTI000044628262", "2022-01-01", "2023-07-21",
                 "PRE2023", "2022-01-01", True),
                ("LEGIARTI000047864765", "2023-07-21", "2025-01-01",
                 "PRE2025", "2023-07-21", False)],
    "L168-10": [("LEGIARTI000039787618", "2019-12-28", "2025-12-31",
                 "PRE2026", "2019-12-28", False)],
}

# Current versions whose registry NOTA carries applicability.
NOTA_IN_FRAGMENT = {"L168-9", "L168-10", "L168-11"}

COVERAGE_START = "2021-01-01"

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
        "// Provenance S1: allocation journalière du proche aidant (CSS,\n"
        "// livre I, titre VI, chapitre 8: L. 168-8 à L. 168-16). Block\n"
        "// generated by tools/build_sources.py from the registry\n"
        "// .scratch/reg-css.json (cut 2026-10-06; current alineas) and the\n"
        "// DILA LEGI mirror (old versions). Do not edit by hand.\n"
        "//\n"
        "// Coverage D-01 from 2021-01-01 (L168-11 NOTA service/control\n"
        "// attribution; same window as the AJPP lane); in-coverage reforms\n"
        "// pin the previous version as a reform pair (pf-af _PRE<year>\n"
        "// pattern). Pre-coverage versions are declared prev-text gaps:\n"
        "// the 2019 L168-8 extended channel (L544-8 persons, public agents)\n"
        "// and the 2019 L168-11 service text (boundary B-PFAJPA-AVANT2021),\n"
        "// and the stillborn L168-9 LEGIARTI000045061968 (MODIFIE_MORT_NE,\n"
        "// never in force). Editions run back to back from the earliest\n"
        "// pinned debut. NOTA joins the fragment only where it carries\n"
        "// applicability (L168-9 2022 deferred entry + 2025 entry, L168-10\n"
        "// 2025 entry + birth scope, L168-11 2021 entry); see\n"
        "// sources/articles.json. D168/R168 decree mechanics are NOT pinned\n"
        "// (inventory PENDING_WAVE): they arrive as case inputs with\n"
        "// provenance.\n"
        "\n"
        'language "law.core" version "0.2";\n'
        'package fr.css.ajpa version "0.1.0";\n'
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
    # premise (per-carer keys); free-key generation runs only in the
    # latest edition (fr.pf.aeeh evidence).

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
    frags = "\n// BEGIN GENERATED FR-CSS-AJPA FRAGMENTS\n"
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
    # FINISH-W4 source layout (D-43): the depth/source gates resolve the
    # map relative to its own directory, read the division unit from each
    # edition entry (top level as fallback), and accept scope only as
    # "whole" or a list of actual article numbers — never a count.
    # Per-edition scope is the exact ed_members set: early pinned editions
    # do not retroactively gain later articles (B-PFAJPA-AVANT2021).
    ed_nums = {}
    for ed, _fname, v in frag_rows:
        ed_nums.setdefault(ed, set()).add(v["num"])
    ed_entries = [{"edition": name,
                   "document": f"editions/{name}.txt",
                   "unit": "fr_code_lettered_article",
                   "scope": [n for n in SCOPE if n in ed_nums.get(name, set())]}
                  for name, _st, _window in editions]
    outputs["sources/articles.json"] = (
        json.dumps({"cutoff": "2026-10-06", "coverage_start": COVERAGE_START,
                    "unit": "fr_code_lettered_article",
                    "scope": list(SCOPE),
                    "document": ed_entries[-1]["document"],
                    "pinned_versions": len(versions),
                    "fragments": len(frag_rows),
                    "editions": ed_entries,
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
