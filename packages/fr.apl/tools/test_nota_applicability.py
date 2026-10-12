"""NOTA applicability wordings are data with a test (3b).

The window axis of the bareme is the applicability date (``applies_from``),
which the version's own NOTA states ("applicables aux prestations dues à
compter du …"). This test pins the invariant over all pinned versions in
``sources/fr-apl/articles.json``: a version whose applicability differs from
its force window MUST carry the NOTA saying so, and the known reform wordings
must name their exact applicability.
"""
import json
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1] / "sources" / "fr-apl" / "articles.json"


def versions():
    book = json.loads(BOOK.read_text(encoding="utf-8"))
    for edition in book["editions"]:
        for article, row in edition["versions"].items():
            yield edition["document"], article, row


def test_applicability_gap_requires_nota():
    bare = [(d, a) for d, a, v in versions()
            if v.get("applies_from") != v.get("in_force_from") and not v.get("nota")]
    assert bare == [], f"applicability without NOTA wording: {bare[:5]}"


def test_nota_wording_preserved_verbatim():
    # NOTA also fires when the dates coincide: it then names the enabler or
    # the version's own history instead of a gap. Either way the wording is
    # data, kept verbatim, and the window builder must read it, not drop it.
    by_key = {(d, a): v for d, a, v in versions()}

    art7 = by_key[("arrete-2023-01.txt", "7")]
    assert art7["applies_from"] == art7["in_force_from"] == "2022-07-01"
    assert "TREL2220744A" in art7["nota"]
    assert "1er juillet 2022" in art7["nota"]

    rls = by_key[("cch.txt", "L442-2-1")]
    assert rls["applies_from"] == rls["in_force_from"]
    assert "2017-1837" in rls["nota"]


def test_reform_wordings():
    by_key = {(d, a): v for d, a, v in versions()}

    r822 = by_key[("cch-2021-01.txt", "R822-2")]
    assert r822["applies_from"] == "2021-01-01"
    assert "2019-1574" in r822["nota"] and "article 25" in r822["nota"]

    d823 = by_key[("cch-2021-01.txt", "D823-17")]
    assert d823["applies_from"] == "2021-01-01"
    assert "2019-1574" in d823["nota"]
