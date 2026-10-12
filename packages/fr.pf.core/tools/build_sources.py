#!/usr/bin/env python3
"""Pinning of fr.pf.core package sources (CNAF wave 1).

Reads the CSS registry (.scratch/reg-css.json, snapshot 2026-10-06) and builds:
  sources/css/<ARTICLE>.txt   - pinned article text (registry alineas);
  sources/articles.json        - accounting: versions, NOTA, coverage, gaps;
  01-sources.law               - source CSS, back-to-back editions, publications
                                 (one pinned file per edition concatenating its
                                 debuting fragments), fragments (one per
                                 article, in the debut edition of the pinned
                                 version).

Scope: 95 articles = 71 wave-1 (68 L-series L511-1-L584-1 except
L521-*/L531-*, + R512-1, R512-2, R532-3; L552-2/4/6 and L554-2/3 are
already among them) + 22 FINISH payment-core (R514-1, R552-1..4, R553-1,
R553-2, R553-3, R553-3-1..7, D552-6/7, D553-1..5) + 2 D73 DOM
(L755-4, D755-2, both debut before coverage start). Coverage from
01.01.2021 (plan D-01). Edition states are FROZEN at the wave-1 sixteen
(PW-01, journaled): new debuts slot into their containing edition via
max(state <= debut) and rules carry exact debuts in effective windows,
so all wave-1 fragments, editions and publications stay byte-identical.
The only quantized debut is 2022-01-31 (D552-7, R552-3, R552-4 -> base
fragment in ED2022_01); any further new debut fails the build until an
edition decision is recorded.

Honest gap: articles whose debut falls after 01.01.2021 without a pinned
predecessor declare gap=prev-text-unpinned when a MODIFIE predecessor
exists, else gap=not-in-force-before-debut (created after coverage
start, or abrogated gap: D552-7, L552-7, R552-4), not silence.
Five predecessors are present in the mirror dump and pinned as PREV
fragments with coverage from 2021-01-01: L523-1 (wave 1), L532-2
(2018-06-14 to 2025-12-31), L552-4 (1985-12-21 to 2022-09-01),
D553-1 (2021-01-01 to 2022-01-01), R552-3 (2015-01-01 to 2022-01-31).

Usage:
  python3 corpus/laws/fr/pf-core/tools/build_sources.py --check   # verify
  python3 corpus/laws/fr/pf-core/tools/build_sources.py --write   # write
"""

import argparse
import hashlib
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-core"
REGISTRY = ROOT / ".scratch" / "reg-css.json"
MIRROR = ROOT / ".scratch" / "legi" / "mirror" / "LEGITEXT000006073189"
CUTOFF = "2026-10-06"
COVERAGE_START = "2021-01-01"
DUMP_URL = ("https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
            "Freemium_legi_global_20250713-140000.tar.gz")
RETRIEVED_AT = "@2026-10-06T00:00:00Z"

NS = "urn:fr:corpus:clir:pf-core"

# Pinned predecessors: versions present in the mirror dump whose alineas are
# rendered straight from the mirror XML with the registry's own rule
# (cell_text/block_lines, byte-identical copy of
# corpus/tools/sources/sync/fr_legi_registry.py), because the registry
# carries only the current version's alineas. Each entry pins a PREV base
# fragment plus repeats over the pre-debut states; the build asserts the
# predecessor fin equals the pinned debut (chain integrity).
# L523-1 (wave 1): I. 1-4 word-identical, only IV 5 added on 2021-12-25.
# L532-2: I, III-V word-identical, only II items changed on 2025-12-31.
# L552-4: 1985 text has three schooling pieces vs two from 2022-09-01.
# D553-1: 2021 numbers identical to 2022 (revalorisation sentence differs).
# R552-3: 2015 text has the L531-10 exception in III and no IV.
PREVS = [
    {
        "num": "L523-1",
        "id": "LEGIARTI000041398664",
        "debut": "2019-12-28",
        "fin": "2021-12-25",
        "etat": "MODIFIE",
        "xml_rel": "article/LEGI/ARTI/00/00/41/39/86/LEGIARTI000041398664.xml",
        "frag": "CSS_L523_1_PREV",
        "article_file": "sources/css/L523-1-prev.txt",
    },
    {
        "num": "L532-2",
        "id": "LEGIARTI000037062512",
        "debut": "2018-06-14",
        "fin": "2025-12-31",
        "etat": "MODIFIE",
        "xml_rel": "article/LEGI/ARTI/00/00/37/06/25/LEGIARTI000037062512.xml",
        "frag": "CSS_L532_2_PREV",
        "article_file": "sources/css/L532-2-prev.txt",
    },
    {
        "num": "L552-4",
        "id": "LEGIARTI000006743415",
        "debut": "1985-12-21",
        "fin": "2022-09-01",
        "etat": "MODIFIE",
        "xml_rel": "article/LEGI/ARTI/00/00/06/74/34/LEGIARTI000006743415.xml",
        "frag": "CSS_L552_4_PREV",
        "article_file": "sources/css/L552-4-prev.txt",
    },
    {
        "num": "D553-1",
        "id": "LEGIARTI000042827715",
        "debut": "2021-01-01",
        "fin": "2022-01-01",
        "etat": "MODIFIE",
        "xml_rel": "article/LEGI/ARTI/00/00/42/82/77/LEGIARTI000042827715.xml",
        "frag": "CSS_D553_1_PREV",
        "article_file": "sources/css/D553-1-prev.txt",
    },
    {
        "num": "R552-3",
        "id": "LEGIARTI000030049068",
        "debut": "2015-01-01",
        "fin": "2022-01-31",
        "etat": "MODIFIE",
        "xml_rel": "article/LEGI/ARTI/00/00/30/04/90/LEGIARTI000030049068.xml",
        "frag": "CSS_R552_3_PREV",
        "article_file": "sources/css/R552-3-prev.txt",
    },
]

# Frozen edition states (wave-1 sixteen, PW-01): derived states would add
# 2022-01-31 and shorten ED2022_01, forcing a repeat cite onto every
# existing rule; the frozen layout keeps wave-1 output byte-identical.
FROZEN_STATES = [
    "2021-01-01", "2021-05-01", "2021-11-17", "2021-12-25",
    "2022-01-01", "2022-02-09", "2022-03-01", "2022-09-01",
    "2023-07-21", "2024-01-01", "2025-02-28", "2025-09-01",
    "2025-12-31", "2026-01-01", "2026-04-01", "2026-06-14",
]

# FINISH payment-core R/D articles (exact allowlist: the regex below only
# covers L-series, and a prefix regex would sweep unrelated R/D articles).
RD_ADDED = frozenset({
    "R514-1",
    "R552-1", "R552-2", "R552-3", "R552-4",
    "R553-1", "R553-2", "R553-3",
    "R553-3-1", "R553-3-2", "R553-3-3", "R553-3-4",
    "R553-3-5", "R553-3-6", "R553-3-7",
    "D552-6", "D552-7",
    "D553-1", "D553-2", "D553-3", "D553-4", "D553-5",
})

# D73 DOM twins (exact allowlist: Livre VII is outside every series
# regex above; both debut before coverage start, so no new quantized
# state and no PREV pin - SOURCE_ONLY addressability only).
DOM_ADDED = frozenset({
    "L755-4",
    "D755-2",
})


def cell_text(fragment: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", fragment)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text).replace("\xa0", " ")
    return " ".join(unicodedata.normalize("NFC", text).split())


def block_lines(block: str) -> list:
    """One alinea, one line, in document order (registry rule, see above)."""
    lines = []

    def bare(segment: str) -> None:
        lines.extend(cell_text(part) for part in re.split(r"<br\s*/?>", segment) if cell_text(part))

    position = 0
    for match in re.finditer(r"<table\b.*?</table>|<p\b.*?</p>", block, re.S):
        bare(block[position:match.start()])
        position = match.end()
        chunk = match.group(0)
        if chunk.startswith("<table"):
            for row in re.findall(r"<tr\b.*?</tr>", chunk, re.S):
                cells = [cell_text(x) for x in re.findall(r"<t[hd]\b.*?</t[hd]>", row, re.S)]
                if any(cells):
                    lines.append(" | ".join(c for c in cells if c))
        else:
            text = cell_text(chunk)
            if text:
                lines.append(text)
    bare(block[position:])
    return lines


def predecessor_alineas(prev: dict) -> tuple:
    """Render one predecessor's alineas from its mirror XML."""
    raw = (MIRROR / "dump" / prev["xml_rel"]).read_bytes()
    xml = raw.decode("utf-8")
    body = re.search(r"<BLOC_TEXTUEL>(.*?)</BLOC_TEXTUEL>", xml, re.S)
    assert body, f"predecessor {prev['num']} XML has no BLOC_TEXTUEL"
    return block_lines(body.group(1)), hashlib.sha256(raw).hexdigest()


def scope_filter(num: str) -> bool:
    if num in ("R512-1", "R512-2", "R532-3"):
        return True
    if num in RD_ADDED:
        return True
    if num in DOM_ADDED:
        return True
    if re.match(r"L521-", num) or re.match(r"L531-", num):
        return False
    return bool(re.match(r"L51[1-9]-", num) or re.match(r"L5[2-8]\d-", num))


def frag_name(num: str) -> str:
    return "CSS_" + num.replace("-", "_")


def ed_name(state: str) -> str:
    return "CSS_ED" + state[:4] + "_" + state[5:7]


def law_escape(text: str) -> str:
    if '"""' in text:
        raise ValueError("triple-quote in article text, escaping needed")
    return text


def load_scope():
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    arts = [a for a in reg["articles"] if scope_filter(a["num"])]
    arts.sort(key=lambda a: a["num"])
    return reg, arts


def build():
    reg, arts = load_scope()
    assert len(arts) == 95, f"scope drift: {len(arts)} articles, want 95"
    states = list(FROZEN_STATES)
    quantized = sorted({a["debut"] for a in arts
                        if a["debut"] >= COVERAGE_START} - set(states))
    assert quantized == ["2022-01-31"], \
        f"new debuts need an edition decision: {quantized}"
    outputs = {}  # rel path -> bytes

    header = (
        "// Provenance 194: prestations familiales common layer (CSS, Book V).\n"
        "// Block below generated by tools/build_sources.py from registry\n"
        "// .scratch/reg-css.json (snapshot 2026-10-06; LEGI alineas and versions,\n"
        "// DILA mirror). Do not edit by hand.\n"
        "//\n"
        "// Coverage from 01.01.2021 (D-01). Editions run back-to-back from that date;\n"
        "// states are frozen at the wave-1 sixteen (PW-01): debut 2022-01-31\n"
        "// slots into the containing ED2022_01 and exact debuts ride on rule\n"
        "// effective windows, so wave-1 output stays byte-identical.\n"
        "// Articles changed version later with earlier text absent from the\n"
        "// mirror (increments only from 07.2025) keep their fragment in the\n"
        "// debut edition of the pinned version, and the window before it\n"
        "// is a declared gap (see sources/articles.json, gap=prev-text-unpinned\n"
        "// with a MODIFIE predecessor, else gap=not-in-force-before-debut).\n"
        "// Five predecessors are pinned as PREV fragments with coverage from\n"
        "// 2021-01-01, no gap: L523-1 (wave 1), L532-2, L552-4, D553-1, R552-3.\n"
        "// BMAF and ceiling figures are published by DSS/2B/2026/46 and\n"
        "// DSS/2B/2025/177 (pinned in fr.css.revalorisation, phase W0-06):\n"
        "// tools/build_bareme.py transcribes them into bareme.json (95\n"
        "// self-checked rows); boundary B-PFCORE-BAREME REMOVED 2026-10-06.\n"
        "// Each edition pins one file (sources/editions/<ED>.txt) concatenating\n"
        "// every fragment in force in it; it is the section 194 publication\n"
        "// of that edition. Repeats carry the same pinned bytes forward so rules\n"
        "// stay anchored past their debut edition (E-0095).\n"
        "\n"
        'language "law.core" version "0.2";\n'
        'package fr.pf.core version "0.1.0";\n'
        f'namespace "{NS}";\n'
        "\n"
        '@id("urn:fr:source:css")\n'
        "source CSS {\n"
        "    kind code;\n"
        "    jurisdiction FR;\n"
        '    label fr official "Code de la sécurité sociale";\n'
        '    label en unofficial "French Social Security Code";\n'
        "}\n"
    )

    editions = []
    for i, st in enumerate(states):
        nxt = states[i + 1] if i + 1 < len(states) else None
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
            f'    label fr official "Code de la sécurité sociale, champ retenu du paquet, état en vigueur à compter du {st}";\n'
            f'    label en unofficial "French Social Security Code: pinned-scope state from {st}";\n'
            f"}}\n"
        )

    frags = "\n// BEGIN GENERATED FR-PF-CORE FRAGMENTS\n"
    accounting = []
    edition_blobs = {}
    for a in arts:
        num = a["num"]
        frag = frag_name(num)
        debut = a["debut"]
        ed_state = (max(s for s in states if s <= debut)
                    if debut >= COVERAGE_START else COVERAGE_START)
        ed = ed_name(ed_state)
        text = f"Article {num}\n" + "\n".join(a["alineas"])
        law_escape(text)
        rel = f"sources/css/{num}.txt"
        blob = (text + "\n").encode("utf-8")
        outputs[rel] = blob
        digest = "sha256:" + hashlib.sha256(blob).hexdigest()
        # Base fragment in the debut edition plus one repeat per later state:
        # a rule fires at legal_time T only through a fragment whose edition
        # window covers T (E-0095), so every edition past the debut needs its
        # own anchor of the same pinned bytes. Pre-debut editions have no
        # fragment: earlier text is unpinned (declared gap), not repeated.
        edition_frags = [(frag, ed)]
        for later in [s for s in states if s > ed_state]:
            later_ed = ed_name(later)
            rep = f"{frag}_{later_ed}"
            edition_frags.append((rep, later_ed))
        for name, in_ed in edition_frags:
            edition_blobs.setdefault(in_ed, []).append((num, blob))
            frags += (
                f"\n"
                f'@id("{NS}#{name}")\n'
                f"pub fragment {name} in {in_ed} {{\n"
                f"    kind article;\n"
                f'    locator "article/{num}";\n'
                f'    text fr official """{text}\n""";\n'
                f'    content_hash "{digest}";\n'
                f"}}\n"
            )
        predecessor = None
        prev_spec = next((p for p in PREVS if p["num"] == num), None)
        if prev_spec is not None:
            # Pinned predecessor (see PREVS): it covers the editions before
            # the current version debut, so it gets its own base fragment
            # plus repeats, same E-0095 pattern. The --check byte comparison
            # is the drift guard for the emitted edition lists.
            assert prev_spec["fin"] == debut, \
                f"predecessor chain drift for {num}: fin {prev_spec['fin']} != debut {debut}"
            prev_alineas, prev_xml_sha = predecessor_alineas(prev_spec)
            prev_text = f"Article {num}\n" + "\n".join(prev_alineas)
            law_escape(prev_text)
            prev_blob = (prev_text + "\n").encode("utf-8")
            prev_digest = "sha256:" + hashlib.sha256(prev_blob).hexdigest()
            outputs[prev_spec["article_file"]] = prev_blob
            prev_states = [s for s in states
                           if COVERAGE_START <= s < debut]
            prev_edition_frags = []
            for i, s in enumerate(prev_states):
                in_ed = ed_name(s)
                name = (prev_spec["frag"] if i == 0
                        else f"{prev_spec['frag']}_{in_ed}")
                prev_edition_frags.append((name, in_ed))
            for name, in_ed in prev_edition_frags:
                edition_blobs.setdefault(in_ed, []).append((num, prev_blob))
                frags += (
                    f"\n"
                    f'@id("{NS}#{name}")\n'
                    f"pub fragment {name} in {in_ed} {{\n"
                    f"    kind article;\n"
                    f'    locator "article/{num}";\n'
                    f'    text fr official """{prev_text}\n""";\n'
                    f'    content_hash "{prev_digest}";\n'
                    f"}}\n"
                )
            predecessor = {
                "id": prev_spec["id"],
                "debut": prev_spec["debut"],
                "fin": prev_spec["fin"],
                "etat": prev_spec["etat"],
                "fragment": prev_spec["frag"],
                "edition": prev_edition_frags[0][1],
                "fragments": [{"name": n, "edition": e}
                              for n, e in prev_edition_frags],
                "article_file": prev_spec["article_file"],
                "content_hash": prev_digest,
                "xml_sha256": prev_xml_sha,
                "xml_rel": prev_spec["xml_rel"],
            }
        gap = None
        if debut > COVERAGE_START and predecessor is None:
            versions = a.get("versions", [])
            has_mod_pred = any(v.get("etat") == "MODIFIE"
                               and v.get("fin") == debut for v in versions)
            gap = ("prev-text-unpinned" if has_mod_pred
                   else "not-in-force-before-debut")
        entry = {
            "num": num,
            "legi_id": a["id"],
            "etat": a["etat"],
            "version_debut": debut,
            "version_fin": a["fin"],
            "coverage_start": (COVERAGE_START if predecessor is not None
                               else max(debut, COVERAGE_START)),
            "gap": gap,
            "fragment": frag,
            "edition": ed,
            "fragments": [{"name": n, "edition": e}
                          for n, e in edition_frags],
            "article_file": rel,
            "content_hash": digest,
            "xml_sha256": a.get("xml_sha256"),
            "xml_rel": a.get("xml_rel"),
            "nota": a.get("nota", []),
            "versions": [
                {"id": v["id"], "debut": v["debut"],
                 "fin": v["fin"], "etat": v["etat"]}
                for v in a.get("versions", [])
            ],
        }
        if predecessor is not None:
            entry["predecessor"] = predecessor
        accounting.append(entry)
    # One pinned file per edition concatenating every fragment in force in
    # it (debuting plus repeats), in article order: every fragment of the
    # edition is a byte-substring of its edition file (LDC-E5202), and the
    # file hash is declared (LDC-E5201).
    pubs = ""
    edition_files = {}
    for name, st, window in editions:
        parts = sorted(edition_blobs.get(name, []), key=lambda nb: nb[0])
        ed_bytes = ("\n".join(b.decode("utf-8") for _, b in parts)).encode("utf-8")
        ed_rel = f"sources/editions/{name}.txt"
        outputs[ed_rel] = ed_bytes
        ed_digest = "sha256:" + hashlib.sha256(ed_bytes).hexdigest()
        edition_files[name] = {"local_path": ed_rel,
                               "content_hash": ed_digest,
                               "articles": [num for num, _ in parts]}
        pubs += (
            f"\n"
            f"publication {name}_TEXT of {name} {{\n"
            f'    media_type "text/plain; charset=utf-8";\n'
            f'    uri "{DUMP_URL}";\n'
            f"    retrieved_at {RETRIEVED_AT};\n"
            f'    content_hash "{ed_digest}";\n'
            f'    local_path "{ed_rel}";\n'
            f"}}\n"
        )
        for acc in accounting:
            if acc["edition"] == name:
                acc["edition_file"] = ed_rel
    outputs["01-sources.law"] = (header + pubs + frags).encode("utf-8")
    outputs["sources/articles.json"] = (
        json.dumps({"cutoff": CUTOFF, "coverage_start": COVERAGE_START,
                    "scope": len(accounting), "articles": accounting,
                    "edition_files": edition_files},
                   ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return outputs, accounting


def check_mirror(accounting):
    """Cross-check pinned XML against the registry (when the mirror is present)."""
    problems = []
    if not MIRROR.exists():
        return ["mirror absent, xml check skipped"]
    for acc in accounting:
        rel = acc.get("xml_rel")
        if not rel:
            continue
        p = MIRROR / "dump" / rel
        if not p.exists():
            # current version may live only in an increment
            cands = sorted(MIRROR.glob(f"increments/*/{rel}"))
            p = cands[-1] if cands else None
        if p is None:
            problems.append(f"{acc['num']}: xml missing in mirror")
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if digest != acc["xml_sha256"]:
            problems.append(f"{acc['num']}: xml sha256 mismatch")
        prev = acc.get("predecessor")
        if prev:
            pp = MIRROR / "dump" / prev["xml_rel"]
            if not pp.exists():
                problems.append(f"{acc['num']}: predecessor xml missing in mirror")
            elif hashlib.sha256(pp.read_bytes()).hexdigest() != prev["xml_sha256"]:
                problems.append(f"{acc['num']}: predecessor xml sha256 mismatch")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    outputs, accounting = build()
    if args.write:
        for rel, blob in outputs.items():
            p = PKG / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(blob)
        print(f"WROTE {len(outputs)} files, {len(accounting)} articles")
        for prob in check_mirror(accounting):
            print("MIRROR:", prob)
        return 0
    # --check (and by default): byte-for-byte comparison
    assert args.check, "give --check or --write"
    errors = []
    for rel, blob in outputs.items():
        p = PKG / rel
        if not p.exists():
            errors.append(f"missing {rel}")
        elif p.read_bytes() != blob:
            errors.append(f"drift {rel}")
    # back-to-back editions: windows cover [2021-01-01, infinity) without holes
    states = sorted({a["version_debut"] for a in accounting
                     if a["version_debut"] >= COVERAGE_START})
    if states[0] != COVERAGE_START:
        errors.append("editions do not start at coverage start")
    gaps = [a["num"] for a in accounting if a["gap"]]
    print(f"articles: {len(accounting)}, editions: {len(states)}, "
          f"declared prev-text gaps: {len(gaps)}")
    for prob in check_mirror(accounting):
        print("MIRROR:", prob)
    if errors:
        print("ERRORS:")
        for e in errors:
            print("  " + e)
        return 1
    print("SOURCES OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
