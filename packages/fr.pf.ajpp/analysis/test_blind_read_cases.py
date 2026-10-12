"""Protocol guard for pf-ajpp blind-read cases (P.4).

Blind cases carry inputs only. Any recorded answer ('expected', 'answer',
'value', 'montant') voids the blindness the file exists for.
"""
import json
from pathlib import Path

CASES = Path(__file__).resolve().parent / "blind-read-cases.json"
FORBIDDEN_KEYS = {"expected", "answer", "answers", "value", "montant", "result"}
RELATIONS = {
    "ajpp_droit_ouvert",
    "reexamen_conforme",
    "ajpp_dans_limite",
    "renouvellement_accorde",
    "droit_rouvert",
    "avance_accordee",
    "mensuel_dans_limite",
    "ajpp_montant_mois",
    "complement_frais_attribue",
    "ajpp_montant_complement",
    "ajpp_cumul_refuse",
    "activite_partielle_cumulee",
    "InformerDemandeurAjpp",
    # FINISH ajpp-death decree heads (probe surface only; cases and
    # answers belong to the independent blind reader Luna).
    "ajpp_duree_dans_limite",
    "duree_maximale_expiree",
    "droit_nouvelle_pathologie",
    "echeance_reexamen_mois",
    "delai_demande_reexamen",
    "reexamen_demande_recevable",
    "droit_renouvele_reexamen",
    "mois_depuis_ouverture",
    "reouverture_dans_delai",
    "versement_sans_attendre_fin_max",
    "versement_au_dela_max",
    "taux_journalier_calcule",
    "taux_tie_en_attente",
    "taux_demi_journee_calcule",
    "taux_journalier_2021",
    "taux_demi_journee_2021",
    "statut_chomeur_l5421",
    "seuil_complement_calcule",
    "forfait_22_conforme",
    "exception_forfait_l544_1",
    "dossier_demande_complet",
    "dossier_reexamen_complet",
    "dossier_renouvellement_complet",
    "controle_medical_competent",
    "mois_silence_ecoules",
    "avis_silence_repute_favorable",
    "decision_silence_reputee_favorable",
    "avis_silence_repute_defavorable",
    "decision_silence_rejet",
    "jours_pris_declares_ft",
    "attestation_conge_employeur_transmise",
    "attestation_formateur_transmise",
    "declaration_cessation_recherche_transmise",
    "declaration_interruption_activite_transmise",
    "attestation_agent_public_transmise",
    "declaration_depenses_transmise",
    "pieces_depenses_produites",
    "avis_renouvellement_notifie",
    "DeclarerJoursPrisFT",
    "TransmettreAttestationConge",
    "TransmettreAttestationFormateur",
    "TransmettreDeclarationCessation",
    "TransmettreDeclarationInterruption",
    "TransmettreAttestationAgentPublic",
    "DeclarerDepensesComplement",
    "ProduirePiecesDepenses",
    "NotifierAvisRenouvellement",
    "ajpp_attribution_l751",
    "enveloppe_ajpp_qualifiee",
}
BOUNDARIES = {
    "core",
    "B-PFAJPP-D544",
    "B-PFAJPP-DUREE",
    "B-PFAJPP-PARTAGE",
    "B-PFAJPP-L544-1-EXCEPTION",
    "B-PFAJPP-SILENCE-RENOUVELLEMENT-AVANT-2022",
    "B-PFAJPP-BMAF-FIGURE",
    "B-PFAJPP-SHN-NET",
    "B-PFAJPP-CRDS-TAUX",
    "B-PFAJPP-FORMULE-DIVISION",
    "B-PFAJPP-TIE-ARRONDI",
    "B-PFAJPP-DOM-L751",
    "B-PFAJPP-ENVELOPPE-QUALIFIEE",
    "B-PFAJPP-DEMI-PLAFOND",
    "B-PFAJPP-ROUVERTURE-COMPTEUR",
    "B-PFAJPP-NOUVELLE-PATHOLOGIE-COMPTEUR",
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
