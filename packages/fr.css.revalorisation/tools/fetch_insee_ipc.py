#!/usr/bin/env python3
"""INSEE IPC → ряды пакета `fr/revalorisation` (фаза 0, по образцу APL/SMIC).

Закрепляются официальные архивы INSEE Melodi (data.gouv.fr, организация INSEE):
DS_IPC_PRINC (mensuel, base 2025, Ensemble COICOP 00 — вход L. 161-25) и
DS_IPC_IND_CAT (1er quintile, Ensemble hors tabac — вход relèvement SMIC,
декрет 2025-1228, ст. 3). Охват — ДАННЫЕ (`sources/source-manifest.json`),
не перечни в коде. ZIP-кэш (`sources/.cache/`) в git не идёт; в git —
извлечённые ряды `sources/insee-ipc-series.json`.

  fetch_insee_ipc.py          — скачать (при отсутствии кэша), проверить sha256,
                                пересобрать ряды из байтов
  fetch_insee_ipc.py --check  — то же без записи: расхождение = ошибка
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PACKAGE = ROOT / "corpus/laws/fr/revalorisation"
SOURCE_DIR = PACKAGE / "sources/insee"
CACHE_DIR = SOURCE_DIR / ".cache"

sys.path.insert(0, str(ROOT / "corpus/tools/sources"))
from fr_manifest import load_package as _load_manifest  # noqa: E402

_MANIFEST = _load_manifest(PACKAGE)
ARCHIVES = {a["name"]: a for a in _MANIFEST["archives"]}
SERIES_JSON = SOURCE_DIR / "insee-ipc-series.json"


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def get_bytes(arch: dict, write_cache: bool) -> bytes:
    cache = CACHE_DIR / arch["file"]
    if cache.exists():
        data = cache.read_bytes()
    else:
        req = urllib.request.Request(arch["url"], headers={"User-Agent": "arxo-law-dsl/1.0"})
        with urllib.request.urlopen(req, timeout=280) as resp:
            data = resp.read()
        if write_cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(data)
    if len(data) != arch["bytes"]:
        raise SystemExit(f"{arch['name']}: байты {len(data)} != манифест {arch['bytes']}")
    if sha256(data) != arch["sha256"]:
        raise SystemExit(f"{arch['name']}: sha256 не сошёлся с манифестом")
    return data


def read_csv(data: bytes, name: str) -> list[dict]:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        raw = z.read(name).decode("utf-8")
    return list(csv.DictReader(raw.splitlines(), delimiter=";"))


def label(meta_rows: list[dict], var: str, mod: str) -> str:
    for r in meta_rows:
        if r["COD_VAR"] == var and r["COD_MOD"] == mod:
            return r["LIB_MOD"]
    return mod


def extract(write_cache: bool) -> dict:
    out: dict = {"series": []}
    specs = _MANIFEST["series"]
    for spec in specs:
        arch = ARCHIVES[spec["archive"]]
        data = get_bytes(arch, write_cache)
        rows = read_csv(data, spec["data_csv"])
        meta = read_csv(data, spec["meta_csv"])
        filt = spec["filter"]
        points: dict[str, str] = {}
        statuses: dict[str, str] = {}
        for r in rows:
            if any(r.get(k) != v for k, v in filt.items()):
                continue
            t = r["TIME_PERIOD"]
            if t in points:
                raise SystemExit(f"{spec['id']}: дубликат месяца {t}")
            points[t] = r["OBS_VALUE"]
            statuses[t] = r.get("OBS_STATUS", "")
        months = sorted(points)
        if not months:
            raise SystemExit(f"{spec['id']}: пустой ряд — фильтр не matched")
        prov = sorted(t for t in months if statuses[t] not in ("A", "F", ""))
        out["series"].append({
            "id": spec["id"],
            "dataset": spec["archive"],
            "filter": filt,
            "filter_labels_fr": {k: label(meta, k, v) for k, v in filt.items()},
            "base": spec["base"],
            "unit": "indice mensuel brut",
            "first": months[0],
            "last": months[-1],
            "n": len(months),
            "provisional": prov,
            "values": {t: points[t] for t in months},
        })
    return out


def main(argv: list[str]) -> int:
    check = "--check" in argv
    built = extract(write_cache=not check)
    if check:
        committed = json.loads(SERIES_JSON.read_text(encoding="utf-8"))
        if committed != built:
            print("insee-ipc-series.json расходится с байтами архивов")
            return 1
        print(f"OK: рядов {len(built['series'])} — " +
              ", ".join(f"{s['id']} {s['first']}→{s['last']} ({s['n']})" for s in built["series"]))
        return 0
    SERIES_JSON.write_text(json.dumps(built, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"записано {SERIES_JSON}: рядов {len(built['series'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
