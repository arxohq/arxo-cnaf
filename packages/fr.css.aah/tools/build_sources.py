#!/usr/bin/env python3
"""Pin the sources of package fr.css.aah (CNAF wave 4, lane fr-cnaf-aah).

Reads the CSS registry (.scratch/reg-css.json, cut 2026-10-06) and the two
decree registries (.scratch/reg-JORFTEXT000046830041.json for 2022-1694,
.scratch/reg-JORFTEXT000047541289.json for 2023-360) and builds:
  sources/css/<ARTICLE>.txt   - pinned text of the current version;
  sources/css/<ARTICLE>-<year>.txt - pinned superseded versions (double
                               calculation of the 2023-10-01 reform);
  sources/jorf/<DECRET>-art<N>.txt - pinned transitional/entry-into-force
                               articles of the two decrees;
  sources/articles.json        - accounting: versions, NOTA, coverage, gaps,
                               per-edition fragments; edition documents are
                               map-relative ("editions/<name>.txt"), top-level
                               "document" is the current CSS edition for the
                               program window (W4 depth layout, CF pilot D-43);
  sources/fragment-map.json    - version base fragment -> all edition fragments
                               (for @source authoring);
  01-sources.law               - sources CSS+JORF, editions back to back from
                               the coverage start, publications (one per
                               edition, all member texts verbatim), fragments
                               (one per pinned version per edition where that
                               version is in force, APL pattern: a rule fires
                               only when an @source fragment of its article
                               belongs to the edition open at legal_time).

Scope: 14 CSS articles (L821-1/2/3/3-1/4/5/8, D821-1/2/5, R821-4/4-1/4-2/4-5)
plus JORF articles 2-3 of decrees 2022-1694 and 2023-360. Superseded
versions pinned where a modelled norm changed in coverage:
  L821-3-PRE2023 (spouse income in the resources, 81 % couple plafond via
    old D821-2), D821-2-PRE2023, D821-5-PRE2023 (30 % couple majoration),
  L821-2-PRE2024, L821-1 x6 earlier wordings, R821-4 x5, R821-4-1 x2,
  R821-4-2 x1 earlier wording.
NOTA joins the fragment only where it carries applicability (L821-3,
D821-2, D821-5: entry into force 2023-10-01).

The monthly AAH euro amount chain (L. 821-3-1: set by decree, revalued on
1 April by the L. 161-25 coefficient) is pinned in sources/montant/ by
tools/pin_montant.py: decrees 2019-1047, 2020-492, 2021-527, 2022-700,
2023-328, 2024-397, 2025-297, 2026-229, the DSS coefficient paragraphs
(bytes of fr.css.revalorisation) and article 9 of act 2022-1158. This
generator appends their sources/editions/publications/fragments to
01-sources.law (block "amount chain"); tools/build_montant_chaine.py writes
07-montant-chaine.law from the same bytes. MVA/complement de ressources (L. 821-1-1 abrogated,
L. 821-1-2, D. 821-3/4), durations and revision (R. 821-5, R. 821-7,
L. 821-7-1), hospital reduction (R. 821-8), recovery (L. 821-5-1, D. 821-11,
D. 821-7), hosting rules (L. 821-6), management (L. 821-7) and the resource
computation mechanics (R. 532-3, D. 821-6/9/10, R. 821-4-3/4-4 details)
are declared gaps with reasons: resources arrive as retained case facts
(GOAL boundary: no DSN extraction).

Usage:
  python3 corpus/laws/fr/aah/tools/build_sources.py --check
  python3 corpus/laws/fr/aah/tools/build_sources.py --write
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "aah"
REGISTRY = ROOT / ".scratch" / "reg-css.json"
REG_2022_1694 = ROOT / ".scratch" / "reg-JORFTEXT000046830041.json"
REG_2023_360 = ROOT / ".scratch" / "reg-JORFTEXT000047541289.json"
MIRROR_CSS = ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006073189"
MIRROR_1694 = ROOT / ".scratch" / "legi" / "mirror" / "JORFTEXT000046830041"
MIRROR_3360 = ROOT / ".scratch" / "legi" / "mirror" / "JORFTEXT000047541289"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"
COVERAGE_START = "2021-01-01"

NS = "urn:fr:corpus:clir:aah"

SCOPE = ["L821-1", "L821-2", "L821-3", "L821-3-1", "L821-4", "L821-5",
         "L821-8", "D821-1", "D821-2", "D821-5", "R821-4", "R821-4-1",
         "R821-4-2", "R821-4-5"]

# (num, legi_id, debut, fin, txt, frag, mirror_dir, sub)
# mirror_dir selects the text mirror; sub selects dump vs a fixed increment.
OLD = [
    ("L821-1", "LEGIARTI000041398803", "2020-07-01", "2021-05-01",
     "sources/css/L821-1-2020.txt", "CSS_L821_1_PRE2021", "CSS", "dump"),
    ("L821-1", "LEGIARTI000042920125", "2021-05-01", "2023-09-01",
     "sources/css/L821-1-2021.txt", "CSS_L821_1_PRE2023", "CSS", "dump"),
    ("L821-1", "LEGIARTI000047453077", "2023-09-01", "2023-10-01",
     "sources/css/L821-1-2023-09.txt", "CSS_L821_1_PRE2023_10", "CSS",
     "increments"),
    ("L821-1", "LEGIARTI000047595374", "2023-10-01", "2024-12-01",
     "sources/css/L821-1-2023-10.txt", "CSS_L821_1_ED2023_10", "CSS",
     "increments"),
    ("L821-1", "LEGIARTI000048850214", "2024-12-01", "2026-01-01",
     "sources/css/L821-1-2024.txt", "CSS_L821_1_PRE2026", "CSS", "dump"),
    ("L821-1", "LEGIARTI000051289863", "2026-01-01", "2026-07-23",
     "sources/css/L821-1-2026-01.txt", "CSS_L821_1_PRE2026_07", "CSS",
     "increments"),
    ("L821-2", "LEGIARTI000020039305", "2008-12-29", "2024-12-01",
     "sources/css/L821-2-2008.txt", "CSS_L821_2_PRE2024", "CSS", "dump"),
    ("L821-3", "LEGIARTI000041412140", "2019-12-29", "2021-12-03",
     "sources/css/L821-3-2019.txt", "CSS_L821_3_PRE2021", "CSS", "dump"),
    ("L821-3", "LEGIARTI000044399288", "2021-12-03", "2022-01-01",
     "sources/css/L821-3-2021.txt", "CSS_L821_3_PRE2022", "CSS", "dump"),
    ("L821-3", "LEGIARTI000044979569", "2022-01-01", "2023-10-01",
     "sources/css/L821-3-2022.txt", "CSS_L821_3_PRE2023", "CSS", "dump"),
    ("D821-2", "LEGIARTI000039211076", "2019-10-14", "2023-10-01",
     "sources/css/D821-2-2019.txt", "CSS_D821_2_PRE2023", "CSS", "dump"),
    ("D821-5", "LEGIARTI000006739708", "2007-01-01", "2023-10-01",
     "sources/css/D821-5-2007.txt", "CSS_D821_5_PRE2023", "CSS", "dump"),
    ("R821-4", "LEGIARTI000023097776", "2010-11-17", "2022-01-21",
     "sources/css/R821-4-2010.txt", "CSS_R821_4_PRE2022", "CSS", "dump"),
    ("R821-4", "LEGIARTI000045048020", "2022-01-21", "2022-06-17",
     "sources/css/R821-4-2022-01.txt", "CSS_R821_4_PRE2022_06", "CSS",
     "dump"),
    ("R821-4", "LEGIARTI000045920113", "2022-06-17", "2023-01-01",
     "sources/css/R821-4-2022-06.txt", "CSS_R821_4_PRE2023", "CSS", "dump"),
    ("R821-4", "LEGIARTI000046833014", "2023-01-01", "2025-08-28",
     "sources/css/R821-4-2023.txt", "CSS_R821_4_PRE2025", "CSS", "dump"),
    ("R821-4", "LEGIARTI000052141008", "2025-08-28", "2026-06-28",
     "sources/css/R821-4-2025.txt", "CSS_R821_4_PRE2026", "CSS",
     "increments"),
    ("R821-4-1", "LEGIARTI000023097768", "2010-11-17", "2023-01-01",
     "sources/css/R821-4-1-2010.txt", "CSS_R821_4_1_PRE2023", "CSS", "dump"),
    ("R821-4-1", "LEGIARTI000046832999", "2023-01-01", "2026-06-28",
     "sources/css/R821-4-1-2023.txt", "CSS_R821_4_1_PRE2026", "CSS",
     "increments"),
    ("R821-4-2", "LEGIARTI000023097764", "2010-11-17", "2026-06-28",
     "sources/css/R821-4-2-2010.txt", "CSS_R821_4_2_PRE2026", "CSS", "dump"),
]

# JORF decree articles pinned (transitional rule + entries into force).
# (key, registry, num, mirror_dir)
JORF = [
    ("D1694-ART2", REG_2022_1694, "2", MIRROR_1694),
    ("D1694-ART3", REG_2022_1694, "3", MIRROR_1694),
    ("D3360-ART2", REG_2023_360, "2", MIRROR_3360),
    ("D3360-ART3", REG_2023_360, "3", MIRROR_3360),
]

NOTA_IN_FRAGMENT = {"L821-3", "D821-2", "D821-5"}

DECLARED_GAPS = {
    "L821-1-1-complement-ressources": (
        "abrogated guarantee/complement de ressources (L. 821-1-1 absent "
        "from the registry); historic euro figures in D. 821-3/4 unmodelled"),
    "L821-1-2-mva": (
        "majoration pour la vie autonome: needs housing-aid facts owned by "
        "fr.apl; not modelled, MVA euro figure (D. 821-3, 104,77) unapplied"),
    "L821-5-recovery": (
        "recovery and limitation (L. 821-5 al. 2-3, L. 821-5-1, D. 821-7, "
        "D. 821-11): wave 5 fr.prestations.versement"),
    "L821-6-hebergement": (
        "reduction for hosted/hospitalised/detained persons and the每日 "
        "forfait journalier minimum: period facts absent (B-AAH-HEBERGEMENT)"),
    "L821-7-gestion": "fund management: empirical bearer, no norm modelled",
    "R821-1-residence": (
        "residence detail (stays abroad, studies): permanent-residence and "
        "regular-stay arrive as case facts"),
    "R821-2-procedure": (
        "MDPH filing and fund liquidation procedure, silence-is-decision: "
        "the commission decision arrives as the established fact"),
    "R821-5-duree": (
        "award durations, revision, renewal procedure, advance on renewal "
        "(R. 821-5, R. 821-7, L. 821-7-1): duration facts absent"),
    "R821-8-hopital": (
        "60-day hospital reduction to 30 %: period facts absent"),
    "ressources-calcul": (
        "resource computation mechanics (R. 532-3 N-2, R. 821-4-3/4-4 "
        "events, D. 821-6/9/10 abatements, R. 821-4-II exclusions): "
        "resources arrive as retained case facts"),
    "montant-euro": (
        "monthly AAH euro amount: RESOLVED 08.10.2026 - decrees 2019-1047 "
        "... 2026-229, DSS coefficients and act 2022-1158 art. 9 pinned in "
        "sources/montant/ (chain in 07-montant-chaine.law); a case-supplied "
        "montant_mensuel_retenu still prevails; rounding of the product is "
        "the reading AahRevalorisationArrondiCentime (D-82)"),
}


def frag_name(num: str) -> str:
    return "CSS_" + num.replace("-", "_")


def ed_name(state: str) -> str:
    # Day precision: debuts 2022-01-01 and 2022-01-21 would otherwise share
    # CSS_ED2022_01 (duplicate edition blocks).
    return "CSS_ED" + state[:4] + "_" + state[5:7] + "_" + state[8:10]


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


def mirror_xml(mirror: Path, legi_id: str, sub: str) -> Path:
    n = legi_id.replace("LEGIARTI", "").replace("JORFARTI", "")
    if legi_id.startswith("JORFARTI"):
        rel = f"article/JORF/ARTI/{n}.xml"
    else:
        d = "/".join([n[0:2], n[2:4], n[4:6], n[6:8], n[8:10]])
        rel = f"article/LEGI/ARTI/{d}/{legi_id}.xml"
    if sub == "dump":
        p = mirror / "dump" / rel
    else:
        cands = sorted((mirror / "increments").rglob(legi_id + ".xml"))
        assert cands, f"no increment XML for {legi_id}"
        p = cands[0]
    return p


MONTANT_DIR = PKG / "sources" / "montant"
EDITION_OPEN = "[@" + COVERAGE_START + ", infinity)"


def montant_blocks() -> list[str]:
    """Sources, editions, publications and fragments of the amount chain (sources/montant/)."""
    manifest = json.loads((MONTANT_DIR / "manifest.json").read_text(encoding="utf-8"))
    out = ["// ---- amount chain (sources/montant/, tools/pin_montant.py) ----", ""]
    declared = set()

    def block(src, src_kind, src_number, label_fr, label_en, edition, ed_label_fr, ed_label_en, in_force,
              row, uri, retrieved, fragment, frag_kind, locator):
        text = (PKG / row["text"]).read_text(encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if src not in declared:
            declared.add(src)
            out.extend([f"source {src} {{", f"    kind {src_kind};", "    jurisdiction FR;"]
                       + ([f'    number "{src_number}";'] if src_number else [])
                       + [f'    label fr official "{label_fr}";', f'    label en unofficial "{label_en}";', "}", ""])
        out.extend([
            f"edition {edition} of {src} {{", "    language fr;", "    officiality official;",
            "    materialization_status PINNED_UNOFFICIAL_COPY;", f"    in_force {in_force};",
            f'    label fr official "{ed_label_fr}";', f'    label en unofficial "{ed_label_en}";', "}", "",
            f"publication {edition}_TEXT of {edition} {{", '    media_type "text/plain; charset=utf-8";',
            f'    uri "{uri}";', f"    retrieved_at {retrieved};", f'    content_hash "sha256:{digest}";',
            f'    local_path "{row["text"]}";', "}", "",
            f'@id("{NS}#{fragment}")', f"pub fragment {fragment} in {edition} {{", f"    kind {frag_kind};",
            f'    locator "{locator}";', f'    text fr official """{text}""";', f'    content_hash "sha256:{digest}";',
            "}", ""])

    for row in manifest["texts"]:
        retrieved = "@" + manifest["retrieved_at"] + "T00:00:00Z"
        if row["kind"] == "decree":
            number = row["numero"]
            under = number.replace("-", "_")
            fragment = f"DEC{under}_ART{row['article']}"
            assert '"' not in row["titre"], row["titre"]
            block(f"DECRET_{under}", "decree", number, row["titre"],
                  f"Decree No. {number} on the revaluation of the adult disability allowance (amount chain)",
                  fragment + "_ED",
                  f"Décret n° {number}, article {row['article']} (montant de l'AAH) en vigueur à compter du {COVERAGE_START}",
                  f"Decree No. {number}: article {row['article']} (AAH amount) as in force from {COVERAGE_START}",
                  EDITION_OPEN, row,
                  manifest["dump"] if row["origin_kind"] == "dump" else
                  "https://echanges.dila.gouv.fr/OPENDATA/JORF/" + row["origin_kind"] + ".tar.gz",
                  retrieved, fragment, "article", f"article/{row['article']}")
        elif row["kind"] == "guidance":
            fragment = row["origin_fragment"].split("::")[1]
            src = row["source"]
            code = re.search(r"n° (DSS/[\w/]+) du", row["label_fr"]).group(1)
            block(src, "regulation", None, row["label_fr"], row["label_en"], fragment + "_ED",
                  f"{code} : paragraphe du coefficient L. 161-25 au 1er avril (octets de fr.css.revalorisation)",
                  f"{code}: L. 161-25 coefficient paragraph for 1 April (bytes of fr.css.revalorisation)",
                  EDITION_OPEN, row, row["uri"], row["retrieved_at"], fragment, "guidance", row["locator"])
        else:
            block("LOI_2022_1158", "statute", "2022-1158",
                  "Loi n° 2022-1158 du 16 août 2022 portant mesures d\u2019urgence pour la protection du pouvoir d\u2019achat",
                  "Act No. 2022-1158 of 16 August 2022 on emergency measures to protect purchasing power "
                  "(article 9: revaluation of 1 July 2022)",
                  "LOI_2022_1158_ART9_ED2022",
                  "Loi n° 2022-1158, article 9 : revalorisation anticipée au 1er juillet 2022 "
                  f"(miroir DILA LEGI, {row['legiarti']}, version en vigueur depuis le {row['version_debut']})",
                  "Act No. 2022-1158, article 9: anticipated revalorisation of 1 July 2022 "
                  f"(DILA LEGI mirror, {row['legiarti']}, version in force from {row['version_debut']})",
                  "[@2022-07-01, infinity)", row, manifest["dump"], retrieved, "LOI_2022_1158_ART9", "article",
                  "article/9")
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

    versions = []  # (num, legi_id, debut, fin, text, txt, frag, ...)
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
            "versions": [
                {"id": v["id"], "debut": v["debut"], "fin": v["fin"],
                 "etat": v["etat"]} for v in a.get("versions", [])],
            "xml_sha256": a.get("xml_sha256"),
            "xml_rel": a.get("xml_rel"),
        })
    for (num, legi_id, debut, fin, txt, frag, which, sub) in OLD:
        mirror = MIRROR_CSS if which == "CSS" else None
        p = mirror_xml(mirror, legi_id, sub)
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

    jorf_articles = []
    for (key, regpath, num, mirror) in JORF:
        jreg = json.loads(regpath.read_text(encoding="utf-8"))
        arts = {a["num"]: a for a in jreg["articles"]}
        assert num in arts, f"{num} absent from {regpath.name}"
        a = arts[num]
        # Resolve the version XML inside the decree mirror.
        cands = list(mirror.rglob(a["id"] + ".xml"))
        assert cands, f"no XML for {a['id']} under {mirror}"
        alineas, nota = xml_alineas(cands[0])
        text = f"Article {num}\n" + "\n".join(alineas)
        jorf_articles.append({
            "key": key, "num": num, "legi_id": a["id"],
            "debut": a["debut"], "fin": a["fin"], "text": text,
            "txt": f"sources/jorf/{key}.txt",
            "frag": "JORF_" + key.replace("-", "_"),
            "xml_sha256": hashlib.sha256(cands[0].read_bytes()).hexdigest(),
            "xml_rel": str(cands[0].relative_to(ROOT)),
        })

    debuts = sorted({COVERAGE_START} | {v["debut"] for v in versions
                                          if v["debut"] >= COVERAGE_START})
    outputs = {}

    header = (
        "// Provenance S1: disabled-adults allowance (CSS, livre VIII,\n"
        "// titre II: L. 821-1..8, R. 821-1..9, D. 821-1..11 in ownership;\n"
        "// modelled: L. 821-1/2 (tracks), L. 821-3/3-1 + D. 821-2 (amount),\n"
        "// L. 821-4 (CDAPH channel), L. 821-5 (recovery ref, unmodelled),\n"
        "// L. 821-8 (application decrees), D. 821-1 (80/50 %), D. 821-5\n"
        "// (ESAT cap), R. 821-4/4-1/4-2 (resource regimes), R. 821-4-5\n"
        "// (recipient duties); JORF: decree 2022-1694 arts 2-3 (double\n"
        "// calculation, irreversible switch) and decree 2023-360 arts 2-3\n"
        "// (entry into force 2023-10-01). Block generated by\n"
        "// tools/build_sources.py from the registries .scratch/reg-css.json,\n"
        "// .scratch/reg-JORFTEXT000046830041.json and\n"
        "// .scratch/reg-JORFTEXT000047541289.json (cut 2026-10-06; alineas\n"
        "// and versions from the DILA LEGI mirror). Do not edit by hand.\n"
        "//\n"
        "// Coverage D-01 from 2021-01-01. Editions run back to back from\n"
        "// the coverage start through every pinned debut. The 2023-10-01\n"
        "// reform (loi 2022-1158 art. 10, decrees 2022-1694/2023-360)\n"
        "// splits L. 821-3, D. 821-2 and D. 821-5 into PRE2023/current\n"
        "// wordings; decree 2026-547 splits R. 821-4/4-1/4-2 from\n"
        "// 2026-06-28. NOTA joins the fragment only where it carries\n"
        "// applicability (L821-3, D821-2, D821-5); see sources/articles.json.\n"
        "// The monthly euro amount chain (L. 821-3-1, L. 161-25) comes from\n"
        "// sources/montant/ (tools/pin_montant.py): block \"amount chain\" at the\n"
        "// end of this file (decrees, DSS coefficient paragraphs, act 2022-1158).\n"
    )

    # Edition texts: all member fragment texts verbatim per edition.
    for i, debut in enumerate(debuts):
        fin = debuts[i + 1] if i + 1 < len(debuts) else None
        members = [v for v in versions
                   if v["debut"] <= debut and (v["fin"] is None or
                                               debut < v["fin"] or
                                               v["fin"] == "2999-01-01")]
        ed = ed_name(debut)
        lines = [f"Edition {ed} [{debut}, {fin or 'infinity'}):"]
        for v in members:
            lines.append(f"--- {v['frag']} ({v['num']} {v['legi_id']}) ---")
            lines.append(v["text"])
        outputs[f"sources/editions/{ed}.txt"] = "\n".join(lines) + "\n"

    # 01-sources.law: sources, editions, publications, fragments.
    law = [header, "",
           'language "law.core" version "0.2";',
           'package fr.css.aah version "0.1.0";',
           'namespace "urn:fr:corpus:clir:aah";', "",
           "source CSS {", "    kind code;", "    jurisdiction FR;",
           '    label fr official "Code de la sécurité sociale";',
           '    label en unofficial "French Social Security Code";', "}",
           "",
           "source JORF {", "    kind official_journal;",
           "    jurisdiction FR;",
           '    label fr official "Journal officiel de la République française";',
           '    label en unofficial "Official Journal of the French Republic";',
           "}", ""]
    pub_hashes = {}
    for i, debut in enumerate(debuts):
        fin = debuts[i + 1] if i + 1 < len(debuts) else None
        window = f"[@{debut}, {'@' + fin if fin else 'infinity'})"
        ed = ed_name(debut)
        law.append(f"edition {ed} of CSS {{")
        law.append("    language fr;")
        law.append("    officiality official;")
        law.append("    materialization_status PINNED_UNOFFICIAL_COPY;")
        law.append(f"    in_force {window};")
        law.append(f'    label fr official "Code de la sécurité sociale, état en vigueur à compter du {debut}";')
        law.append(f'    label en unofficial "French Social Security Code: pinned scope as in force from {debut}";')
        law.append("}")
        law.append("")
        rel = f"sources/editions/{ed}.txt"
        h = hashlib.sha256(outputs[rel].encode("utf-8")).hexdigest()
        pub_hashes[rel] = h
        law.append(f"publication {ed}_TEXT of {ed} {{")
        law.append('    media_type "text/plain; charset=utf-8";')
        law.append(f'    uri "{DUMP_URL}";')
        law.append(f"    retrieved_at {RETRIEVED_AT};")
        law.append(f'    content_hash "sha256:{h}";')
        law.append(f'    local_path "{rel}";')
        law.append("}")
        law.append("")
    # JORF editions/publications (one-shot: single edition each).
    for j in jorf_articles:
        ed = "JORF_" + j["key"].replace("-", "_") + "_ED"
        rel = j["txt"]
        # edition text file content
        etxt = (f"Edition {ed} [{j['debut']}, infinity):\n"
                f"--- {j['frag']} (decree article {j['num']} "
                f"{j['legi_id']}) ---\n{j['text']}\n")
        outputs[rel] = etxt
        h = hashlib.sha256(etxt.encode("utf-8")).hexdigest()
        law.append(f"edition {ed} of JORF {{")
        law.append("    language fr;")
        law.append("    officiality official;")
        law.append("    materialization_status PINNED_UNOFFICIAL_COPY;")
        law.append(f"    in_force [@{j['debut']}, infinity);")
        law.append(f'    label fr official "Journal officiel, décret applicable à compter du {j["debut"]}";')
        law.append(f'    label en unofficial "Official Journal, decree applicable from {j["debut"]}";')
        law.append("}")
        law.append("")
        law.append(f"publication {ed}_TEXT of {ed} {{")
        law.append('    media_type "text/plain; charset=utf-8";')
        law.append(f'    uri "{DUMP_URL}";')
        law.append(f"    retrieved_at {RETRIEVED_AT};")
        law.append(f'    content_hash "sha256:{h}";')
        law.append(f'    local_path "{rel}";')
        law.append("}")
        law.append("")
    fragmap = {}
    for v in versions:
        eds = [ed_name(d) for d in debuts
               if v["debut"] <= d and (d < v["fin"] or
                                       v["fin"] == "2999-01-01")]
        fragmap[v["frag"]] = [f + "_" + e.replace("CSS_", "")
                              for f, e in [(v["frag"], x) for x in eds]]
        for e in eds:
            fname = f"{v['frag']}_{e.replace('CSS_', '')}"
            fhash = hashlib.sha256((v["text"] + "\n").encode("utf-8")).hexdigest()
            law.append(f'@id("{NS}#{fname}")')
            law.append(f"pub fragment {fname} in {e} {{")
            law.append("    kind article;")
            law.append(f'    locator "article/{v["num"]}";')
            law.append(f'    text fr official """{v["text"]}\n""";')
            law.append(f'    content_hash "sha256:{fhash}";')
            law.append("}")
            law.append("")
        outputs[v["txt"]] = v["text"] + "\n"
    for j in jorf_articles:
        ed = "JORF_" + j["key"].replace("-", "_") + "_ED"
        jhash = hashlib.sha256((j["text"] + "\n").encode("utf-8")).hexdigest()
        law.append(f'@id("{NS}#{j["frag"]}")')
        law.append(f"pub fragment {j['frag']} in {ed} {{")
        law.append("    kind article;")
        law.append(f'    locator "article/{j["num"]}";')
        law.append(f'    text fr official """{j["text"]}\n""";')
        law.append(f'    content_hash "sha256:{jhash}";')
        law.append("}")
        law.append("")
    law.extend(montant_blocks())
    outputs["01-sources.law"] = "\n".join(law)

    # Per-edition member scope for the depth map: the same membership
    # predicate as the edition documents built above (a version belongs to
    # the editions whose start it covers). Early editions list only the
    # versions in force at their start; coverage is not backdated.
    ed_scope = {}
    for _d in debuts:
        ed_scope[ed_name(_d)] = sorted({v["num"] for v in versions
                                        if v["debut"] <= _d and (v["fin"] is None or
                                                                 _d < v["fin"] or
                                                                 v["fin"] == "2999-01-01")})
    current_edition = ed_name(debuts[-1])

    articles_doc = {
        "$comment": ("Source scope of package fr/css/aah (wave 4, CNAF-AAH): "
                     "14 CSS articles + 4 JORF decree articles, registry cut "
                     "2026-10-06. Superseded versions pinned where a modelled "
                     "norm changed in coverage (2023-10-01 reform, 2024-12-01 "
                     "L821-2, 2026-547 R821-4 split). Monthly euro amount and "
                     "The amount chain (decrees, DSS coefficients, act 2022-1158 art. 9) "
                     "is pinned separately in sources/montant/."),
        "coverage_start": COVERAGE_START,
        "dump": {"registry": ".scratch/reg-css.json",
                 "registry_cutoff": "2026-10-06",
                 "retrieved_at": "2026-10-06T00:00:00Z",
                 "url": DUMP_URL},
        "jorf_registries": [".scratch/reg-JORFTEXT000046830041.json",
                            ".scratch/reg-JORFTEXT000047541289.json"],
        "scope_articles": SCOPE,
        # Depth-measure addressing (FINISH-W4 layout, CF pilot D-43):
        # "scope" (== scope_articles for the CSS act) and "unit" mirror the
        # CF map shape; "document" pins the current CSS edition for the
        # program window (coverage from 2021-01-01, cutoff 2026-10-06).
        # Edition documents are map-relative ("editions/<name>.txt"):
        # articles.json lives inside sources/, so the previous
        # "sources/editions/..." resolved to sources/sources/... (NO_SOURCE).
        # The four JORF decree articles stay out of the CSS scope: they are
        # separate one-shot JORF editions/publications (transitional and
        # entry-into-force rules), not lettered code articles. Publication
        # local_path values stay package-relative for the pinning gate;
        # source bytes, fragment IDs, edition windows and provenance
        # untouched, as are "scope_articles", "pinned", "pinned_jorf" and
        # "declared_gaps".
        "scope": SCOPE,
        "unit": "fr_code_lettered_article",
        "document": f"editions/{current_edition}.txt",
        "pinned": versions,
        "pinned_jorf": jorf_articles,
        "editions": [{"edition": ed_name(d),
                      "unit": "fr_code_lettered_article",
                      "scope": ed_scope[ed_name(d)],
                      "document": f"editions/{ed_name(d)}.txt"}
                     for d in debuts],
        "declared_gaps": DECLARED_GAPS,
    }
    outputs["sources/articles.json"] = (json.dumps(articles_doc,
                                                   ensure_ascii=False,
                                                   indent=2) + "\n")
    outputs["sources/fragment-map.json"] = (json.dumps(fragmap,
                                                       ensure_ascii=False,
                                                       indent=2) + "\n")
    manifest = {
        "$comment": ("Source scope of package fr/css/aah (wave 4, CNAF-AAH): "
                     "14 CSS articles + 4 JORF decree articles, registry cut "
                     "2026-10-06. Bytes: alineas of the registries (DILA LEGI "
                     "mirror); old wordings from mirror dump/increments. "
                     "The monthly amount chain (decrees, DSS coefficients, act "
                     "2022-1158 art. 9) is pinned in sources/montant/ "
                     "(tools/pin_montant.py)."),
        "coverage_start": COVERAGE_START,
        "dump": {"registry": ".scratch/reg-css.json",
                 "registry_cutoff": "2026-10-06",
                 "retrieved_at": "2026-10-06T00:00:00Z",
                 "url": DUMP_URL},
        "scope_articles": len(SCOPE),
        "articles": SCOPE,
        "pinned_old_versions": {o[5]: {"num": o[0], "legi_id": o[1],
                                       "debut": o[2], "fin": o[3]}
                                for o in OLD},
        "pinned_jorf": [j["key"] for j in jorf_articles],
        "declared_gaps": DECLARED_GAPS,
    }
    outputs["sources/source-manifest.json"] = (json.dumps(manifest,
                                                          ensure_ascii=False,
                                                          indent=2) + "\n")

    if args.write:
        for rel, doc in outputs.items():
            p = PKG / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(doc, encoding="utf-8")
        print(f"WROTE {len(outputs)} files, {len(debuts)} editions, "
              f"{len(versions)} CSS versions, {len(jorf_articles)} JORF")
        return 0
    errors = []
    for rel, doc in outputs.items():
        p = PKG / rel
        if not p.exists():
            errors.append(f"missing {rel}")
        elif p.read_text(encoding="utf-8") != doc:
            errors.append(f"drift {rel}")
    print(f"editions: {len(debuts)}, css versions: {len(versions)}, "
          f"jorf: {len(jorf_articles)}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print("  " + e)
        return 1
    print("SOURCES OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
