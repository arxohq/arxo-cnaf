#!/usr/bin/env python3
"""Fetch DSS instructions (BO Sante) and slice them out of full bulletins.

Three channels, all pinned by SHA-256 in sources/source-manifest.json and in
01-sources.law publications:

1. BO direct (bulletins-officiels.social.gouv.fr, Safari UA): individual
   instruction PDFs for the recent window (dss-2026-46, dss-2025-177).
   Already pinned; this tool only verifies them (--check).

2. Internet Archive id_ snapshots of the full-bulletin PDFs
   (https://sante.gouv.fr/fichiers/bo/YYYY/YYYY.N.sante.pdf): sliced with
   pypdf into per-instruction PDFs (sources/dss-YYYY-NNN.pdf) plus layout
   text (sources/dss-YYYY-NNN.txt, pdftotext -layout). Full bulletins live
   in sources/bo/.cache/ (git-ignored, reproducible via this tool).

3. Internet Archive id_ snapshots of single-instruction PDFs
   (https://sante.gouv.fr/fichiers/bo/YYYY/YY-MM/ste_YYYYMMMM_0000_NNNN.pdf,
   the per-article files of the old BO Sante site): the snapshot is kept whole
   as sources/dss-YYYY-NNN.pdf (no slicing) plus layout text
   sources/dss-YYYY-NNN.txt. Pinned in SINGLES: byte size, SHA-256, the
   Internet Archive CDX digest (base32 SHA-1 of the bytes, checked offline
   against the local file by --check and against the live CDX index by
   --cdx), the NOR (exactly once in the text) and a header marker.

Page ranges were determined once (D-24 reconnaissance): the full-text
header page of the instruction up to the page before the next "NOR :"
occurrence in the bulletin. Boundaries were verified by hand (each slice
starts with its INSTRUCTION header and ends with its annexe; the next
bulletin page starts a new text). See sources/PROVENANCE.md.

Requires: python3 with pypdf (slicing), poppler pdftotext (text).
Network: operator machine only (like every corpus fetch tool).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"}

PKG = Path(__file__).resolve().parent.parent
SOURCES = PKG / "sources"
CACHE = SOURCES / "bo" / ".cache"

# bulletin -> (wayback snapshot ts, official url path, bytes, sha256)
BULLETINS = {
    "2017.4": ("20240327030904", "2017/17-04/ste_20170004_0000_p000.pdf", 11982626,
               "3a2ef6844c7347b32d8ca03a8d6531b12ca3b17c333e08056e20935a918f658a"),
    "2018.1": ("20240403102916", "2018/18-01/ste_20180001_0000_p000.pdf", 12103731,
               "761464b3e8e76600e8148adb03790673d44c11281c5efdc4cbb9fca74245012f"),
    "2019.1": ("20230516134052", "2019/19-01/ste_20190001_0000_p000.pdf", 6010824,
               "367c27c1e6c291a69bd97d53b3a783335db1e084a194ae52e9430fe3e74b22d5"),
    # solidarites-sante.gouv.fr host: the sante.gouv.fr snapshot of 19-04 is truncated
    "2019.4": ("20200306193845",
               "https://solidarites-sante.gouv.fr/fichiers/bo/2019/19-04/ste_20190004_0000_p000.pdf",
               12604050,
               "e85c9cb70ee7bd059d0ce6d1f78951811451e536c31804f4573d2dd330676469"),
    "2021.24": ("20230407184317", "2021/2021.24.sante.pdf", 4088617,
                "13f81c311e803d0904ae7b37ca38973c8d1fb402fc50db0b748b6cc9c68ef58e"),
    "2021.5": ("20240806005418", "2021/2021.5.sante.pdf", 8452274,
               "f4ff369a62171f669c6cc025f22c60e94395129cee5e843fefcf79f27194a6cb"),
    "2022.26": ("20230130162057", "2022/2022.26.sante.pdf", 5248748,
                "d6da7e04ffe75ceaed95dfa5863171d2ff84e3638802c5aca846fbabb5e99c0c"),
    "2022.8": ("20240309145501", "2022/2022.8.sante.pdf", 16653881,
               "9f1adaa4113766f932816dceedff0a719a357d8e3063e07d953da8f2b4dd58f4"),
    "2023.24": ("20231231050117", "2023/2023.24.sante.pdf", 4239194,
                "7c5072aac0ee488dd33b3e4498a8d7e4edf651228a7637376e925d927eb132fd"),
    "2023.6": ("20230331123522", "2023/2023.6.sante.pdf", 6578281,
               "cf80128acc35e9f7525f78bc093dbd0d60531b3a5f032a423db0bab720731797"),
    "2024.34": ("20250117220816", "2024/2024.34.sante.pdf", 6400276,
                "90a1166ea2994e3eb1b039493be0f5611a6f3dcb9d313ca20a7a1f9cc7b628fb"),
    "2024.6": ("20240403124929", "2024/2024.6.sante.pdf", 3406444,
               "bd9ff93203f1c0d4a48907271347b0766806a81017b64317f7dff5bbe6000383"),
    "2025.6": ("20250401012620", "2025/2025.6.sante.pdf", 7288874,
               "9dd8350854c16fe896aa19b1c6fad0410f1040a4c57f9fff691488f8693f2ce2"),
}

# stem -> (bulletin, first_pdf_page, last_pdf_page, pdf_bytes, pdf_sha256,
#           txt_bytes, txt_sha256, header_marker, nor)
SLICES = {
    "dss-2017-97": ("2017.4", 458, 462, 78357,
                    "98357d59d70ed3d9a7d617f5d60905ee7684062b798a5745b38d1854e21d1709",
                    22022, "37193b7938f5be2575111e82de5ce36af4ef7604a28868e7775064913b517ea7", "DSS/SD2B/2017/97", "AFSS1709166C"),
    "dss-2017-352": ("2018.1", 692, 698, 82128,
                    "20638e451ad0d5f58dd36b33254025b07bc664183bd76384875dcd60dc21ee6b",
                    27030, "b94603492e6f287e87a8e68c981683a3f0ca000955b855ebe1aa1eee4ed0b1ee", "DSS/SD2B/2017/352", "SSAS1736497C"),
    "dss-2018-279": ("2019.1", 460, 466, 155040,
                    "1ee88059893865636b2e951fe4b914b257bc9573d23d5bae5d74cd7393c8192d",
                    28543, "ba9e275944845442bc67c771cd475d11282d5422b63738e4063a1d628eaa70f1", "DSS/SD2B/2018/279", "SSAS1834542J"),
    "dss-2019-65": ("2019.4", 355, 361, 90657,
                    "534314a268134154066ac567305165b31afbb598d6b4edc7f268ea4a36ff5362",
                    23629, "88920600cc9deeb9bd09e9b6093e27c6f5c4bf8ee8ddb1e4b2e0f552f136ba28", "DSS/SD2B/2019/65", "SSAS1908955J"),
    "dss-2021-247": ("2021.24", 162, 170, 958380,
                     "f7fa037ac65a127c165c46d5eaf8a3d8813ea12f982ce58f6f2937c577894d0e",
                     29588, "83751230269006af7989a8244b2264e0fea399b1eb64893f1d84f6d8f37402cc",
                     "DSS/2B/2021/247", "SSAS2137492J"),
    "dss-2021-65": ("2021.5", 140, 150, 1007500,
                    "ba3e644635bfe38e74fe1ad42196154c0bb2669631d338439e5f78a198874a42",
                    30022, "fa0697db8f1bbb09fa52f66d8e4f01bc123e4fd0fc724e1fe702c4742621e49a",
                    "DSS/2B/2021/65", "SSAS2108988J"),
    "dss-2022-283": ("2022.26", 171, 180, 935905,
                     "9a014ec3bde4884373df935cb1b34a7427cca35b94a72839551731ca01f2d06c",
                     35343, "1eee3bca6acfefeedb1a1be1afbfdf876590e9381297927fe07d6a26a0cbbfa2",
                     "DSS/SD2B/2022/283", "APHS2237054J"),
    "dss-2022-82": ("2022.8", 404, 413, 908558,
                    "ae121608393a18982ac09971129c219da1e67e712c7c24a46ac73dd27750292b",
                    30444, "8257ed00550d1703f884df4f7de1a00b7571ce6289e41c8fd1dedf52214fc585",
                    "DSS/2B/2022/82", "SSAS2209926J"),
    "dss-2023-205": ("2023.24", 72, 81, 927693,
                     "89da3de4729c84288b1cfda79a8f3347e2d7ae25e40a39b509db5547c5422f19",
                     37769, "a3d4e559096b8bb62b4b06db5a14058e215ae660fc8c6f0bf4c68af37f4d3731",
                     "DSS/2B/2023/205", "FAMS2335370J"),
    "dss-2023-41": ("2023.6", 119, 129, 1940812,
                    "628434c066d9fe27505b1819a9dcb026afe7a921d8e3747dd8ecadb5041f9caa",
                    31105, "89e0b6e620f9977e791d712b2748ce5742ec6fc6709e4fe10bd5a69a44882611",
                    "DSS/2B/2023/41", "APHS2308236J"),
    "dss-2024-181": ("2024.34", 201, 210, 1570712,
                     "123c1510ed3992f7edc532765109e1beda68714c7e4a3aae80b711490829dc13",
                     37918, "4b04ba3dcffcde306a3ad98245b2466a8c7fa7d06bd39490178a5300d5812f73",
                     "DSS/2B/2024/181", "SAES2434195J"),
    "dss-2024-43": ("2024.6", 86, 97, 1286945,
                    "693c0a794cc4cb5ef6aabe43299a41a7df8084b91439f7bbc7d357794f5c80fd",
                    33739, "6705d15c37a1e092b81139ae02dcef894bcdd5426818c6608ab973bd433b8fc4",
                    "DSS/2B/2024/43", "TSSS2408365J"),
    "dss-2025-38": ("2025.6", 27, 38, 907450,
                    "f9018e16b45a8bc3bd0cbc2bc49684ab6a0a625f4d2fdd3a384a7039ded694a0",
                    34255, "bc4a3399b528fd77446a8ec6705aa5abdbffb2eb8f269b2958c4aa5734bf0e84",
                    "DSS/2B/2025/38", "TSSS2508202J"),
}

# Channel 3: stem -> (original url, wayback ts, pdf_bytes, pdf_sha256,
#   txt_bytes, txt_sha256, header_marker, nor, cdx_sha1_base32)
SINGLES: dict[str, tuple] = {
    "dss-2014-345": ("https://sante.gouv.fr/fichiers/bo/2015/15-01/ste_20150001_0000_0061.pdf",
        "20230420072139", 106874,
        "ee1b2da90f055f47e522b9bd753c879857542f4a7c04d83b61318e5fc4bf8b7a",
        21068, "eded869ecb02b74f592bb04dca801f430bef9cb29834ed4ea0fde242f560ee45",
        "2014-345 du 16 décembre 2014", "AFSS1430005C",
        "MQMT6YFNK2TLE3VBCPXWKOJCQQ4GBIM7"),
    "dss-2015-92": ("https://sante.gouv.fr/fichiers/bo/2015/15-04/ste_20150004_0000_0085.pdf",
        "20240702050209", 91406,
        "e790ce3da5e3d2353c5fd4af94e6ecf12c024dc60c0f9852383b78d529ae6df1",
        13703, "ff0d384b6d20b4e2626a9d39587db3d309f27eae900de48bb2f601c639b47db9",
        "2015-92 du 31 mars 2015", "AFSS1507843C",
        "FKS2EWE5OGKQ54K2DAQ44ERB2VIOBNYS"),
    "dss-2016-396": ("https://sante.gouv.fr/fichiers/bo/2017/17-01/ste_20170001_0000_0088.pdf",
        "20240630052908", 121066,
        "5527924f84604b0cfe79e8e53e2d99f8cb4f76ecb1e0e8b14e4836b5cfde0aad",
        23680, "5ada35c7fcc273bf65111bafde50e4cabe06557dc3b144b1758c07599e412d8e",
        "DSS/SD2B/2016/396 du 21 décembre 2016", "AFSS1638099C",
        "VGEP3JQJKBRFAYHDS4ONI4QJHIC5OTTQ"),
    "dss-2016-77": ("https://sante.gouv.fr/fichiers/bo/2016/16-04/ste_20160004_0000_0132.pdf",
        "20240706135050", 122498,
        "194dae53ee3038186ed2561d54fa4a907effd1324a5f692404382edfca927a05",
        22856, "0152d7623b6a3924a9d0f38fe0c4f77ef33d2823b2f1a6074afc559f72e2e5e4",
        "DSS/SD2B/2016/77 du 15 mars 2016", "AFSS1607684C",
        "A6FSKKAJCJO2XR547ZP2IO2CPUHWIAGT"),
    "dss-2019-261": ("https://sante.gouv.fr/fichiers/bo/2019/19-12/ste_20190012_0000_0064.pdf",
        "20250504041933", 224570,
        "0831bf4a407ef50dc5f12a85adf86bc06d361138e3f76938cc7135dc532ce8cc",
        27761, "0fb53c4fb53aaf54ba6ce1dea85a798f24fa854ffce4ddbbc3f3b9144bc9c45b",
        "DSS/SD2B/2019/261 du 18 décembre 2019", "SSAS1936748J",
        "LLCQUBWSVISWONPMDG3OFDJRWU7AXL6I"),
    "dss-2020-226": ("https://sante.gouv.fr/fichiers/bo/2020/20-12/ste_20200012_0000_0050.pdf",
        "20240520154018", 223227,
        "243d4973838b48d6fe353e796d91152570b1dcb11dece161b2575f03ae316822",
        28812, "1fab624eb1b2f5691a5f8f4860b9afc407b5391956d6cfeca76e77664d564590",
        "DSS/2B/DB/2020/226 du 14 décembre 2020", "SSAS2034948J",
        "OEOBBYBHTLCINNPFS5QVG5NWMHYQNSC2"),
    "dss-2020-33": ("https://sante.gouv.fr/fichiers/bo/2020/20-02/ste_20200002_0000_0046.pdf",
        "20230119222325", 255193,
        "33f04ed80bce08012771eee9bd8e6d91393ad20520a16d3605b63c79045588d8",
        35759, "ecca137fe3c55979447244f34eb105c5af624fba99b449a42e1879f5b99588a4",
        "DSS/SD2B/2020/33 du 18 février 2020", "SSAS2005144J",
        "7BJKUZH3ENE6MRUPH53N6LAPY5YZU3SA"),
}

# CDX digests (base32 SHA-1 of the snapshot bytes) of the full bulletins of
# channel 2, keyed by the BULLETINS key. Offline check against the cache.
BULLETIN_CDX_SHA1: dict[str, str] = {
    "2017.4": "U424BVR2ALXF45BBEGMRTYCP2YB2GKOR",
    "2018.1": "3JZOYWF6LNRM2HFBKEAUOJM2MZJI3XWO",
    "2019.1": "4CBPYTHCBF636EXQ62HKIJM7CEARQE3S",
    "2019.4": "ZFQRYLGPHQVLCTFTFPMSOSX77DZ6SR5X",
    "2021.24": "FJ3OYFHBK6YNADTCQL3ZPAC5GC2LHWIP",
    "2021.5": "D7YSWGLYXIVOR6JXETCAV6JQK7HQRASX",
    "2022.26": "63WLKNHMORE3M3MTNTEJGZJ7WYQ4UHLY",
    "2022.8": "R3IQUNNXNQ63Q7DIPRTOHBWQNPLYQPSF",
    "2023.24": "OQQRRYHJG2RPAGZXZL7KJAAEPP5S5QEQ",
    "2023.6": "7UTULN6EE6P35H4MA75BKDSYJIC6JPYA",
    "2024.34": "GHFGGNS4W4HHP6MHXSMGAZJMWKOJSKGP",
    "2024.6": "SF7TD75HCDLFU7H2527ANOFVSZDFYWGO",
    "2025.6": "2OQKEPUJXN6U2UW5GZ5TSP2RQTJOGCV4",
}

# BO-direct pins (fetch channel 1): verified, never re-downloaded here.
DIRECT = {
    "dss-2026-46": ("263198", "5288475881ca40b7ee82e53d8b77bd2767f0051258f39ecb5ce541704b9e0756"),
    "dss-2025-177": ("230195", "a51de9474b15cbc0f746ebf9811c3c0e2f823db1e7e7e2bc34fc985dc730e161"),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_url(bulletin: str) -> str:
    ts, path, _, _ = BULLETINS[bulletin]
    # a path starting with "https://" is a full original URL (another host)
    orig = path if path.startswith("https://") else f"https://sante.gouv.fr/fichiers/bo/{path}"
    return f"https://web.archive.org/web/{ts}id_/{orig}"


def fetch_bulletin(bulletin: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / f"{bulletin}.sante.pdf"
    _, _, want_bytes, want_sha = BULLETINS[bulletin]
    if dest.exists() and dest.stat().st_size == want_bytes and sha256_file(dest) == want_sha:
        print(f"have {dest.name} (hash ok)")
        return dest
    url = snapshot_url(bulletin)
    print(f"fetch {url}")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    got = sha256_file(dest)
    if dest.stat().st_size != want_bytes or got != want_sha:
        raise SystemExit(f"HASH MISMATCH {dest.name}: bytes={dest.stat().st_size} sha={got}")
    print(f"ok {dest.name}")
    return dest


def sha1_b32(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return base64.b32encode(h.digest()).decode()


def cdx_digests(original: str, ts: str) -> list[str]:
    """Digests the Internet Archive CDX index holds for (url, timestamp)."""
    q = ("https://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote(original, safe=":/")
         + f"&output=json&fl=timestamp,digest&from={ts}&to={ts}")
    for attempt in range(6):  # the archive answers 503/504 under load
        try:
            with urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=120) as r:
                rows = json.loads(r.read())
            break
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            print(f"  retry {attempt}: {exc}")
            time.sleep(15 * (attempt + 1))
    else:
        raise SystemExit(f"CDX unavailable for {original}")
    return [row[1] for row in rows[1:] if row[0] == ts]


def fetch_single(stem: str) -> None:
    if shutil.which("pdftotext") is None:
        raise SystemExit("need poppler pdftotext for text extraction")
    original, ts, pdf_bytes, pdf_sha, txt_bytes, txt_sha, marker, nor, cdx_sha1 = SINGLES[stem]
    out_pdf = SOURCES / f"{stem}.pdf"
    if not (out_pdf.exists() and out_pdf.stat().st_size == pdf_bytes and sha256_file(out_pdf) == pdf_sha):
        url = f"https://web.archive.org/web/{ts}id_/{original}"
        print(f"fetch {url}")
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=180) as r, open(out_pdf, "wb") as f:
            shutil.copyfileobj(r, f)
        if out_pdf.stat().st_size != pdf_bytes or sha256_file(out_pdf) != pdf_sha:
            raise SystemExit(f"HASH MISMATCH {out_pdf.name}")
    if sha1_b32(out_pdf) != cdx_sha1:
        raise SystemExit(f"{stem}: SHA-1 differs from the pinned CDX digest")
    out_txt = SOURCES / f"{stem}.txt"
    subprocess.run(["pdftotext", "-layout", str(out_pdf), str(out_txt)], check=True)
    text = out_txt.read_text(encoding="utf-8")
    if marker not in text:
        raise SystemExit(f"{stem}: header marker {marker!r} missing from text")
    if text.count(f"NOR : {nor}") != 1:
        raise SystemExit(f"{stem}: NOR {nor} occurs {text.count(f'NOR : {nor}')}x, want exactly 1")
    if sha256_file(out_txt) != txt_sha:
        print(f"WARN {stem}: text bytes differ from committed (poppler version drift?)")
    else:
        print(f"ok {stem}.pdf/.txt (hash ok)")


def slice_and_extract(stem: str, bulletin_path: Path) -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        raise SystemExit("need pypdf for slicing (pip install pypdf)")
    if shutil.which("pdftotext") is None:
        raise SystemExit("need poppler pdftotext for text extraction")
    bulletin, first, last, pdf_bytes, pdf_sha, txt_bytes, txt_sha, marker, nor = SLICES[stem]
    reader = PdfReader(str(bulletin_path))
    writer = PdfWriter()
    for i in range(first - 1, last):
        writer.add_page(reader.pages[i])
    out_pdf = SOURCES / f"{stem}.pdf"
    with open(out_pdf, "wb") as f:
        writer.write(f)
    out_txt = SOURCES / f"{stem}.txt"
    subprocess.run(["pdftotext", "-layout", str(out_pdf), str(out_txt)], check=True)
    text = out_txt.read_text(encoding="utf-8")
    if marker not in text:
        raise SystemExit(f"{stem}: header marker {marker!r} missing from slice text")
    if text.count(f"NOR : {nor}") != 1:
        raise SystemExit(f"{stem}: NOR {nor} occurs {text.count(nor)}x, want exactly 1")
    got_pdf, got_txt = sha256_file(out_pdf), sha256_file(out_txt)
    # pypdf output bytes depend on the pypdf version; the committed slices
    # were cut with pypdf 6.14.2. A mismatch here means re-cut, not corruption.
    if got_pdf != pdf_sha or got_txt != txt_sha:
        print(f"WARN {stem}: slice bytes differ from committed (pypdf/poppler version drift?)")
        print(f"  pdf: got {got_pdf} want {pdf_sha}")
        print(f"  txt: got {got_txt} want {txt_sha}")
    else:
        print(f"ok {stem}.pdf/.txt (hash ok)")


def check() -> int:
    fails = 0
    for stem, (bulletin, *_rest) in SLICES.items():
        for suffix, want in ((".pdf", SLICES[stem][4]), (".txt", SLICES[stem][6])):
            p = SOURCES / f"{stem}{suffix}"
            if not p.exists():
                print(f"MISSING {p.name}");
                fails += 1
                continue
            got = sha256_file(p)
            if got != want:
                print(f"MISMATCH {p.name}: got {got} want {want}");
                fails += 1
    for stem, row in SINGLES.items():
        pdf_bytes, pdf_sha, txt_sha, cdx_sha1 = row[2], row[3], row[5], row[8]
        for suffix, want in ((".pdf", pdf_sha), (".txt", txt_sha)):
            p = SOURCES / f"{stem}{suffix}"
            if not p.exists():
                print(f"MISSING {p.name}")
                fails += 1
            elif sha256_file(p) != want:
                print(f"MISMATCH {p.name}")
                fails += 1
        p = SOURCES / f"{stem}.pdf"
        if p.exists() and (p.stat().st_size != pdf_bytes or sha1_b32(p) != cdx_sha1):
            print(f"MISMATCH {p.name}: size or CDX SHA-1")
            fails += 1
        txt = SOURCES / f"{stem}.txt"
        if txt.exists():
            text = txt.read_text(encoding="utf-8")
            if text.count(f"NOR : {row[7]}") != 1 or row[6] not in text:
                print(f"MISMATCH {txt.name}: NOR/header marker")
                fails += 1
    for stem, (want_bytes, want_sha) in DIRECT.items():
        p = SOURCES / f"{stem}.pdf"
        if not p.exists() or sha256_file(p) != want_sha:
            print(f"MISMATCH {stem}.pdf");
            fails += 1
    cached = sorted(p.name for p in CACHE.glob("*.sante.pdf")) if CACHE.exists() else []
    for name in cached:
        bulletin = name.removesuffix(".sante.pdf")
        if bulletin in BULLETINS and sha256_file(CACHE / name) != BULLETINS[bulletin][3]:
            print(f"MISMATCH cache/{name}");
            fails += 1
        elif bulletin in BULLETIN_CDX_SHA1 and sha1_b32(CACHE / name) != BULLETIN_CDX_SHA1[bulletin]:
            print(f"MISMATCH cache/{name}: SHA-1 vs CDX digest")
            fails += 1
    print("check: " + ("OK" if fails == 0 else f"{fails} FAILURES"))
    return 1 if fails else 0


def check_cdx() -> int:
    """Network: compare every pinned SHA-1 with the live CDX index."""
    fails = 0
    items = [(f"single {k}", v[0], v[1], v[8]) for k, v in SINGLES.items()]
    for key, sha1 in BULLETIN_CDX_SHA1.items():
        ts, path = BULLETINS[key][0], BULLETINS[key][1]
        orig = path if path.startswith("https://") else f"https://sante.gouv.fr/fichiers/bo/{path}"
        items.append((f"bulletin {key}", orig, ts, sha1))
    for label, original, ts, sha1 in items:
        got = cdx_digests(original, ts)
        status = "ok" if sha1 in got else "MISMATCH"
        fails += status != "ok"
        print(f"{status} {label}: pinned {sha1} CDX {got}")
    print("cdx: " + ("OK" if fails == 0 else f"{fails} FAILURES"))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify committed hashes only")
    ap.add_argument("--cdx", action="store_true", help="compare pinned SHA-1 with the live Internet Archive CDX index")
    ap.add_argument("--only", default="", help="fetch one stem (e.g. dss-2024-43 or dss-2015-92)")
    args = ap.parse_args()
    if args.check:
        return check()
    if args.cdx:
        return check_cdx()
    stems = [args.only] if args.only else sorted(SLICES) + sorted(SINGLES)
    for stem in stems:
        if stem in SINGLES:
            fetch_single(stem)
        elif stem in SLICES:
            path = fetch_bulletin(SLICES[stem][0])
            slice_and_extract(stem, path)
        else:
            raise SystemExit(f"unknown stem {stem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
