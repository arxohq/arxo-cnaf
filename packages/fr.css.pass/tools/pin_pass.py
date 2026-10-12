#!/usr/bin/env python3
"""Закрепить arrêtés о плафоне социального страхования (PASS) пакета `fr.css.pass`.

PASS (plafond de la sécurité sociale) ежегодно фиксирует arrêté «portant fixation du plafond
de la sécurité sociale pour <год>» (CSS, L. 241-3, D. 242-17 — valeur mensuelle и valeur
journalière). Охват — ДАННЫЕ: `sources/source-manifest.json` (архивы DILA, arrêtés, их
члены-XML и объявленные пробелы); в коде перечней нет.

Байты берутся из открытых данных DILA:
  * 2015, 2016 — глобальный дамп LEGI `Freemium_legi_global_20250713-140000`
    (TNC_en_vigueur/JORF; перенесены из пакета `fr.pf.cf`, где закреплены 08.10.2026);
  * 2017–2025 — глобальный дамп JORF `Freemium_jorf_global_20250713-140000` (найдены
    `--discover` одним проходом по tar, 08.10.2026; в LEGI-дампе этих arrêtés нет);
  * 2026 — суточный архив JORF `JORF_20251223-005127` (JO № 0300 от 23.12.2025).

Четыре режима (сети нет: архивы лежат в `.scratch/`, получение — ручной шаг; дампы большие —
запускать под `nice -n 10`, tar читается потоком, целиком не распаковывается):

  pin_pass.py --discover KEY --years A-B [--merge]
                          один проход по архиву `KEY` из манифеста (хэш архива сверяется):
                          найти arrêtés «portant fixation du plafond de la sécurité sociale
                          pour <год>» за годы A–B и их статьи с «valeur mensuelle»; без --merge —
                          только отчёт; с --merge — дописать arrêtés в `source-manifest.json` и
                          сложить их XML в `sources/pass/xml/<arrêté>/` (годы, уже внесённые в
                          манифест, пропускаются; два arrêtés на один год — ошибка)
  pin_pass.py --extract   достать XML-члены из архивов в `sources/pass/xml/<arrêté>/`
                          (хэш архива сверяется с манифестом, хэши XML — с учётом)
  pin_pass.py --write     из закреплённых XML вывести `sources/pass/<имя>.txt` и
                          `sources/pass/manifest.json` (учёт: NOR, даты, sha256)
  pin_pass.py --check     то же без записи: расхождение = ошибка (сеть и архивы не нужны)
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus/laws/fr/pass"
SCOPE = PKG / "sources/source-manifest.json"
OUT = PKG / "sources/pass"
XML_DIR = OUT / "xml"
#: где лежат скачанные архивы (не в git; `.scratch/` — рабочий каталог проекта)
ARCHIVE_DIRS = [ROOT / ".scratch/legi", ROOT / ".scratch/pass-jorf"]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def contenu(xml: str) -> str:
    """Текст статьи как в первом непустом CONTENU: абзацы построчно, теги сняты."""
    body = re.search(r"<CONTENU>(.*?)</CONTENU>", xml, re.S).group(1)
    body = re.sub(r"<br\s*/>|</p>", "\n", body)
    body = html.unescape(re.sub(r"<[^>]+>", "", body))
    return "\n".join(line.strip() for line in body.splitlines() if line.strip()) + "\n"


def tag(xml: str, name: str) -> str:
    found = re.search(rf"<{name}>([^<]*)", xml)
    return html.unescape(found.group(1)).strip() if found else ""


def scope() -> dict:
    return json.loads(SCOPE.read_text(encoding="utf-8"))


def find_archive(name: str) -> Path:
    for directory in ARCHIVE_DIRS:
        if (directory / name).exists():
            return directory / name
    raise SystemExit(f"архив {name} не найден в {[str(d.relative_to(ROOT)) for d in ARCHIVE_DIRS]}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def xml_path(arrete: dict, member: str) -> Path:
    return XML_DIR / arrete["name"] / Path(member).name


def extract() -> int:
    data = scope()
    by_archive: dict[str, list[tuple[str, Path]]] = {}
    for arrete in data["arretes"]:
        members = [arrete["texte_member"]] + [a["member"] for a in arrete["articles"]]
        for member in members:
            by_archive.setdefault(arrete["archive"], []).append((member, xml_path(arrete, member)))
    for key, wanted in by_archive.items():
        info = data["archives"][key]
        path = find_archive(info["archive"])
        if file_sha256(path) != info["sha256"]:
            print(f"хэш архива {info['archive']} не совпал с манифестом")
            return 1
        names = {member for member, _ in wanted}
        targets = {member: dest for member, dest in wanted}
        by_base: dict[str, list[str]] = {}
        for member in names:
            by_base.setdefault(member.rpartition("/")[2], []).append(member)
        found = 0
        with tarfile.open(path, "r|gz") as tar:
            for entry in tar:
                # JORF-суточные архивы кладут членов под каталог `<архив>/`; LEGI и глобальный JORF — без префикса
                rel = entry.name
                for member in by_base.get(rel.rpartition("/")[2], ()):
                    if rel == member or rel.endswith("/" + member):
                        dest = targets[member]
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_bytes(tar.extractfile(entry).read())
                        found += 1
                if found == len(names):
                    break
        if found != len(names):
            print(f"{info['archive']}: найдено {found} из {len(names)} членов")
            return 1
        print(f"{info['archive']}: {found} XML → sources/pass/xml/")
    return 0


#: заголовок годового arrêté о плафоне: «Arrêté du <дата> portant fixation du plafond de la sécurité
#: sociale pour [l'année ]<год>» (decrets 1980–2011 и иные акты о плафоне в охват не входят)
TITLE_RE = re.compile(r"^Arrêté du [^,]*? portant fixation du plafond de la sécurité sociale pour (?:l'année )?(\d{4})$")
PLAFOND_RE = re.compile(rb"plafond de la s(?:\xc3\xa9|e)curit(?:\xc3\xa9|e) sociale", re.I)


def discover(key: str, years: range, merge: bool) -> int:
    """Один проход по tar архива `key`: arrêtés о плафоне за `years` и их статьи с «valeur mensuelle»."""
    data = scope()
    info = data["archives"][key]
    path = find_archive(info["archive"])
    if file_sha256(path) != info["sha256"]:
        print(f"хэш архива {info['archive']} не совпал с манифестом")
        return 1
    have = {a["year"] for a in data["arretes"]}
    texts: dict[str, dict] = {}  # JORFTEXT → найденный текст
    articles: dict[str, list[dict]] = {}  # JORFTEXT → статьи с valeur mensuelle
    seen = {"members": 0, "texte_version": 0, "article": 0, "plafond_texts": 0}
    with tarfile.open(path, "r|gz") as tar:
        for entry in tar:
            if not entry.isfile():
                continue
            seen["members"] += 1
            name = entry.name
            if "/texte/version/" in name:
                seen["texte_version"] += 1
                raw = tar.extractfile(entry).read()
                found = re.search(rb"<TITREFULL>([^<]*)", raw)
                if not (found and PLAFOND_RE.search(found.group(1))):
                    continue
                seen["plafond_texts"] += 1
                title = " ".join(html.unescape(found.group(1).decode("utf-8")).split())
                matched = TITLE_RE.match(title)
                if matched and int(matched.group(1)) in years:
                    xml = raw.decode("utf-8")
                    texts[tag(xml, "ID")] = {"year": int(matched.group(1)), "member": name, "raw": raw,
                                             "date_texte": tag(xml, "DATE_TEXTE"), "nor": tag(xml, "NOR"),
                                             "title": title}
            elif "/article/" in name:
                seen["article"] += 1
                raw = tar.extractfile(entry).read()
                if b"valeur mensuelle" in raw and b"plafond" in raw:
                    xml = raw.decode("utf-8")
                    cid = re.search(r'<TEXTE cid="(JORFTEXT\d+)"', xml)
                    if cid:
                        articles.setdefault(cid.group(1), []).append(
                            {"num": tag(xml, "NUM"), "id": tag(xml, "ID"), "member": name, "raw": raw})
    print(f"просмотрено {seen['members']} членов: версий текстов {seen['texte_version']}, статей {seen['article']}; "
          f"текстов с «plafond de la sécurité sociale» в заголовке {seen['plafond_texts']}")
    by_year: dict[int, list[str]] = {}
    for jorftext, text in texts.items():
        by_year.setdefault(text["year"], []).append(jorftext)
    code = 0
    new_rows = []
    for year in sorted(years):
        ids = by_year.get(year, [])
        if len(ids) > 1:
            print(f"{year}: НЕСКОЛЬКО arrêtés ({', '.join(ids)}) — нужен ручной разбор, ряд ключом год не выдержит")
            code = 1
            continue
        if not ids:
            print(f"{year}: arrêté не найден в {info['archive']} (граница; описание поиска — README)")
            continue
        jorftext = ids[0]
        text = texts[jorftext]
        arts = sorted(articles.get(jorftext, []), key=lambda a: a["num"])
        print(f"{year}: {text['title']} — {text['nor']} — {jorftext}; статьи с valeur mensuelle: "
              f"{[a['num'] + ' ' + a['id'] for a in arts] or 'НЕТ'}"
              + (" (уже в манифесте)" if year in have else ""))
        if not arts:
            code = 1
            continue
        if year in have:
            continue
        new_rows.append((jorftext, text, arts))
    if merge and code == 0:
        for jorftext, text, arts in new_rows:
            row = {"name": f"arrete-{text['date_texte']}", "year": text["year"], "jorftext": jorftext,
                   "archive": key, "texte_member": text["member"],
                   "articles": [{"num": a["num"], "id": a["id"], "member": a["member"]} for a in arts]}
            data["arretes"].append(row)
            for member, raw in [(text["member"], text["raw"])] + [(a["member"], a["raw"]) for a in arts]:
                dest = xml_path(row, member)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
        data["arretes"].sort(key=lambda a: (a["year"], a["name"]))
        SCOPE.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"в манифест добавлено arrêtés: {len(new_rows)}; XML → sources/pass/xml/")
    return code


def build() -> tuple[dict[str, str], dict]:
    """Тексты статей и учёт из закреплённых XML (без архивов)."""
    data = scope()
    texts: dict[str, str] = {}
    rows = []
    for arrete in data["arretes"]:
        head_raw = xml_path(arrete, arrete["texte_member"]).read_bytes()
        head = head_raw.decode("utf-8")
        archive = data["archives"][arrete["archive"]]
        for art in arrete["articles"]:
            raw = xml_path(arrete, art["member"]).read_bytes()
            xml = raw.decode("utf-8")
            number = tag(xml, "NUM")
            if number != art["num"]:
                raise SystemExit(f"{arrete['name']}: номер статьи {number!r} != охват {art['num']!r}")
            text = contenu(xml)
            year = arrete["year"]
            if "valeur mensuelle" not in text:
                raise SystemExit(f"{arrete['name']} art. {number}: нет «valeur mensuelle»")
            if f"pour {year}" not in tag(head, "TITREFULL"):
                raise SystemExit(f"{arrete['name']}: заголовок не называет {year}")
            if not re.search(rf"1(?:er)? janvier(?: et jusqu'au 31 décembre)? {year}|à compter du 1er janvier {year}", text):
                raise SystemExit(f"{arrete['name']}: текст статьи не привязан к {year}")
            stem = f"{arrete['name']}-art{number}"
            texts[stem] = text
            rows.append({"name": stem, "arrete": arrete["name"], "year": year, "jorftext": arrete["jorftext"],
                         "article_id": art["id"], "article": number,
                         "titre": tag(head, "TITREFULL"), "nor": tag(head, "NOR"),
                         "date_texte": tag(head, "DATE_TEXTE"), "date_publi": tag(head, "DATE_PUBLI"),
                         "parution": tag(head, "ORIGINE_PUBLI"),
                         "etat": tag(xml, "ETAT"), "version_debut": tag(xml, "DATE_DEBUT"),
                         "archive": archive["archive"], "archive_url": archive["url"],
                         "texte_member": arrete["texte_member"],
                         "texte_xml": str(xml_path(arrete, arrete["texte_member"]).relative_to(PKG)),
                         "texte_xml_sha256": sha256(head_raw),
                         "member": art["member"], "xml": str(xml_path(arrete, art["member"]).relative_to(PKG)),
                         "xml_sha256": sha256(raw),
                         "text": f"sources/pass/{stem}.txt", "text_sha256": sha256(text.encode("utf-8"))})
    rows.sort(key=lambda r: (r["year"], r["name"]))
    manifest = {"scope": "sources/source-manifest.json", "texts": rows}
    return texts, manifest


def write() -> int:
    texts, manifest = build()
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, text in texts.items():
        (OUT / f"{stem}.txt").write_text(text, encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"закреплено {len(texts)} текстов → {OUT.relative_to(ROOT)}")
    return 0


def check() -> int:
    texts, manifest = build()
    bad = []
    for stem, text in texts.items():
        path = OUT / f"{stem}.txt"
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            bad.append(stem)
    want = json.dumps(manifest, ensure_ascii=False, indent=1) + "\n"
    if not (OUT / "manifest.json").exists() or (OUT / "manifest.json").read_text(encoding="utf-8") != want:
        bad.append("manifest.json")
    if bad:
        print("расхождения:", ", ".join(bad))
        return 1
    print(f"OK: {len(texts)} текстов совпадают с закреплёнными XML и учётом")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--discover", metavar="KEY", help="ключ архива из манифеста для поиска arrêtés")
    ap.add_argument("--years", metavar="A-B", help="годы для --discover, например 2017-2025")
    ap.add_argument("--merge", action="store_true", help="--discover: дописать найденное в манифест и сложить XML")
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if not (args.discover or args.extract or args.write or args.check):
        ap.error("укажите --discover, --extract, --write или --check")
    code = 0
    if args.discover:
        if not args.years or not re.fullmatch(r"\d{4}-\d{4}", args.years):
            ap.error("--discover требует --years A-B")
        first, last = (int(x) for x in args.years.split("-"))
        code = discover(args.discover, range(first, last + 1), args.merge)
    if code == 0 and args.extract:
        code = extract()
    if code == 0 and args.write:
        code = write()
    if code == 0 and args.check:
        code = check()
    return code


if __name__ == "__main__":
    sys.exit(main())
