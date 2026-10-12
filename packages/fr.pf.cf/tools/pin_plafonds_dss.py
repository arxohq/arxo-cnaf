#!/usr/bin/env python3
"""Закрепить опубликованные плафоны CF (D-83): база и надбавки порознь, по годам.

D-83 переносит на CF образец D-81 (pf-af): R. 522-2 / R. 522-4 поручают декрету
«le montant du plafond de ressources et celui de la majoration» и ревалоризацию
1 января, а инструкции DSS печатают базу и надбавки отдельно (каждую со своим
округлением). Плафон поэтому строится как «база + надбавка за ребёнка × n»
из ОПУБЛИКОВАННЫХ сумм, а не из одного номинала и процентов.

Источник — те же байты, что закрепил пакет `fr.css.revalorisation` (читаются, не
правятся): тексты `revalorisation/sources/dss-*.txt`. Из каждого берутся два
дословных среза:

  * раздел «Plafonds … du complément familial» (метрополия, плафон CF: база,
    25 % на ребёнка, 30 % с третьего, надбавка за двойную активность или
    изоляцию, строки таблицы);
  * раздел «Plafonds … du montant majoré du complément familial» (R. 522-4: своя
    база, свои надбавки; в пакете revalorisation для него фрагмента нет);

плюс абзац инструкции 2016 о том, что суммы 2016 года «reconduits à l'identique» на
2017 год (плафоны 2016 = плафоны 2017).

Пишет `sources/dss-plafonds/<инструкция>-cf.txt`, `-majore.txt`,
`dss-2016-396-reconduction.txt` и учёт `sources/dss-plafonds/manifest.json` (имя
источника и издания пакета revalorisation, sha256 всего текста и среза, диапазон
строк, разобранные числа). Срез — подстрока текста инструкции; sha256 всего текста
сверяется с `content_hash` публикации в `revalorisation/01-sources.law`. Числа
сверяются с напечатанной таблицей инструкции (строки для n = 3, 4 и, где есть,
n = 1, 2); расхождения опечаток самой инструкции записываются в `anomalies`.

  python3 corpus/laws/fr/pf-cf/tools/pin_plafonds_dss.py --write
  python3 corpus/laws/fr/pf-cf/tools/pin_plafonds_dss.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus/laws/fr/pf-cf"
OUT = PKG / "sources/dss-plafonds"
REVALO = ROOT / "corpus/laws/fr/revalorisation"

#: год плафона (1 января) → файл инструкции пакета revalorisation. 2016 — не отдельная
#: инструкция: суммы 2016 «reconduits à l'identique» на 2017 (см. RECONDUCTION).
INSTRUCTIONS = {
    2015: "dss-2014-345",
    2017: "dss-2016-396",
    2018: "dss-2017-352",
    2019: "dss-2018-279",
    2020: "dss-2019-261",
    2021: "dss-2020-226",
    2022: "dss-2021-247",
    2023: "dss-2022-283",
    2024: "dss-2023-205",
    2025: "dss-2024-181",
    2026: "dss-2025-177",
}
RECONDUCTION = ("dss-2016-396", 2016, 2017)

_NUM = r"\d[\d   ]*"
_HEAD_CF = re.compile(r"Plafonds de ressources applicables pour l.attribution du compl[ée]ment familial")
_HEAD_MAJORE = re.compile(r"Plafonds de ressources applicables pour l.attribution du montant major[ée]")
_END = re.compile(r"[Pp]ar enfant suppl[ée]mentaire[^\n]*\n")


def num(text: str) -> int:
    return int(re.sub(r"[   ]", "", text))


def line_start(text: str, index: int) -> int:
    return text.rfind("\n", 0, index) + 1


def slices(text: str) -> dict[str, tuple[int, int]]:
    """Начало/конец срезов CF и montant majoré (первое вхождение — метрополия)."""
    head = _HEAD_CF.search(text)
    assert head, "нет раздела плафонов CF"
    a = line_start(text, head.start())
    end = _END.search(text, head.end())
    assert end, "нет строки «par enfant supplémentaire» в разделе CF"
    cf = (a, end.end())
    head2 = _HEAD_MAJORE.search(text, cf[1])
    assert head2, "нет раздела montant majoré"
    b = line_start(text, head2.start())
    end2 = _END.search(text, head2.end())
    assert end2, "нет строки «par enfant supplémentaire» в разделе montant majoré"
    return {"cf": cf, "majore": (b, end2.end())}


def parse(section: str) -> dict:
    """Числа раздела: база, надбавки, строки таблицы {n: (плафон, плафон с двойной активностью)}."""
    base = re.search(rf"(?:Plafond de base|Base)\s*:\s*({_NUM})\s*€", section)
    m25 = re.search(rf"25\s*%\s*par enfant à charge\s*:?\s*({_NUM})\s*€", section)
    m30 = re.search(rf"30\s*%\s*par enfant à charge à partir du 3\s*(?:e|ème|ᵉ)?\s*:?\s*({_NUM})\s*€", section)
    dbl = re.search(rf"pour double activité ou pour isolement\s*:?\s*({_NUM})\s*€", section, re.I)
    assert base and m25 and m30 and dbl, f"не разобраны надбавки: {section[:200]!r}"
    rows = {}
    for n, a, b in re.findall(rf"^\s*(\d) enfants?\s+({_NUM}?)\s{{2,}}({_NUM})\s*$", section, re.M):
        rows[int(n)] = (num(a) if a.strip() else None, num(b))
    extra = re.search(rf"[Pp]ar enfant suppl[ée]mentaire\s+\+?\s*({_NUM})\s{{2,}}\+?\s*({_NUM})", section)
    assert extra, "нет строки «par enfant supplémentaire»"
    return {"base": num(base.group(1)), "majoration_enfant": num(m25.group(1)),
            "majoration_troisieme": num(m30.group(1)), "majoration_biactivite": num(dbl.group(1)),
            "rows": {str(k): v for k, v in rows.items()},
            "par_enfant_supplementaire": [num(extra.group(1)), num(extra.group(2))]}


def build(n: int, p: dict) -> tuple[int, int]:
    plain = p["base"] + p["majoration_enfant"] * min(n, 2) + p["majoration_troisieme"] * max(n - 2, 0)
    return plain, plain + p["majoration_biactivite"]


def anomalies(p: dict) -> list[str]:
    """Строки напечатанной таблицы, не равные «база + надбавки» (опечатки инструкции)."""
    out = []
    for n, (plain, dbl) in p["rows"].items():
        want = build(int(n), p)
        if plain is not None and plain != want[0]:
            out.append(f"n={n}: плафон напечатан {plain}, база + надбавки {want[0]}")
        if dbl != want[1]:
            out.append(f"n={n}: плафон с двойной активностью напечатан {dbl}, база + надбавки {want[1]}")
    if p["par_enfant_supplementaire"][0] != p["majoration_troisieme"]:
        out.append(f"par enfant supplémentaire {p['par_enfant_supplementaire'][0]} ≠ 30 % {p['majoration_troisieme']}")
    return out


def revalo_publications() -> dict[str, dict]:
    """txt инструкции → {source, edition, uri, retrieved_at, content_hash} из 01-sources.law revalorisation."""
    law = (REVALO / "01-sources.law").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'publication (\w+) of (\w+) \{\s*media_type "text/plain; charset=utf-8";\s*uri "([^"]+)";\s*'
                         r'retrieved_at (@[\dT:\-Z]+);\s*content_hash "sha256:(\w+)";\s*local_path "(sources/dss-[\w\-]+\.txt)";', law):
        pub, edition, uri, retrieved, digest, local = m.groups()
        src = re.search(rf"edition {edition} of (\w+) \{{", law).group(1)
        label = re.search(rf"source {src} \{{.*?label fr official \"([^\"]+)\";\s*label en unofficial \"([^\"]+)\";", law, re.S)
        out[local] = {"source": src, "edition": edition, "publication": pub, "uri": uri, "retrieved_at": retrieved,
                      "content_hash": digest, "label_fr": label.group(1), "label_en": label.group(2)}
    return out


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect() -> tuple[list[dict], dict[str, str]]:
    pubs = revalo_publications()
    rows, files = [], {}
    names = dict(INSTRUCTIONS)
    for year, stem in sorted(names.items()):
        local = f"sources/{stem}.txt"
        raw = (REVALO / local).read_bytes()
        pub = pubs[local]
        assert sha(raw) == pub["content_hash"], f"{local}: sha256 расходится с публикацией revalorisation"
        text = raw.decode("utf-8")
        cut = slices(text)
        for kind in ("cf", "majore"):
            a, b = cut[kind]
            section = text[a:b]
            assert '"""' not in section and "\\" not in section, f"{stem} {kind}: недопустимые символы среза"
            assert text[a:b] == section
            p = parse(section)
            name = f"{stem}-{kind}"
            files[f"{name}.txt"] = section
            rows.append({"year": year, "kind": kind, "name": name, "instruction": stem, **{k: pub[k] for k in
                         ("source", "edition", "uri", "retrieved_at", "label_fr", "label_en")},
                         "revalorisation_text": f"corpus/laws/fr/revalorisation/{local}",
                         "text_sha256": pub["content_hash"], "line_from": text.count("\n", 0, a) + 1,
                         "line_to": text.count("\n", 0, b),
                         "slice": f"sources/dss-plafonds/{name}.txt", "slice_sha256": sha(section.encode("utf-8")),
                         **p, "anomalies": anomalies(p)})
    stem, year, later = RECONDUCTION
    local = f"sources/{stem}.txt"
    text = (REVALO / local).read_bytes().decode("utf-8")
    start = text.index("Or compte tenu de la stabilité des prix en 2015")
    end = text.index("1er janvier 2017 au 31 décembre 2017.\n", start) + len("1er janvier 2017 au 31 décembre 2017.\n")
    start = line_start(text, start)
    section = text[start:end]
    assert "reconduits à l’identique" in section
    pub = pubs[local]
    files[f"{stem}-reconduction.txt"] = section
    rows.append({"year": year, "kind": "reconduction", "name": f"{stem}-reconduction", "instruction": stem,
                 "same_as_year": later, **{k: pub[k] for k in ("source", "edition", "uri", "retrieved_at", "label_fr", "label_en")},
                 "revalorisation_text": f"corpus/laws/fr/revalorisation/{local}", "text_sha256": pub["content_hash"],
                 "line_from": text.count("\n", 0, start) + 1, "line_to": text.count("\n", 0, end),
                 "slice": f"sources/dss-plafonds/{stem}-reconduction.txt", "slice_sha256": sha(section.encode("utf-8"))})
    return rows, files


def manifest(rows: list[dict]) -> str:
    doc = {"scope": "Плафоны CF (R. 522-2) и montant majoré (R. 522-4), метрополия: срезы инструкций DSS, "
                    "закреплённых пакетом fr.css.revalorisation; 2016 — по абзацу о reconduction",
           "decision": "D-83", "texts": rows}
    return json.dumps(doc, ensure_ascii=False, indent=1) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    assert args.write or args.check, "укажите --write или --check"
    rows, files = collect()
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            (OUT / name).write_text(text, encoding="utf-8")
        (OUT / "manifest.json").write_text(manifest(rows), encoding="utf-8")
        print(f"закреплено {len(rows)} срезов → {OUT.relative_to(ROOT)}")
    bad = []
    for name, text in files.items():
        path = OUT / name
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            bad.append(name)
    if not (OUT / "manifest.json").exists() or (OUT / "manifest.json").read_text(encoding="utf-8") != manifest(rows):
        bad.append("manifest.json")
    for row in rows:
        for note in row.get("anomalies", []):
            print(f"  опечатка/расхождение таблицы {row['name']}: {note}")
    if bad:
        print("расхождения:", ", ".join(bad))
        return 1
    print(f"OK: {len(rows)} срезов совпадают с байтами revalorisation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
