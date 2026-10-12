"""Protocol guard for pf-ars blind-read cases.

Blind cases carry inputs only. Any recorded answer ('expected', 'answer',
'value', 'montant') voids the blindness the file exists for.
"""
import json
from pathlib import Path

CASES = Path(__file__).resolve().parent / "blind-read-cases.json"
FORBIDDEN_KEYS = {"expected", "answer", "answers", "value", "montant", "result"}
RELATIONS = {
    "ars_enfant_eligible",
    "ars_droit_ouvert",
    "plafond_ars_applicable",
    "ars_montant_du",
    "ars_differentiel_du",
    "ars_paiement_cdc",
    "ars_paiement_famille",
    "ars_verse",
    "DevoirVerserArs",
    "DevoirVerserArsDifferentiel",
}
BOUNDARIES = {
    "core",
    "B-PFARS-SEUIL",
    "B-PFARS-SITUATION",
    "B-PFARS-CDC-PROC",
}


def load():
    return json.loads(CASES.read_text(encoding="utf-8"))


def test_case_count_in_range():
    cases = load()["cases"]
    assert 20 <= len(cases) <= 30, len(cases)


def test_no_answers_recorded():
    def walk(node):
        if isinstance(node, dict):
            for key, val in node.items():
                assert key not in FORBIDDEN_KEYS, f"answer leaked under key {key!r}"
                walk(val)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(load())


def test_inputs_well_formed():
    cases = load()["cases"]
    ids = [c["id"] for c in cases]
    assert len(set(ids)) == len(ids), "duplicate case ids"
    for case in cases:
        assert case["boundary"] in BOUNDARIES, case
        assert set(case["probe"]) <= RELATIONS, case
        assert len(case["legal_time"]) == 10, case
        assert case["facts"], case
        assert case["family"], case
