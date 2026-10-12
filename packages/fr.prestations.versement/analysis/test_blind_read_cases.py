"""Protocol guard for prestations-versement blind-read cases (W5-VERS).

Blind cases carry inputs only. Any recorded answer ('expected', 'answer',
'value', 'montant', 'result') voids the blindness the file exists for.
Mirrors corpus/laws/fr/smic/analysis/test_blind_read_cases.py.
"""
import json
from pathlib import Path

CASES = Path(__file__).resolve().parent / "blind-read-cases.json"
FORBIDDEN_KEYS = {"expected", "answer", "answers", "value", "montant", "result"}
RELATIONS = {
    "crds_precomptee_af", "montant_net_crds_af",
    "crds_precomptee_cf", "montant_net_crds_cf",
    "crds_precomptee_ars", "montant_net_crds_ars",
    "crds_precomptee_asf_differentiel", "montant_net_crds_asf_differentiel",
    "crds_precomptee_prime", "montant_net_crds_prime",
    "crds_precomptee_cmg_structure", "montant_net_crds_cmg_structure",
    "crds_precomptee_ajpp", "montant_net_crds_ajpp",
    "asf_total_non_verse", "asf_total_verse", "ars_total_verse",
    "dette_recouvrable_af", "taux_effectif_af", "retenue_mensuelle_af", "net_verse_af",
    "net_verse_rsa", "dette_recouvrable_logement", "net_verse_logement",
    "af_net_verse",
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
        assert set(case["probe"]) <= RELATIONS, case
        assert len(case["legal_time"]) == 10, case
        assert case["boundary"], case
        assert case["facts"], case
