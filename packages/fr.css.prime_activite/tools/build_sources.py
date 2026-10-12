#!/usr/bin/env python3
"""Pin the sources of package fr.css.prime_activite (CNAF wave 4, W4-PPA).

Reads the CSS registry (.scratch/reg-css.json, cut 2026-10-06) and builds:
  sources/css/<ARTICLE>.txt   - pinned text of the current version;
  sources/css/<ARTICLE>-<year>.txt - pinned superseded versions (modelled
                               norms that changed in coverage);
  sources/articles.json        - accounting: versions, NOTA, coverage, gaps,
                               per-edition fragments;
  sources/fragment-map.json    - version base fragment -> all edition fragments
                               (for @source authoring);
  01-sources.law               - sources CSS, editions back to back from
                               the coverage start, publications (one per
                               edition, all member texts verbatim), fragments
                               (one per pinned version per edition where that
                               version is in force, APL pattern: a rule fires
                               only when an @source fragment of its article
                               belongs to the edition open at legal_time).

Scope: 68 CSS articles (L841-1, L842-1/2/3/4/5/7/8, L843-1..6, L844-1,
L845-1..6, L846-1..3, D843-1/2/3/4, R843-1; FINISH pa: D846-1/2/3,
D847-1/2/3, D848-1..5, R842-1..5, R843-2, R844-1/2/3/4/5, R845-1/2/3,
R846-1..9, R847-1/1-1/2/3, R848-1). Superseded versions pinned where a
modelled norm changed in coverage:
  D843-2-PRE2026 (bonification 120x SMIC / 29.101 %, decree 2026-222 art. 1
    raises to 138x / 37.7 % from 2026-04-01),
  D843-3-PRE2025 (fraction 61 %, decree 2025-292 art. 1 lowers to 59.85 %
    from 2025-03-31),
  R843-1-PRE2025 (trimestre M-3..M-1, decree 2025-185 art. 6 shifts to
    M-4..M-2 for demands/reviews from 2025-03-01),
  L845-3-PRE2024 (recovery wording before the 2024-01-01 reform),
  L846-2-PRE2025 (statistics wording 2016-2025; unmodelled, pinned for
    full-scope editions),
  R842-2-PRE2025 (timing each-month-of-quarter + month of right except
    1°/3°/5°, decree 2025-185 art. 2 sets per-condition M-4..M-2 timing
    from 2025-02-28),
  R843-2-PRE2025 (revision on L842-7 only, decree 2025-185 art. 2 adds
    couple separation from 2025-02-28),
  R845-1-PRE2025 / R845-2-PRE2025 (fallback on the preceding quarter's
    receipts, decree 2025-185 art. 2 sets M-4..M-2 from 2025-02-28),
  D848-4-PRE2024 (Pôle emploi publisher, decree 2024-606 art. 19 sets
    France Travail from 2024-07-01),
  R844-3-PRE2024 (housing in-kind forfait without the opening reserve for
    professional-income benefits in kind, decree 2023-1378 art. 4 II),
  R844-1-W2020 (list without section II), R844-1-W2023 (list + section II,
    5° without the birth leave),
  R844-5-W2020 (items 1-28, short 18°, old 21°),
  R844-5-W2021 (adds 29°), R844-5-W2022 (new 21° + 21°bis).
NOTA joins the fragment where it carries applicability (D843-2, D843-3,
R843-1: entry-into-force notes of decrees 2026-222, 2025-292, 2025-185;
R842-2, R843-2, R845-1, R845-2: decree 2025-185 demands/reviews from
2025-03-01, MSA arrêté date; R844-1: birth indemnities from 2026-07-01;
R844-5: resources from 2024-01-01, declared from 2024-02-01; R847-1-1:
indus notified from entry into force).

The single-person euro forfait (L. 842-3: set by decree, revalued on 1 April by
the L. 161-25 coefficient) is pinned in sources/montant/ by
tools/pin_forfait.py: decrees 2020-491, 2021-528, 2022-701, 2023-343,
2024-403, 2025-294, 2026-222 (arts 2-3), the DSS coefficient paragraphs
(bytes of fr.css.revalorisation) and article 9 of act 2022-1158. This
generator appends their sources/editions/publications/fragments to
01-sources.law (block "amount chain"); tools/build_forfait_chaine.py writes
11-forfait-chaine.law from the same bytes. The BMAF euros, the CGI
abatement rates and ceilings, the L. 241-3 ceiling and the DSN-extracted
resource totals are NOT pinned: they arrive as retained case inputs
(B-PPA-RESSOURCES-CALCUL). The SMIC hourly rate arrives as a retained
monthly fact (B-PPA-SMIC-MOIS: a rule cannot evaluate fr.travail.smic at a
reference month other than the legal time of the case); resource totals
arrive as retained case facts (GOAL boundary: no DSN extraction);
R844/R845 classifications are derived from itemized retained facts
(convergence with the retained totals deferred).
R842-1..5 condition timing is modelled from monthly retained facts
(B-PPA-CONDITION-TIMING resolved in structure; monthly-fact convergence
with 02-droit deferred: B-PPA-CONDITIONS-MENSUELLES).

Usage:
  python3 corpus/laws/fr/prime-activite/tools/build_sources.py --check
  python3 corpus/laws/fr/prime-activite/tools/build_sources.py --write
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "prime-activite"
REGISTRY = ROOT / ".scratch" / "reg-css.json"
MIRROR_CSS = ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006073189"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"
COVERAGE_START = "2021-01-01"

NS = "urn:fr:corpus:clir:ppa"

SCOPE = ["L841-1", "L842-1", "L842-2", "L842-3", "L842-4", "L842-5",
         "L842-7", "L842-8", "L843-1", "L843-2", "L843-3", "L843-4",
         "L843-5", "L843-6", "L844-1", "L845-1", "L845-2", "L845-3",
         "L845-4", "L845-5", "L845-6", "L846-1", "L846-2", "L846-3",
         "D843-1", "D843-2", "D843-3", "D843-4", "R843-1",
         "D846-1", "D846-2", "D846-3",
         "D847-1", "D847-2", "D847-3",
         "D848-1", "D848-2", "D848-3", "D848-4", "D848-5",
         "R842-1", "R842-2", "R842-3", "R842-4", "R842-5",
         "R843-2",
         "R844-1", "R844-2", "R844-3", "R844-4", "R844-5",
         "R845-1", "R845-2", "R845-3",
         "R846-1", "R846-2", "R846-3", "R846-4", "R846-5",
         "R846-6", "R846-7", "R846-8", "R846-9",
         "R847-1", "R847-1-1", "R847-2", "R847-3",
         "R848-1"]

# (num, legi_id, debut, fin, txt, frag, mirror_dir, sub)
# mirror_dir selects the text mirror; sub selects dump vs a fixed increment.
# Windows below are the registry DATE_DEBUT/DATE_FIN of each superseded
# version (cut 2026-10-06); all predate the July-2025 dump, hence "dump".
OLD = [
    ("D843-2", "LEGIARTI000037873473", "2018-10-01", "2026-04-01",
     "sources/css/D843-2-2018.txt", "CSS_D843_2_PRE2026", "CSS", "dump"),
    ("D843-3", "LEGIARTI000037462909", "2018-10-05", "2025-03-31",
     "sources/css/D843-3-2018.txt", "CSS_D843_3_PRE2025", "CSS", "dump"),
    ("R843-1", "LEGIARTI000031694309", "2016-01-01", "2025-02-28",
     "sources/css/R843-1-2016.txt", "CSS_R843_1_PRE2025", "CSS", "dump"),
    ("L845-3", "LEGIARTI000041398429", "2020-01-01", "2024-01-01",
     "sources/css/L845-3-2020.txt", "CSS_L845_3_PRE2024", "CSS", "dump"),
    ("L846-2", "LEGIARTI000031077508", "2016-01-01", "2025-01-01",
     "sources/css/L846-2-2016.txt", "CSS_L846_2_PRE2025", "CSS", "dump"),
    ("R842-2", "LEGIARTI000031694328", "2016-01-01", "2025-02-28",
     "sources/css/R842-2-2016.txt", "CSS_R842_2_PRE2025", "CSS", "dump"),
    ("R843-2", "LEGIARTI000033969687", "2017-01-01", "2025-02-28",
     "sources/css/R843-2-2017.txt", "CSS_R843_2_PRE2025", "CSS", "dump"),
    ("R845-1", "LEGIARTI000034624202", "2017-07-01", "2025-02-28",
     "sources/css/R845-1-2017.txt", "CSS_R845_1_PRE2025", "CSS", "dump"),
    ("R845-2", "LEGIARTI000041727755", "2020-03-16", "2025-02-28",
     "sources/css/R845-2-2020.txt", "CSS_R845_2_PRE2025", "CSS", "dump"),
    ("D848-4", "LEGIARTI000031674634", "2016-01-01", "2024-07-01",
     "sources/css/D848-4-2016.txt", "CSS_D848_4_PRE2024", "CSS", "dump"),
    ("R844-3", "LEGIARTI000031675988", "2016-01-01", "2023-12-31",
     "sources/css/R844-3-2016.txt", "CSS_R844_3_PRE2024", "CSS", "dump"),
    ("R844-1", "LEGIARTI000042497177", "2020-11-06", "2023-12-31",
     "sources/css/R844-1-2020.txt", "CSS_R844_1_W2020", "CSS", "dump"),
    ("R844-1", "LEGIARTI000048841691", "2023-12-31", "2026-06-27",
     "sources/css/R844-1-2023.txt", "CSS_R844_1_W2023", "CSS", "dump"),
    ("R844-5", "LEGIARTI000042497129", "2020-11-06", "2021-03-25",
     "sources/css/R844-5-2020.txt", "CSS_R844_5_W2020", "CSS", "dump"),
    ("R844-5", "LEGIARTI000043281969", "2021-03-25", "2022-03-21",
     "sources/css/R844-5-2021.txt", "CSS_R844_5_W2021", "CSS", "dump"),
    ("R844-5", "LEGIARTI000045386120", "2022-03-21", "2023-12-31",
     "sources/css/R844-5-2022.txt", "CSS_R844_5_W2022", "CSS", "dump"),
]

NOTA_IN_FRAGMENT = {"D843-2", "D843-3", "R843-1",
                      "R842-2", "R843-2", "R845-1", "R845-2",
                      "R844-1", "R844-3", "R844-5", "R847-1-1"}

# CNAF instruction IT-2026-080 (inbox 2026-10-06): exceptional April-2026
# revalorisation of the PPA bonification (decree 2026-222). Pinned as
# official PDF bytes plus extracted layout text; fragments slice exact .txt
# line ranges (1-based, inclusive): bonification amounts, scale edges in
# euros, and the 1.5-SMIC exit point.
IT_URL = ("https://www.caf.fr/sites/default/files/medias/cnaf/Nous_connaitre/"
          "qui%20sommes%20nous/Textes%20de%20r%C3%A9f%C3%A9rence/Circulaires/"
          "2026/IT-%202026-080.pdf")
IT_PDF = "sources/cnaf-it-2026-080.pdf"
IT_TXT = "sources/cnaf-it-2026-080.txt"
IT_FRAGS = [
    ("CNAF_IT_2026_080_MONTANTS", "guidance",
     "instruction-technique/IT-2026-080/I/montant-bonification", 71, 77),
    ("CNAF_IT_2026_080_BORNES", "table",
     "instruction-technique/IT-2026-080/I/bornes-euros", 96, 110),
    ("CNAF_IT_2026_080_SORTIE", "guidance",
     "instruction-technique/IT-2026-080/I/point-sortie", 115, 117),
]


def it_block() -> str:
    pdf = (PKG / IT_PDF).read_bytes()
    txt = (PKG / IT_TXT).read_bytes()
    lines = txt.decode("utf-8").split("\n")
    pdf_h = "sha256:" + hashlib.sha256(pdf).hexdigest()
    txt_h = "sha256:" + hashlib.sha256(txt).hexdigest()
    b = ["\n// BEGIN GENERATED FR-PPA CNAF DOCUMENTS\n"]
    b.append("source CNAF_IT_2026_080 {\n"
             "    kind guidance;\n"
             "    jurisdiction FR;\n"
             '    label fr official "Instruction technique CNAF n° IT-2026-080 du 2 avril 2026 : modification du calcul de la bonification en Prime d’activité";\n'
             '    label en unofficial "CNAF technical instruction IT-2026-080 of 2 April 2026: change of the activity-bonus calculation";\n'
             "}\n")
    for ed, window, label_fr, label_en in (
            ("CNAF_IT_2026_080_PDF", "[@2026-04-01, infinity)",
             "IT-2026-080 : bytes officiels du PDF (caf.fr, instruction CNAF)",
             "IT-2026-080: official PDF bytes (caf.fr, CNAF instruction)"),
            ("CNAF_IT_2026_080_TEXT", "[@2026-04-01, infinity)",
             "IT-2026-080 : texte de mise en page extrait du PDF officiel",
             "IT-2026-080: layout text extracted from the official PDF")):
        b.append(f"\nedition {ed} of CNAF_IT_2026_080 {{\n"
                 "    language fr;\n"
                 "    officiality official;\n"
                 "    materialization_status PINNED_OFFICIAL_BYTES;\n"
                 f"    in_force {window};\n"
                 f'    label fr official "{label_fr}";\n'
                 f'    label en unofficial "{label_en}";\n'
                 "}\n")
    b.append(f"\npublication CNAF_IT_2026_080_PDF_BYTES of CNAF_IT_2026_080_PDF {{\n"
             '    media_type "application/pdf";\n'
             f'    uri "{IT_URL}";\n'
             f"    retrieved_at {RETRIEVED_AT};\n"
             f'    content_hash "{pdf_h}";\n'
             f'    local_path "{IT_PDF}";\n'
             "}\n")
    b.append(f"\npublication CNAF_IT_2026_080_TEXT_TXT of CNAF_IT_2026_080_TEXT {{\n"
             '    media_type "text/plain; charset=utf-8";\n'
             f'    uri "{IT_URL}";\n'
             f"    retrieved_at {RETRIEVED_AT};\n"
             f'    content_hash "{txt_h}";\n'
             f'    local_path "{IT_TXT}";\n'
             "}\n")
    for fid, kind, locator, a, zz in IT_FRAGS:
        text = "\n".join(lines[a - 1:zz])
        fh = "sha256:" + hashlib.sha256((text + "\n").encode("utf-8")).hexdigest()
        b.append(f"\n@id(\"{NS}#{fid}\")\n"
                 f"pub fragment {fid} in CNAF_IT_2026_080_TEXT {{\n"
                 f"    kind {kind};\n"
                 f'    locator "{locator}";\n'
                 f'    text fr official """{text}\n'
                 '""";\n'
                 f'    content_hash "{fh}";\n'
                 "}\n")
    b.append("\n// END GENERATED FR-PPA CNAF DOCUMENTS\n")
    return "".join(b)

DECLARED_GAPS = {
    "montant-euro": (
        "single-person euro forfait: RESOLVED 08.10.2026 - decrees 2020-491 "
        "... 2026-222, DSS coefficients and act 2022-1158 art. 9 pinned in "
        "sources/montant/ (chain in 11-forfait-chaine.law); a case-supplied "
        "forfait_base_retenu still prevails; rounding of the product is the "
        "reading ForfaitRevalorisationArrondiCentime (D-82)"),
    "circulaire-it-2026-080": (
        "IT-2026-080 pinned 2026-10-06 (CNAF_IT_2026_080: official PDF "
        "bytes + layout text; fragments on the bonification amounts, the "
        "59x/120x/138x euro edges and the 1.5-SMIC exit point). The "
        "foreign seuils-it-2026-080 scenario anchors on the document; "
        "the decree 2026-222 text itself stays unpinned"),
    "condition-timing": (
        "R842-1..5 modelled from monthly retained facts (06-ouverture); "
        "convergence of the monthly facts with the atemporal 02-droit "
        "facts deferred (B-PPA-CONDITIONS-MENSUELLES)"),
    "ressources-calcul": (
        "resource totals arrive as retained case facts (GOAL: no DSN "
        "extraction); R844/R845 item classifications derived from "
        "itemized retained facts (07-ressources), convergence with the "
        "retained totals deferred"),
    "L843-3-reduction": (
        "hospital/penitentiary reduction (L843-3 via R846-7/8): derived "
        "from retained stay facts; revision-rank facts retained"),
    "L843-5-radiation": (
        "radiation after a no-payment period (L843-5, 24-month decree "
        "duration D846-3): derived from the retained last-payment date; "
        "convergence with the retained elapsed fact deferred"),
    "L845-recovery": (
        "recovery detail (L845-3 al. 2-3, L845-4/5, D847-1/2/3, "
        "R847-1-1/2/3): D553 mechanics PENDING_WAVE with SEC-PF-GEN, "
        "R142/L133-4-1/L241-3 OUT_OF_SCOPE (retained facts); wave 5 "
        "fr.prestations.versement consumes indu_recouvrable"),
    "L846-stats": (
        "statistical reporting duties (L846-1..3 via D848-1..5, R848-1): "
        "duties with retained performance facts; D848-5 list contents "
        "set by unpinned joint arretes"),
    "R844-3-forfait-logement": (
        "R844-4 APL forfait modalities (R844-3 1°/2°/3°) owned by "
        "CNAF-PPA but outside the FINISH pa 38: retained forfait fact, "
        "same-line convergence pending"),
    "bmaf-cgi-plafonds": (
        "BMAF euros (R844-4), CGI abatement rates/ceilings (R845-1/2), "
        "L241-3 ceiling (D847-2): no public neighbour relation; "
        "retained facts, bridge requests in lines/finish-pa.md"),
}


def frag_name(num: str) -> str:
    return "CSS_" + num.replace("-", "_")


def ed_name(state: str) -> str:
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
    """Sources, editions, publications and fragments of the forfait chain (sources/montant/)."""
    manifest = json.loads((MONTANT_DIR / "manifest.json").read_text(encoding="utf-8"))
    out = ["", "// ---- amount chain (sources/montant/, tools/pin_forfait.py) ----", ""]
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
            uri = manifest["dump"] if row["origin_kind"] == "dump" else (
                "https://echanges.dila.gouv.fr/OPENDATA/LEGI/" + row["origin_kind"] + ".tar.gz")
            block(f"DECRET_{under}", "decree", number, row["titre"],
                  f"Decree No. {number} on the revaluation of the activity bonus flat-rate amount (amount chain)",
                  fragment + "_ED",
                  f"Décret n° {number}, article {row['article']} (montant forfaitaire de la prime d'activité) en vigueur à compter du {COVERAGE_START}",
                  f"Decree No. {number}: article {row['article']} (activity bonus flat-rate amount) as in force from {COVERAGE_START}",
                  EDITION_OPEN, row, uri, retrieved, fragment, "article", f"article/{row['article']}")
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

    debuts = sorted({COVERAGE_START} | {v["debut"] for v in versions
                                          if v["debut"] >= COVERAGE_START})
    outputs = {}

    header = (
        "// Provenance S1: activity bonus (CSS, livre VIII, titre IV:\n"
        "// L. 841-1, L. 842-1..8, L. 843-1..6, L. 844-1, L. 845-1..6,\n"
        "// L. 846-1..3, D. 843-1..4, R. 843-1 in ownership; FINISH pa:\n"
        "// D. 846-1/2/3, D. 847-1/2/3, D. 848-1..5, R. 842-1..5,\n"
        "// R. 843-2, R. 844-1/2/4/5, R. 845-1/2/3, R. 846-1..9,\n"
        "// R. 847-1/1-1/2/3, R. 848-1. Modelled: L. 842-1/2 (right),\n"
        "// L. 842-3 + D. 843-1/2/3 (formula, scales, bonification,\n"
        "// fraction) + D. 843-4 (minimum), R. 843-1 (trimestre M-4..M-2\n"
        "// average), L. 845-3/4/5 (recovery refs); 06-ouverture (R842,\n"
        "// R843-2, D846-1/3), 07-ressources (R844, R845), 08-service\n"
        "// (D846-2, R846), 09-recours (D847, R847), 10-statistiques\n"
        "// (D848, R848-1).\n"
        "// Block generated by tools/build_sources.py from the registry\n"
        "// .scratch/reg-css.json (cut 2026-10-06; alineas and versions\n"
        "// from the DILA LEGI mirror). Do not edit by hand.\n"
        "//\n"
        "// Coverage from 2021-01-01. Editions run back to back from the\n"
        "// coverage start through every pinned debut (12 editions:\n"
        "// 2021-03-25 R844-5/R847-1-1, 2021-06-01 D847-3, 2022-03-21\n"
        "// R844-5, 2023-12-31 R844-1/R844-5, 2024-07-01 D848-4,\n"
        "// 2026-06-27 R844-1 join the previous six). Decree 2025-185\n"
        "// shifts R. 843-1/R. 842-2/R. 843-2/R. 845-1/R. 845-2 to\n"
        "// M-4..M-2 from 2025-02-28; decree 2025-292 lowers the fraction\n"
        "// 61 % -> 59.85 % from 2025-03-31; decree 2026-222 raises the\n"
        "// bonification 120x/29.101 % -> 138x/37.7 % from 2026-04-01.\n"
        "// NOTA joins the fragment only where it carries applicability\n"
        "// (D843-2, D843-3, R843-1, R842-2, R843-2, R844-1, R844-5,\n"
        "// R845-1, R845-2, R847-1-1); see sources/articles.json.\n"
        "// The single-person euro forfait chain (L. 842-3, L. 161-25) comes\n"
        "// from sources/montant/ (tools/pin_forfait.py): block \"amount chain\"\n"
        "// at the end of the CSS part (decrees, DSS coefficient paragraphs,\n"
        "// act 2022-1158).\n"
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
           'package fr.css.prime_activite version "0.1.0";',
           'namespace "urn:fr:corpus:clir:ppa";', "",
           "source CSS {", "    kind code;", "    jurisdiction FR;",
           '    label fr official "Code de la sécurité sociale";',
           '    label en unofficial "French Social Security Code";', "}",
           ""]
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
    law.extend(montant_blocks())
    outputs["01-sources.law"] = "\n".join(law) + it_block()

    # W4 source layout (D-43): one lettered article is the unit of every
    # edition document; per-edition scope lists exactly the member nums
    # (early editions lack later-created wordings: no retroactive scope).
    def ed_members(debut):
        return sorted({v["num"] for v in versions
                       if v["debut"] <= debut and (v["fin"] is None or
                                                  debut < v["fin"] or
                                                  v["fin"] == "2999-01-01")})

    articles_doc = {
        "$comment": ("Source scope of package fr/css/prime_activite "
                     "(wave 4, W4-PPA + FINISH pa): 68 CSS articles, "
                     "registry cut 2026-10-06. Superseded versions pinned "
                     "where a modelled norm changed in coverage (2025-185 "
                     "trimestre/timing, 2025-292 fraction, 2026-222 "
                     "bonification, 2023-1378 R844 lists, 2024-606 "
                     "publisher, 2026-535 birth leave). The euro forfait chain "
                     "(decrees, DSS coefficients, act 2022-1158 art. 9) is "
                     "pinned separately in sources/montant/."),
        "coverage_start": COVERAGE_START,
        "dump": {"registry": ".scratch/reg-css.json",
                 "registry_cutoff": "2026-10-06",
                 "retrieved_at": "2026-10-06T00:00:00Z",
                 "url": DUMP_URL},
        "scope": SCOPE,
        "unit": "fr_code_lettered_article",
        "document": f"editions/{ed_name(debuts[-1])}.txt",
        "pinned": versions,
        "editions": [{"edition": ed_name(d),
                      "unit": "fr_code_lettered_article",
                      "scope": ed_members(d),
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
        "$comment": ("Source scope of package fr/css/prime_activite "
                     "(wave 4, W4-PPA + FINISH pa): 68 CSS articles, "
                     "registry cut 2026-10-06. Bytes: alineas of the "
                     "registry (DILA LEGI mirror); old wordings from "
                     "mirror dump. The euro forfait chain (decrees, DSS "
                     "coefficients, act 2022-1158 art. 9) is pinned in "
                     "sources/montant/ (tools/pin_forfait.py)."),
        "scope": SCOPE,
        "unit": "fr_code_lettered_article",
        "editions": [ed_name(d) for d in debuts],
    }
    outputs["sources/source-manifest.json"] = (json.dumps(manifest,
                                                          ensure_ascii=False,
                                                          indent=2) + "\n")
    if args.write:
        for rel, content in outputs.items():
            p = PKG / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        print(f"wrote {len(outputs)} files")
        return
    # --check: every output must exist byte-identical.
    bad = []
    for rel, content in outputs.items():
        p = PKG / rel
        if not p.exists():
            bad.append(f"missing {rel}")
        elif p.read_text(encoding="utf-8") != content:
            bad.append(f"drift {rel}")
    if bad:
        print("SOURCES NOT CURRENT:")
        for b in bad:
            print("  " + b)
        sys.exit(1)
    print(f"SOURCES OK ({len(outputs)} files)")


if __name__ == "__main__":
    main()
