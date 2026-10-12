#!/usr/bin/env python3
'''Restore pinned source bytes that this repository does not redistribute.

WITHHELD.json lists them: the publisher's terms do not allow republishing, so
each package keeps only the address and the sha256 in its sources.law. This
script downloads every file from its address and checks the hash; a text
extracted from a PDF is rebuilt with `pdftotext -layout` (poppler) and checked
the same way. A file that does not match is refused, never kept.

    python3 tools/fetch_withheld.py            # everything listed
    python3 tools/fetch_withheld.py fr.pf.af   # one package
'''
import hashlib, json, pathlib, shutil, subprocess, sys, tempfile, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> int:
    entries = json.loads((ROOT / "WITHHELD.json").read_text(encoding="utf-8"))["files"]
    only = set(sys.argv[1:])
    failed = 0
    for entry in sorted(entries, key=lambda e: e.get("extract") is not None):
        if only and entry["package"] not in only:
            continue
        target = ROOT / "packages" / entry["package"] / entry["path"]
        if target.is_file() and sha256(target.read_bytes()) == entry["content_hash"]:
            continue
        if entry.get("extract"):
            source = ROOT / "packages" / entry["package"] / entry["from"]
            if shutil.which("pdftotext") is None:
                print(f"{entry['path']}: pdftotext (poppler) is required", file=sys.stderr)
                failed += 1
                continue
            with tempfile.TemporaryDirectory() as tmp:
                out = pathlib.Path(tmp) / "text.txt"
                subprocess.run(["pdftotext", "-layout", str(source), str(out)], check=True)
                data = out.read_bytes()
        else:
            request = urllib.request.Request(entry["uri"], headers={"User-Agent": "Mozilla/5.0 (law fetch_withheld)"})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
        if sha256(data) != entry["content_hash"]:
            print(f"{entry['package']}/{entry['path']}: got {sha256(data)}, pinned {entry['content_hash']}"
                  + (f" (pinned with {entry['tool']})" if entry.get("tool") else ""), file=sys.stderr)
            failed += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print(f"restored {entry['package']}/{entry['path']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
