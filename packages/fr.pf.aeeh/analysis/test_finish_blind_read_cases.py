"""Protocol guard for pf-aeeh finish-wave blind-read cases (pfaeeh-finish-01..24).

Blind cases carry inputs only. Any recorded answer ('expected', 'answer',
'value', 'montant') voids the blindness the file exists for. Mirrors
test_blind_read_cases.py; the probed relations are the R541 finish-wave
heads and positions.
"""
import json
from pathlib import Path

CASES = Path(__file__).resolve().parent / "finish-blind-read-cases.json"
FORBIDDEN_KEYS = {"expected", "answer", "answers", "value", "montant", "result"}
RELATIONS = {
    "seuil_80_atteint",
    "seuil_50_atteint",
    "tranche_50_80",
    "prise_en_charge_reconnue",
    "modalite_versement_annuel",
    "categorie1_criteres_remplis",
    "categorie2_criteres_remplis",
    "categorie3a_criteres_remplis",
    "categorie3b_criteres_remplis",
    "categorie3c_criteres_remplis",
    "categorie4a_criteres_remplis",
    "categorie4b_criteres_remplis",
    "categorie4c_criteres_remplis",
    "categorie4d_criteres_remplis",
    "categorie5_criteres_remplis",
    "categorie6_criteres_remplis",
    "demande_complete",
    "charges_pch_exclues_complement",
    "bornes_duree_attribution",
    "fin_exclusive_droit",
    "date_limite_reexamen",
    "reexamen_en_retard",
    "date_rejet_implicite",
    "rejet_implicite",
    "date_debut_droit",
    "date_fin_suppression",
    "aeeh_condition_r512_2",
    "date_fin_complement_pch",
    "date_assimilation_hospitalisation",
    "assimile_internat",
    "date_fin_prolongation_deces",
    "montant_prolongation_deces",
    "JoindrePiecesDemande",
    "TransmettreDossierMDPH",
    "DeposerDemandePCH",
    "ReviserDecisionPCH",
    "ReexaminerComplementPCH",
    "OpterComplementAvantEcheance",
    "DemanderRevisionBeneficiaire",
    "DemanderRevisionOrganisme",
    "ReexaminerAggravation",
    "ControlerEffectivite",
    "SaisirCommission",
    "VerserAvanceComplement",
    "StatuerUrgence",
    "ReexaminerMesures",
    "SuspendreComplementPCH",
    "RetablirComplementRetroactif",
    "MaintenirVersementHospitalisation",
}
BOUNDARIES = {
    "core",
    "B-PFAEEH-GUIDE-BAREME",
    "B-PFAEEH-SEUILS-ARRETE",
    "B-PFAEEH-GUIDE-EVALUATION",
    "B-PFAEEH-TEMPS-PLEIN",
    "B-PFAEEH-MODELE-ARRETE",
    "B-PFAEEH-DELAI-URGENCE",
    "B-PFAEEH-PCH-MECANIQUE",
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
