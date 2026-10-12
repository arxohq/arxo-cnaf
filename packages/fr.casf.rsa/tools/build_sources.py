#!/usr/bin/env python3
"""Pin the sources of package fr.casf.rsa (CNAF wave 4, W4-RSA).

Reads the registries (.scratch/reg-*.json, cut 2026-10-06) and builds:
  sources/casf/<ARTICLE>[-<TAG>].txt   - pinned CASF versions;
  sources/ctrav/<ARTICLE>[-<TAG>].txt  - pinned Code du travail versions;
  sources/jorf/ART12.txt               - decree 2025-478 article 12;
  sources/articles.json                - accounting: versions, NOTA,
                                         coverage, gaps, per-edition fragments;
  sources/fragment-map.json            - version base fragment -> all edition
                                         fragments (for @source authoring);
  01-sources.law                       - sources CASF / CODE_TRAVAIL /
                                         DECRET_2025_478, editions back to back
                                         from 2021-01-01 (D-01), publications
                                         (one per edition, all member texts
                                         verbatim), fragments (one per pinned
                                         version per edition where that
                                         version is in force, APL pattern).

Scope: CASF L. 262-2/3/4/5/6/9/27/28/29/30/31/34/37/38/39/45/46/47 and
R. 262-1/2/5/39/68(-1..-7)/69(-1..-8)/88/89/90/92/92-1/93/94/94-1, Code du
travail L. 5411-6, decree 2025-478 article 12 (article 13 only charges
ministers with execution: no case content, not pinned), plus the finish
wave (FINISH-W1 group rsa): D. 262-25-1/25-2/25-3/25-4 (young workers),
D. 262-26/27/28/29/30 (claim filing and instruction), D. 262-61/62/63/64
(department-body conventions), D. 262-65/65-2/65-2-1/73 (duties and
orientation), D. 262-77/94-2 (control and recovery bridge),
D. 262-95/96/97/98/99/100 (statistics), plus the six decrees revaluing the
RSA montant forfaitaire 2020-2025 (article 1 of decrees 2020-490, 2021-530,
2022-699, 2023-340, 2024-396, 2025-293; texts pinned by
tools/pin_mf_decrets.py into sources/decrets-mf/, one source/edition/
publication/fragment per decree: DECRET_<year>_<no>, DEC<year>_<no>,
DEC<year>_<no>_ART1; their euro figures feed the bareme parameter
MontantForfaitaireDecret), plus article 9 of law 2022-1158 (coefficient 1.04
from 1 July 2022: LOI_2022_1158, LOI2022_1158, LOI_2022_1158_ART9; its
coefficient feeds the bareme parameter CoefficientLoi2022).

Superseded versions (in force at some point in [2021-01-01, +inf)) are
derived from each record's `versions` history; TAG marks the version end
(PRE2025 = in force until 2025-01-01, PRE202506 = until 2025-06-01,
PRE202606 = until 2026-06-27).

NOTA joins the fragment only where it carries applicability (entry into
force of the plein-emploi rewrite, of the 2024 recovery rewrite, of the
2025 residence rewrite, of the 2021 recovery procedure); see
sources/articles.json. The L. 262-2 euro base (decree, unpinned) and the
1 April L. 161-25 factor: the pinned decrees (2020-2025) now build the base
(MontantForfaitaireDecret) and article 9 of law 2022-1158 bridges the window
2022-07..2023-03 (decree 2022-699 x 1.04, a reading); outside the series
(before 2020-04, after the last pinned 1 April) the base stays a case input
(B-RSA-MF-EURO, DSS_PENDING); the quarterly average arrives from fr.minima.ressources
(same lane, dependency); the received housing-aid figure arrives
established (APL-FORFAIT-PENDING).

Usage:
  python3 corpus/laws/fr/rsa/tools/build_sources.py --check
  python3 corpus/laws/fr/rsa/tools/build_sources.py --write
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "rsa"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"
COVERAGE_START = "2021-01-01"

NS = "urn:fr:corpus:clir:rsa"

SOURCES = {
    "CASF": {
        "registry": ROOT / ".scratch" / "reg-LEGITEXT000006074069.json",
        "mirror": ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006074069",
        "decl": "CASF",
        "kind": "code",
        "unit": "fr_code_lettered_article",
        "extra": "",
        "label_fr": "Code de l'action sociale et des familles",
        "label_en": "French Social Action and Families Code",
        "frag_prefix": "CASF_",
        "ed_prefix": "CASF",
        "txt_dir": "sources/casf",
        "ed_label_fr": ("Code de l'action sociale et des familles, "
                        "état en vigueur à compter du {st}"),
        "ed_label_en": ("French Social Action and Families Code: pinned "
                        "scope as in force from {st}"),
        "scope": ["L262-2", "L262-3", "L262-4", "L262-5", "L262-6",
                  "L262-9", "L262-27", "L262-28", "L262-29", "L262-30",
                  "L262-31", "L262-34", "L262-37", "L262-38", "L262-39",
                  "L262-20", "L262-45", "L262-46", "L262-47", "R262-1", "R262-2",
                  "R262-5", "R262-39", "R262-68", "R262-68-1", "R262-68-2",
                  "R262-68-3", "R262-68-4", "R262-68-5", "R262-68-6",
                  "R262-68-7", "R262-69", "R262-69-1", "R262-69-2",
                  "R262-69-3", "R262-69-4", "R262-69-5", "R262-69-6",
                  "R262-69-7", "R262-69-8", "R262-88", "R262-89",
                  "R262-90", "R262-92", "R262-92-1", "R262-93", "R262-94",
                  "R262-94-1", "D262-100", "D262-25-1", "D262-25-2",
                  "D262-25-3", "D262-25-4", "D262-26", "D262-27", "D262-28",
                  "D262-29", "D262-30", "D262-61", "D262-62", "D262-63",
                  "D262-64", "D262-65", "D262-65-2", "D262-65-2-1",
                  "D262-73", "D262-77", "D262-94-2", "D262-95", "D262-96",
                  "D262-97", "D262-98", "D262-99"],
    },
    "CODE_TRAVAIL": {
        "registry": ROOT / ".scratch" / "reg-LEGITEXT000006072050.json",
        "mirror": ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006072050",
        "decl": "CODE_TRAVAIL",
        "kind": "code",
        "unit": "fr_code_lettered_article",
        "extra": "",
        "label_fr": "Code du travail",
        "label_en": "French Labour Code",
        "frag_prefix": "CTRAV_",
        "ed_prefix": "CTRAV",
        "txt_dir": "sources/ctrav",
        "ed_label_fr": ("Code du travail, état en vigueur "
                        "à compter du {st}"),
        "ed_label_en": ("French Labour Code: pinned scope as in force "
                        "from {st}"),
        "scope": ["L5411-6"],
    },
    "DECRET_2025_478": {
        "registry": ROOT / ".scratch" / "reg-JORFTEXT000051672648.json",
        "mirror": ROOT / ".scratch" / "legi" / "mirror" / "JORFTEXT000051672648",
        "decl": "DECRET_2025_478",
        "kind": "decree",
        "unit": "fr_article",
        "extra": '\n    number "2025-478";',
        "label_fr": ("Décret n° 2025-478 du 30 mai 2025 relatif aux "
                     "sanctions applicables aux demandeurs d'emploi en cas "
                     "de manquement à leurs obligations"),
        "label_en": ("Decree No. 2025-478 of 30 May 2025 on sanctions for "
                     "jobseekers who breach their obligations"),
        "frag_prefix": "DEC2025_478_",
        "ed_prefix": "DEC2025_478",
        "txt_dir": "sources/jorf",
        "ed_label_fr": ("Décret n° 2025-478 du 30 mai 2025, article 12 "
                        "transitoire en vigueur à compter du {st}"),
        "ed_label_en": ("Decree No. 2025-478 of 30 May 2025: transitional "
                        "article 12 as in force from {st}"),
        "scope": ["12"],
    },
}

MF_DIR = PKG / "sources" / "decrets-mf"


def mf_decree_cfgs() -> dict:
    """One source config per pinned MF revaluation decree (article 1)."""
    manifest = json.loads((MF_DIR / "manifest.json").read_text(encoding="utf-8"))
    cfgs = {}
    for row in manifest["decrets"]:
        year, num = row["decret"].removeprefix("decret-").split("-")
        title = row["titre"]
        assert '"' not in title, title
        decl = f"DECRET_{year}_{num}"
        cfgs[decl] = {
            "mf_row": row,
            "retrieved_at": "@" + manifest["retrieved_at"] + "T00:00:00Z",
            "decl": decl, "kind": "decree", "unit": "fr_article",
            "extra": f'\n    number "{year}-{num}";',
            "label_fr": title,
            "label_en": (f"Decree No. {year}-{num} revaluing the RSA "
                         "flat-rate amount (article 1)"),
            "frag_prefix": f"DEC{year}_{num}_",
            "ed_prefix": f"DEC{year}_{num}",
            "txt_dir": "sources/jorf",
            "ed_label_fr": (f"Décret n° {year}-{num}, article 1er "
                            "(montant forfaitaire du RSA) en vigueur à compter "
                            "du {st}"),
            "ed_label_en": (f"Decree No. {year}-{num}: article 1 (RSA "
                            "flat-rate amount) as in force from {st}"),
            "scope": ["1"],
        }
    for row in manifest["lois"]:
        year, num = row["number"].split("-")
        title = row["titre"]
        assert '"' not in title, title
        decl = f"LOI_{year}_{num}"
        cfgs[decl] = {
            "mf_law_row": row,
            "retrieved_at": "@" + manifest["retrieved_at"] + "T00:00:00Z",
            "decl": decl, "kind": "statute", "unit": "fr_article",
            "extra": f'\n    number "{year}-{num}";',
            "label_fr": title,
            "label_en": (f"Act No. {year}-{num} of 16 August 2022 on emergency "
                         "measures to protect purchasing power (article 9: "
                         "revaluation of 1 July 2022)"),
            "frag_prefix": f"LOI_{year}_{num}_",
            "ed_prefix": f"LOI{year}_{num}",
            "txt_dir": "sources/jorf",
            "ed_label_fr": (f"Loi n° {year}-{num}, article 9 (coefficient 1,04 "
                            "de la revalorisation anticipée) applicable à "
                            "compter du {st}"),
            "ed_label_en": (f"Act No. {year}-{num}: article 9 (coefficient 1.04 "
                            "of the anticipated revaluation) applicable from {st}"),
            "scope": ["9"],
        }
    return cfgs


SOURCES.update(mf_decree_cfgs())

# Articles whose NOTA carries applicability and joins the fragment text.
# Finish-wave D articles add none: their current NOTAs restate the exact
# version debut (2022-1015 art. 18, 2024-606 art. 21, 2024-1269 art. 5) with
# no date gap and no transitional rule; predecessor NOTAs join automatically.
NOTA_IN_FRAGMENT = {"L262-27", "L262-29", "L262-30", "L262-31", "L262-34",
                    "L262-37", "L262-38", "L262-39", "L262-46", "R262-5",
                    "R262-92-1"}


def frag_base(cfg, num: str) -> str:
    if num.isdigit():
        return cfg["frag_prefix"] + "ART" + num
    return cfg["frag_prefix"] + num.replace("-", "_")


def tag_for(fin: str) -> str:
    tag = "PRE" + fin[:4]
    if fin[5:] != "01-01":
        tag += fin[5:7]
        if fin[8:] != "01":
            tag += fin[8:10]
    return tag


def xml_rel_for(legi_id: str) -> str:
    digits = legi_id.replace("LEGIARTI", "")
    pairs = [digits[i:i + 2] for i in range(0, 12, 2)][:5]
    return "dump/article/LEGI/ARTI/" + "/".join(pairs) + f"/{legi_id}.xml"


def find_xml(mirror: Path, legi_id: str) -> Path:
    p = mirror / xml_rel_for(legi_id)
    if p.exists():
        return p
    hits = sorted((mirror / "increments").rglob(legi_id + ".xml"))
    assert hits, f"version XML absent from mirror: {legi_id}"
    return hits[-1]


def old_xml_alineas(mirror: Path, legi_id: str):
    """Extract alineas from a mirror version XML (<br/> separated)."""
    p = find_xml(mirror, legi_id)
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
    return parts, nota, p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    assert args.check or args.write, "give --check or --write"

    versions = []  # one row per pinned version, all sources
    for skey, cfg in SOURCES.items():
        if "mf_row" in cfg:
            row = cfg["mf_row"]
            year, num = row["decret"].removeprefix("decret-").split("-")
            body = (PKG / row["text"]).read_text(encoding="utf-8").rstrip("\n")
            versions.append({
                "source": skey, "decl": cfg["decl"], "num": "1",
                "legi_id": row["legiarti"],
                "debut": row["start_month"] + "-01", "fin": "2999-01-01",
                "etat": row["etat"], "text": "Article 1\n" + body,
                "txt": f"{cfg['txt_dir']}/{year}-{num}-1.txt",
                "frag": frag_base(cfg, "1"), "nota": [],
                "nota_in_fragment": False,
                "xml_sha256": row["xml_sha256"], "xml_rel": row["dump_path"],
            })
            continue
        if "mf_law_row" in cfg:
            row = cfg["mf_law_row"]
            year, num = row["number"].split("-")
            body = (PKG / row["text"]).read_text(encoding="utf-8").rstrip("\n")
            assert body.startswith("Article 9\n"), "loi: first line must be the article heading"
            versions.append({
                "source": skey, "decl": cfg["decl"], "num": row["article"],
                "legi_id": row["legiarti"],
                "debut": row["start_date"], "fin": "2999-01-01",
                "etat": row["etat"], "text": body,
                "txt": f"{cfg['txt_dir']}/{year}-{num}-{row['article']}.txt",
                "frag": frag_base(cfg, row["article"]), "nota": [],
                "nota_in_fragment": False,
                "xml_sha256": row["xml_sha256"], "xml_rel": row["dump_path"],
            })
            continue
        mirror = cfg["mirror"]
        reg = json.loads(cfg["registry"].read_text(encoding="utf-8"))
        by_num = {a["num"]: a for a in reg["articles"]}
        missing = [n for n in cfg["scope"] if n not in by_num]
        assert not missing, f"{skey} scope absent from registry: {missing}"
        for num in cfg["scope"]:
            a = by_num[num]
            nota_lines = a.get("nota", [])
            title = ("Article " + num if not num.isdigit()
                     else "Article " + num)
            text = title + "\n" + "\n".join(a["alineas"])
            if num in NOTA_IN_FRAGMENT and nota_lines:
                text += "\n" + "\n".join("NOTA: " + n for n in nota_lines)
            versions.append({
                "source": skey, "decl": cfg["decl"], "num": num,
                "legi_id": a["id"], "debut": a["debut"], "fin": a["fin"],
                "etat": a["etat"], "text": text,
                "txt": f"{cfg['txt_dir']}/{num}.txt",
                "frag": frag_base(cfg, num),
                "nota": nota_lines,
                "nota_in_fragment": num in NOTA_IN_FRAGMENT,
                "xml_sha256": a.get("xml_sha256"),
                "xml_rel": a.get("xml_rel"),
            })
            for v in a.get("versions", []):
                if v["fin"] <= COVERAGE_START or v["id"] == a["id"]:
                    continue
                if v["fin"] <= v["debut"]:
                    continue  # stillborn MODIFIE_MORT_NE (D262-25-2
                              # LEGIARTI000043308998, debut 2023-01-01 past
                              # fin 2022-07-21): in force in no edition, so
                              # it would leave rows_by_version empty and
                              # crash the fragment emission below; the live
                              # version and the two real predecessors
                              # (PRE202104, PRE2023) still pin.
                if not v.get("etat"):
                    continue  # JORF original pseudo-record, not a version
                if v["id"].startswith("JORFARTI"):
                    continue  # JO original, not a LEGI version XML
                tag = tag_for(v["fin"])
                alineas, nota, p = old_xml_alineas(mirror, v["id"])
                text = title + "\n" + "\n".join(alineas)
                nota_lines = [nota] if nota else []
                if nota_lines:
                    text += "\n" + "\n".join("NOTA: " + n
                                            for n in nota_lines)
                versions.append({
                    "source": skey, "decl": cfg["decl"], "num": num,
                    "legi_id": v["id"], "debut": v["debut"], "fin": v["fin"],
                    "etat": "MODIFIE", "text": text,
                    "txt": f"{cfg['txt_dir']}/{num}-{tag}.txt",
                    "frag": frag_base(cfg, num) + "_" + tag,
                    "nota": nota_lines,
                    "nota_in_fragment": bool(nota_lines),
                    "xml_sha256": hashlib.sha256(
                        p.read_bytes()).hexdigest(),
                    "xml_rel": str(p.relative_to(mirror)),
                })

    outputs = {}
    header = (
        "// Provenance S1: revenu de solidarité active (CASF, livre II,\n"
        "// titre VI, chapitre II: droit et montant, droits et devoirs,\n"
        "// sanctions, recouvrement, jeunes travailleurs, instruction des\n"
        "// demandes, conventions, orientation, contrôle, statistiques),\n"
        "// contrat d'engagement du code du\n"
        "// travail (L. 5411-6) et article 12 transitoire du décret\n"
        "// n° 2025-478. Block generated by tools/build_sources.py from the\n"
        "// registries .scratch/reg-LEGITEXT000006074069.json (CASF),\n"
        "// .scratch/reg-LEGITEXT000006072050.json (code du travail) and\n"
        "// .scratch/reg-JORFTEXT000051672648.json (decree 2025-478), cut\n"
        "// 2026-10-06, plus superseded version XMLs from the mirror dumps.\n"
        "// The six decrees revaluing the montant forfaitaire (article 1 of\n"
        "// decrees 2020-490, 2021-530, 2022-699, 2023-340, 2024-396 and\n"
        "// 2025-293) come from sources/decrets-mf/ (tools/pin_mf_decrets.py;\n"
        "// LEGI dump of 2025-07-13, retrieved 2026-10-08), together with\n"
        "// article 9 of law 2022-1158 (coefficient 1.04 from 1 July 2022; the\n"
        "// edition opens at that date, the consolidated LEGI version is in\n"
        "// force from 2022-08-18; bytes shared with fr.css.revalorisation).\n"
        "// Do not edit by hand.\n"
        "//\n"
        "// Coverage D-01 from 2021-01-01. Editions run back to back from\n"
        "// the coverage start (decree: from its 2025-06-01 entry into\n"
        "// force); every pinned version gets a fragment in each edition\n"
        "// where it is in force.\n"
        "// Decree article 13 (ministers charged with execution) carries no\n"
        "// case content and is not pinned.\n"
        "// L. 542- / R. 542- adaptations for the outre-mer are wave 7\n"
        "// (SANS_OWNER): this package covers only the same-text metro/DOM\n"
        "// scope of the articles above.\n"
        "\n"
        'language "law.core" version "0.2";\n'
        'package fr.casf.rsa version "0.1.0";\n'
        f'namespace "{NS}";\n'
    )
    for skey, cfg in SOURCES.items():
        header += (
            "\n"
            f"source {cfg['decl']} {{\n"
            f"    kind {cfg['kind']};\n"
            "    jurisdiction FR;"
            f"{cfg['extra']}\n"
            f"    label fr official \"{cfg['label_fr']}\";\n"
            f"    label en unofficial \"{cfg['label_en']}\";\n"
            "}\n"
        )

    INF = "2999-01-01"

    def in_force(v_debut, v_fin, e_start):
        fin = None if v_fin in (None, "", INF) else v_fin
        return v_debut <= e_start and (fin is None or e_start < fin)

    frag_rows = []  # (edition, fname, version)
    ed_order = []  # edition declaration order
    for skey, cfg in SOURCES.items():
        svers = [v for v in versions if v["source"] == skey]
        starts = sorted({max(v["debut"], COVERAGE_START) for v in svers})
        editions = []
        for i, st in enumerate(starts):
            nxt = starts[i + 1] if i + 1 < len(starts) else None
            window = f"[@{st}, @{nxt})" if nxt else f"[@{st}, infinity)"
            editions.append((cfg["ed_prefix"] + ("" if len(starts) == 1
                                                 else "_ED" + st[:4] + "_"
                                                 + st[5:7]), st, window))
        for name, st, window in editions:
            ed_order.append((skey, cfg, name, st, window))
            header += (
                f"\n"
                f"edition {name} of {cfg['decl']} {{\n"
                f"    language fr;\n"
                f"    officiality official;\n"
                f"    materialization_status PINNED_UNOFFICIAL_COPY;\n"
                f"    in_force {window};\n"
                f"    label fr official \"{cfg['ed_label_fr'].format(st=st)}\";\n"
                f"    label en unofficial \"{cfg['ed_label_en'].format(st=st)}\";\n"
                f"}}\n"
            )
        ed_starts = [st for _, st, _ in editions]
        for v in svers:
            first = True
            for est in ed_starts:
                if in_force(v["debut"], v["fin"], est):
                    if first:
                        fname = v["frag"]
                        first = False
                    else:
                        fname = f"{v['frag']}_ED{est[:4]}_{est[5:7]}"
                        if len(starts) == 1:
                            fname = v["frag"]
                    frag_rows.append(
                        (cfg["ed_prefix"] + ("" if len(starts) == 1
                                             else "_ED" + est[:4] + "_"
                                             + est[5:7]), fname, v))

    pubs = ""
    frags = "\n// BEGIN GENERATED FR-CASF-RSA FRAGMENTS\n"
    accounting = []
    frag_map = {}
    ed_members = {}
    for ed, fname, v in frag_rows:
        ed_members.setdefault(ed, []).append((fname, v))
        frag_map.setdefault(v["frag"], []).append((ed, fname))
    for _, cfg, ed, _st, _window in ed_order:
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
            f"    retrieved_at {cfg.get('retrieved_at', RETRIEVED_AT)};\n"
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
            "source": v["source"],
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
    # D-43 source-map layout (FINISH-W4, CF pilot): map-relative edition
    # documents, explicit units and number-list scopes, current-document
    # selection. articles.json lives inside sources/, so edition documents
    # are "editions/<name>.txt" (the previous "sources/editions/..."
    # resolved to sources/sources/... and measured NO_SOURCE). Each edition
    # carries its source's unit and its exact member numbers (never the whole
    # scope: early editions hold no later norms). The map is heterogeneous:
    # CASF and Code du travail editions are lettered code articles
    # (fr_code_lettered_article; headings "Article L262-2", "Article L5411-6"),
    # the decree edition is a plain numbered article (fr_article; heading
    # "Article 12"). A single lettered-code unit must not cover the decree
    # publication, so the top level pins the main CASF act as
    # "scope"/"unit"/"document" and keeps source-specific scopes, units and
    # currents under "sources". Publication local_path values in
    # 01-sources.law stay package-relative ("sources/editions/...") for the
    # pinning gate; source bytes, fragment IDs, edition windows, provenance,
    # pinned_versions, fragments and articles accounting untouched.
    ed_nums = {}
    for _ed, _fname, _v in frag_rows:
        ed_nums.setdefault(_ed, set()).add(_v["num"])
    # Per-source current = last edition per source (back-to-back, open at cutoff).
    current_by_source = {}
    for _skey, _cfg, _ed, _st, _window in ed_order:
        current_by_source[_skey] = _ed
    casf_current = current_by_source["CASF"]
    # Per-edition scope in source SCOPE order (exact membership, no backdating).
    scope_order = {}
    for _skey, _cfg in SOURCES.items():
        for _i, _n in enumerate(_cfg["scope"]):
            scope_order[(_skey, _n)] = _i
    ed_entries = []
    for _skey, _cfg, _ed, _st, _window in ed_order:
        _members = ed_nums.get(_ed, set())
        _ordered = sorted(_members,
                          key=lambda n: scope_order.get((_skey, n), 10 ** 6))
        ed_entries.append({"edition": _ed,
                           "unit": _cfg["unit"],
                           "scope": _ordered,
                           "document": f"editions/{_ed}.txt"})
    sources_meta = {}
    for _skey, _cfg in SOURCES.items():
        _cur = current_by_source[_skey]
        sources_meta[_skey] = {"unit": _cfg["unit"],
                               "scope": list(_cfg["scope"]),
                               "document": f"editions/{_cur}.txt",
                               "current_edition": _cur}
    outputs["sources/articles.json"] = (
        json.dumps({"cutoff": "2026-10-06", "coverage_start": COVERAGE_START,
                    "scope": list(SOURCES["CASF"]["scope"]),
                    "unit": SOURCES["CASF"]["unit"],
                    "document": f"editions/{casf_current}.txt",
                    "sources": sources_meta,
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
            old = p.read_bytes() if p.exists() else None
            if old != blob:
                p.write_bytes(blob)
                print(f"write {rel} ({len(blob)} bytes)")
        print(f"versions={len(versions)} fragments={len(frag_rows)} "
              f"editions={len(ed_order)}")
        return
    bad = []
    for rel, blob in outputs.items():
        p = PKG / rel
        if not p.exists() or p.read_bytes() != blob:
            bad.append(rel)
    if bad:
        print("STALE: " + " ".join(bad))
        sys.exit(1)
    print(f"current: versions={len(versions)} fragments={len(frag_rows)} "
          f"editions={len(ed_order)}")


if __name__ == "__main__":
    main()
