"""Перенос формульных дел OpenFisca-France 176.1.2 в fr.apl (corpus/tools/foreign/openfisca_formulas.py).

Исполняется в их venv. Из их прогона берутся ФАКТЫ дела — их промежуточные
величины: зона, состав семьи, иждивенцы, база ресурсов, наём, RLS, территория,
вид пособия. Ни одно их нормативное число (барем, ставка, плафон) в пакет не
попадает: барем — только наш закреплённый (`bareme/`, `sources/`).

Отображение повторяет таблицу `tools/foreign-map.json` (раздел "openfisca") и
прежний конвертер `corpus/tools/foreign/openfisca_tests.py`; отличие — дела
выбирает реестр временного охвата, а не перебор файлов.
"""
from __future__ import annotations

# Точная дробь оракула (`161/10000`) разбирается в corpus/tools/foreign/common.py (_exact).

PACKAGE = {"package": "fr.apl", "version": "0.1.0", "namespace": "urn:fr:corpus:clir:apl",
           "prefix": "fr-apl", "timezone": "Europe/Paris", "world": ["fr.apl"], "resolve": ["fr.apl"],
           # G-A13: денежный конус требует выбора рабочего прочтения Pp (24-lecture-pp.law).
           # D-82 (08.10.2026): неточное деление без политики в тексте округляется до сантима
           # HALF_UP — прочтение ArrondiCentimeHalfUp (27-lecture-arrondi-centime.law, практика
           # CNAF, не текст): пропорция D. 823-16 и E0 «divisé par douze» D. 832-26. Без выбора
           # эти два места отвечали отказом INEXACT_DIVISION (классом (а)).
           "context": "interpretation PpPlancherFinal; interpretation ArrondiCentimeHalfUp;"}

# D-85 (09.10.2026): вторая проба драйвера «без наших прочтений» (класс РАВНО_ПО_ПРОЧТЕНИЮ)
# сохраняет PpPlancherFinal: группа SensMinimumPp — exactly_one (24-lecture-pp.law), без
# выбора денежный конус отвечает INTERPRETATION_REQUIRED. Снимается только ArrondiCentimeHalfUp.
REQUIRED_INTERPRETATIONS = ("PpPlancherFinal",)

# Их `aide_logement` (= apl + als + alf = `aide_logement_montant`) — сумма «net de CRDS»:
# `round_(aide_logement_montant_brut_crds + crds_logement, 2)`. Наша та же стадия —
# `aide_nette_precompte_crds` (26-precompte-crds.law: пособие D. 823-16 после
# удержания CRDS по ст. 14 III и 19 ордонанса № 96-50), а не `aide_mensuelle`
# (сумма пособия с представительной суммой взносов): иначе сравнивались бы разные
# стадии (аудит 14.09.2026).
TARGETS = {
    "aide_logement": {"predicate": "aide_nette_precompte_crds", "kind": "Money"},
    "aide_logement_montant": {"predicate": "aide_nette_precompte_crds", "kind": "Money"},
    # D-85 (09.10.2026): их `apl`, `als`, `alf` — то же `aide_logement_montant` (net de CRDS),
    # умноженное на признак вида (конвенция жилья; иждивенцы 0 / ≥ 1; не proprietaire_proche_
    # famille): стадия та же, что у aide_logement, — наша `aide_nette_precompte_crds`. Цель
    # вида, отличного от вида дела (`_aid_kind`), не переносится (`skip_target`): наш предикат
    # не разделён по видам, вид задаёт факт aide_demandee.
    "apl": {"predicate": "aide_nette_precompte_crds", "kind": "Money"},
    "als": {"predicate": "aide_nette_precompte_crds", "kind": "Money"},
    "alf": {"predicate": "aide_nette_precompte_crds", "kind": "Money"},
    "aide_logement_loyer_plafond": {"predicate": "plafond_loyer", "kind": "Money"},
    "aide_logement_charges": {"predicate": "forfait_charges", "kind": "Money"},
    "aide_logement_R0": {"predicate": "abattement_r0", "kind": "Money"},
    "aide_logement_participation_minimale": {"predicate": "participation_minimale", "kind": "Money"},
    "aide_logement_taux_famille": {"predicate": "taux_composition_familiale", "kind": "Decimal"},
    "aide_logement_participation_personnelle": {"predicate": "participation_personnelle", "kind": "Money"},
    "al_nb_personnes_a_charge": {"predicate": "personnes_a_charge_retenues", "kind": "Integer"},
    # Промежуточные шаги дела «Personne isolée 2026-08» (их выходы-формулы).
    "aide_logement_taux_loyer": {"predicate": "taux_loyer_eligible", "kind": "Decimal"},
    "aide_logement_taux_participation_personnelle": {"predicate": "taux_participation", "kind": "Decimal"},
    # Их «après dégressivité et abattement forfaitaire, avant CRDS» = наш шаг после минорации.
    "aide_logement_montant_brut": {"predicate": "aide_apres_minoration", "kind": "Money"},
    # Их «brut de CRDS» после вычета 98 % RLS = наш шаг после RLS (вилка взносов D. 823-16 уже пройдена).
    "aide_logement_montant_brut_crds": {"predicate": "aide_apres_rls", "kind": "Money"},
}

SECTOR_BY_STATUT = {
    "locataire_vide": "secteur_locatif",
    "locataire_meuble": "secteur_locatif",
    "locataire_hlm": "secteur_locatif",
    "non_renseigne": "secteur_locatif",
}
ZONE = {"zone_1": "ZONE_I", "zone_2": "ZONE_II", "zone_3": "ZONE_III"}


def skip_target(ctx, variable: str) -> str | None:
    """Их apl/als/alf — одно пособие дела под тремя именами: переносится вид дела.

    Когда у них все три нулевые, вид не определён — переносится каждая выведенная цель
    (сверка «нет выплаты у обоих»)."""
    if variable not in ("apl", "als", "alf"):
        return None
    if not any(float(ctx.value(name)) for name in ("apl", "als", "alf")):
        # У них нет выплаты ни по одному виду: сверяется «нет выплаты» и у этой цели.
        return None
    kind = _aid_kind(ctx)
    if variable.upper() == kind:
        return None
    return (f"их {variable} — вид пособия, не назначенный делу: вид дела {kind} (их apl/als/alf = "
            f"aide_logement_montant × признак вида; их {variable} = {float(ctx.value(variable)):.2f}); "
            "наша aide_nette_precompte_crds по виду не разделена — сверяется цель вида дела")


def members(ctx, key: str) -> list[str]:
    return list(ctx.item["input"].get("famille", {}).get(key) or [])


def money(value) -> str:
    return f"{float(value):.2f} EUR"


def facts(ctx) -> list[str]:
    statut = ctx.value("statut_occupation_logement")
    if statut == "locataire_foyer" or ctx.value("logement_crous"):
        # D. 823-9 2°/3°: logement-foyer и комнаты CROUS считаются по R. 832-20…D. 832-28 /
        # D. 842-15…D. 842-18, « Af = K × (E − E0) » и « Af = K × (L + C − L0) ». Алгебру K
        # пакет читает из отменённых R. 351-61 и R. 351-61-1 (04-calcul-foyer.law,
        # README, «Коэффициент K»): картинки D. 832-25 в закреплённых данных не прочесть.
        return _foyer(ctx)
    sector = SECTOR_BY_STATUT.get(statut)
    if sector is None:
        raise ctx.Skip(f"статус жилья {statut}: перенос из их фактов заведён только для найма")
    kind = _aid_kind(ctx)
    zone = ZONE.get(ctx.value("zone_apl"))
    if zone is None:
        raise ctx.Skip(f"зона {ctx.value('zone_apl')} не I/II/III")
    territoire = _territoire(ctx)
    aah = any(float(v) > 0 for v in ctx.values("aah")) or float(ctx.value("aeeh")) > 0
    return _common(ctx, sector, kind, zone, territoire, aah)


def _aid_kind(ctx) -> str:
    aid = {name: float(ctx.value(name)) for name in ("apl", "alf", "als")}
    if any(aid.values()):
        return max(aid, key=aid.get).upper()
    # Все три вида у них нулевые: вид — по конвенции жилья (их же признак).
    return "APL" if ctx.value("logement_conventionne") else "ALF"


def _territoire(ctx) -> str:
    if ctx.value("residence_saint_pierre_et_miquelon"):
        return "SAINT_PIERRE_ET_MIQUELON"
    if ctx.value("residence_aides_logement_outre_mer"):
        return "OUTRE_MER"
    return "METROPOLE"


def _foyer(ctx) -> list[str]:
    """Факты сектора logement-foyer / комната CROUS: их промежуточные величины.

    Тип фойе и категория D. 842-16 — не наши суждения, а то, что их код выбрал для дела:
    у конвенционированного фойе их `aides_logement_k` берёт параметры общего случая (apl1);
    у неконвенционированного плафон L их код берёт по `aides_logement_foyer_plafond_mensualite`:
    возраст ≥ 62 лет — « personnes âgées », CROUS-комната без реабилитации — « étudiants en
    chambre », иначе « étudiants en chambre réhabilitée »."""
    zone = ZONE.get(ctx.value("zone_apl"))
    if zone is None:
        raise ctx.Skip(f"зона {ctx.value('zone_apl')} не I/II/III")
    kind = _aid_kind(ctx)
    atoms = ["secteur_logement_foyer({main})", f"aide_demandee({{main}}, {kind})",
             f"zone_du_logement({{main}}, {zone})",
             f"situation_familiale({{main}}, {'COUPLE' if ctx.value('al_couple') else 'PERSONNE_SEULE'})",
             f"personnes_a_charge({{main}}, {_pac(ctx)})"]
    if ctx.value("logement_conventionne"):
        atoms.append("type_logement_foyer({main}, GENERAL)")
    else:
        if int(ctx.value("age")) >= 62:
            category = "PERSONNES_AGEES"
        elif ctx.value("logement_crous") and ctx.value("logement_chambre") \
                and ctx.value("etat_logement_foyer") == "logement_non_rehabilite":
            category = "ETUDIANT_CHAMBRE"
        else:
            category = "ETUDIANT_CHAMBRE_REHABILITEE"
        atoms.append(f"categorie_equivalence_loyer({{main}}, {category})")
    atoms += [f"redevance({{main}}, {money(ctx.value('loyer'))})",
              f"ressources_du_menage({{main}}, {money(ctx.value('aide_logement_base_ressources'))})",
              f"territoire({{main}}, {_territoire(ctx)})"]
    return atoms


def _pac(ctx) -> int:
    """Иждивенцы ДО ограничения: наш факт — число лиц, ограничение шестью (DOM до 2023)
    считает пакет (`personnes_a_charge_retenues`). Их `al_nb_personnes_a_charge` уже
    ограничен (`min_(nb_pac, 6)` при `residence_dom` и году < 2023); где он упёрся в
    шесть, берётся число детей семьи из их же дела."""
    retained = int(ctx.value("al_nb_personnes_a_charge"))
    if ctx.value("residence_dom") and int(ctx.period[:4]) < 2023 and retained == 6:
        return max(retained, len(members(ctx, "enfants")))
    return retained


def _common(ctx, sector, kind, zone, territoire, aah) -> list[str]:
    return [
        f"{sector}({{main}})",
        f"aide_demandee({{main}}, {kind})",
        f"zone_du_logement({{main}}, {zone})",
        f"situation_familiale({{main}}, {'COUPLE' if ctx.value('al_couple') else 'PERSONNE_SEULE'})",
        f"personnes_a_charge({{main}}, {_pac(ctx)})",
        f"ressources_du_menage({{main}}, {money(ctx.value('aide_logement_base_ressources'))})",
        # D-85: меблированный наём — цена фактом prix_paye_logement_meuble, loyer principal
        # (две трети, D. 842-2 / D. 823-18) выводит пакет (28-loyer-meuble.law).
        (f"prix_paye_logement_meuble({{main}}, {money(ctx.value('loyer'))})"
         if ctx.value("statut_occupation_logement") == "locataire_meuble"
         else f"loyer_principal({{main}}, {money(ctx.value('loyer'))})"),
        f"mode_location({{main}}, {'COLOCATION' if ctx.value('coloc') else 'LOCATION_SEULE'})",
        f"reduction_loyer_solidarite({{main}}, {money(ctx.value('reduction_loyer_solidarite'))})",
        f"territoire({{main}}, {territoire})",
        "forme_logement({main}, LOGEMENT_ORDINAIRE)",
        f"beneficiaire_aah_ou_aeeh({{main}}, {'true' if aah else 'false'})",
    ]


# ---------------------------------------------------------------- квалификация
#
# Сверено 08.10.2026 по стадиям (scratch-сверка обоих прогонов): у всех дел найма
# плафон L, форфейт C, P0, TF, TL, R0, Pp и Af совпадают с их кодом до float32,
# кроме дела Cas 5 (наём 214,38 € у них округлён до 214 €). Расходится ПОСЛЕДНИЙ
# шаг D. 823-16. Реплика их чтения на НАШИХ закреплённых числах (барем пакета,
# `tools/compare_openfisca.py`, `chain(..., reading="openfisca")`)
#   их = round2((max(0, round2(Af) − 5) − 0,98 × RLS) × (1 − 0,005))
# воспроизводит их число до цента во всех 18 делах; наше по тексту
#   наше = (⌊A − c⌋ + c − 0,98 × RLS) × (1 − 0,005),  A = Af − 5,  c = 0,5 % × A.
_D823_16 = ("D. 823-16 (sources/fr-apl/cch-2021-01.txt:57): « Le montant qui en résulte est diminué "
            "d'un montant représentatif des contributions sociales qui s'y appliquent, arrondi à "
            "l'euro inférieur, puis majoré de ce montant représentatif »; их код "
            "(aide_logement_montant_brut → _brut_crds → aide_logement_montant) округления к "
            "нижнему евро не делает, зато округляет Af до сантима (round_(…, 2) — текст не велит)")
_REPLICA = ("реплика их чтения round2((max(0, round2(Af) − 5) − 0,98·RLS) × 0,995) на нашем "
            "бареме даёт {theirs} = их код; наше (⌊A − c⌋ + c − 0,98·RLS) × 0,995 = {ours}")

# дело → (их код, наше, Af, A = Af − 5, потеря ⌊A − c⌋, RLS, примечание)
_CASES = {
    "of176-aides-logement-reforme-janvier-2021-00": ("254.93", "254.00464475", "261.21", "256.21", "0.92895", "0", ""),
    "of176-aides-logement-reforme-janvier-2021-02": ("100.73", "100.003663826", "106.23896", "101.23896", "0.7327652", "0", ""),
    "of176-aides-logement-reforme-janvier-2021-03": ("53.60", "53.00300250375", "58.86985", "53.86985", "0.60050075", "0", ""),
    "of176-aides-logement-reforme-janvier-2021-04": (
        "214.24", "214.003066307", "220.69172", "215.69172", "0.6132614", "0",
        "; второе отличие — наём: D. 823-16 2° « L est le loyer éligible, correspondant au loyer "
        "principal pris en compte dans la limite d'un plafond » (там же) округления не знает, их "
        "aide_logement_loyer_reel = round_(loyer) даёт L = 214 вместо 214,38 € → TL 0,00187 вместо "
        "0,00189, Af 220,31994 вместо 220,69172"),
    "of176-aides-logement-reforme-janvier-2021-05": ("11.51", "11.002565526", "16.57096", "11.57096", "0.5131052", "0", ""),
    "of176-aides-logement-reforme-janvier-2021-06": ("195.86", "195.6954261985", "252.40406", "247.40406", "0.1670397", "51.59", ""),
    "of176-aides-logement-reforme-janvier-2021-07": ("417.28", "416.8672770625", "502.8975", "497.8975", "0.4080125", "80.13", ""),
    "of176-aides-logement-reforme-janvier-2021-09": ("220.79", "220.003971405", "226.9038", "221.9038", "0.794281", "0", ""),
    "of176-aides-logement-reforme-janvier-2021-11": ("174.01", "174.00002203", "179.8788", "174.8788", "0.004406", "0", ""),
    "of176-aides-logement-etudiant-00": ("220.79", "220.003971405", "226.9038", "221.9038", "0.794281", "0", ""),
    "of176-aides-logement-etudiant-02": ("379.70", "379.00353437625", "386.61495", "381.61495", "0.70687525", "0", ""),
    "of176-aides-logement-personnes-agees-et-invalides-00": ("103.81", "103.004046526", "109.33096", "104.33096", "0.8093052", "0", ""),
    "of176-aides-logement-personnes-agees-et-invalides-01": ("156.11", "156.000552426", "161.89496", "156.89496", "0.1104852", "0", ""),
    "of176-aides-logement-personnes-agees-et-invalides-02": ("143.81", "143.004021626", "149.52696", "144.52696", "0.8043252", "0", ""),
    "of176-aides-logement-personnes-agees-et-invalides-03": ("258.22", "258.001130905", "264.5238", "259.5238", "0.226181", "0", ""),
    "of176-aides-logement-21": ("43.53", "42.90927027625", "84.01895", "79.01895", "0.62385525", "35.99",
                                "; их же файл пишет формулу round(43.7498 × (1 − 0.005), 2) — 43,7498 = 79,02 − 0,98 × 35,99 "
                                "без шага к нижнему евро"),
}

QUALIFIED = {}
for _case, (_theirs, _ours, _af, _a, _loss, _rls, _note) in _CASES.items():
    _target = "aide_logement_montant" if _case.endswith("-21") else "aide_logement"
    QUALIFIED[f"{_case}/{_target}"] = {
        "class": "(б) их дефект против текста",
        "why": (f"{_D823_16}. Af = {_af} € (равно их коду), A = {_a} €, RLS = {_rls} €; шаг к нижнему "
                f"евро снимает {_loss} € с (A − c), у них не снят; "
                + _REPLICA.format(theirs=_theirs, ours=_ours) + _note
                + ". Обе величины — стадия после удержания CRDS (ст. 14 III и 19 ордонанса № 96-50, "
                  "sources/fr-apl/ordonnance-96-50.txt:11,16), наша — aide_nette_precompte_crds"),
    }

QUALIFIED["of176-aides-logement-reforme-janvier-2021-01/aide_logement"] = {
    "class": "(б) их дефект против текста",
    "why": ("Класс определён ПОД ПРОЧТЕНИЕМ D-82 (08.10.2026, решение владельца; прочтение §152, основание — "
            "практика CNAF, не текст; hook выбирает его в context). Без выбора прочтения наш ответ — отказ "
            "INEXACT_DIVISION (tests/openfisca-02.lawtest закрепляет его и не менялся): D. 823-16 "
            "(sources/fr-apl/cch-2021-01.txt:57) « Il décroît proportionnellement au dépassement de ce plafond » "
            "политики округления не называет. Под прочтением (27-lecture-arrondi-centime.law): Af = 189,72296 € "
            "(L = 242,46, C = 53,99, Pp = 106,72704, равно их коду до float32); доля (751,626 − 608) / "
            "(751,626 − 606,150) = 71813/72738 не 10-гладкая; Af × доля = 187,310276… → до сантима HALF_UP "
            "187,31 — то же, что их round_(Af × coeff, 2); минорация −5 → 182,31; шаг взносов D. 823-16 "
            "(« arrondi à l'euro inférieur, puis majoré »): ⌊182,31 − 0,91155⌋ + 0,91155 = 181,91155 "
            "(aide_mensuelle); после удержания CRDS наше 181,00199225 (aide_nette_precompte_crds). Их ход: "
            "round2(182,31 × 0,995) = 181,39845 → 181,40 = их код; реплика их чтения на нашем бареме "
            "(tools/compare_openfisca.py, chain(…, reading=\"openfisca\")) даёт 181,40 до цента. Расхождение "
            "0,398 € целиком из шага взносов (их код не делает шага к нижнему евро), пропорция у нас и у них "
            "совпадает; независимая реплика ожиданий сценария tests/openfisca-02-arrondi-centime.lawtest — "
            "на дробях с HALF_UP, не их число"),
}

QUALIFIED["of176-aides-logement-21/aide_logement_montant_brut_crds"] = {
    "class": "(б) их дефект против текста",
    "why": (f"{_D823_16}. Стадия до удержания CRDS, после вычета 98 % RLS: их код 43,749794 (float32; их "
            "файл — round(200 + 60.59 − 176.57105, 2) − 5 − 35.99 × 0.98 = 43,7498), наше aide_apres_rls "
            "43,12489475 = ⌊79,01895 − 0,39509475⌋ + 0,39509475 − 35,2702; реплика их чтения "
            "round2(84,01895) − 5 − 0,98 × 35,99 = 43,7498 = их код; разница 0,625 = снятые шагом к "
            "нижнему евро 0,62385525 € плюс их округление Af до сантима (+0,00105 €)"),
}


# ----------------------------------------------- сектор logement-foyer / CROUS (08.10.2026)
#
# Фойе и комнаты CROUS считаются по D. 832-24/25/26 и D. 842-15/16/17. Алгебру K пакет
# читает из отменённых R. 351-61 / R. 351-61-1 (D. 832-25 в закреплённых данных — картинка,
# README, «Коэффициент K»); числа r, cm, N, таблицы E0/L0 и форфейты — только закреплённые.
# Сверено по стадиям (scratch-прогон их кода, `of_inter.py`): E / L, C и N совпадают с нашими,
# расходятся K, E0/L0 (только дело CROUS) и последний шаг D. 823-16/D. 832-24.
# Реплика их чтения на НАШИХ закреплённых числах
#   их = round2(round2(K'·(E − E0)) − 5) × 0,995   (APL:  K' = 0,95 − (R − r·N)/(cm·N) без округления)
#   их = round2(round2(K'·(L + C − L0')) − 5) × 0,995 (AL: K' = 0,90 − R/(cm·N) без округления)
# воспроизводит их код до цента в обоих делах: 114,81 и 128,26.
_FOYER_STEP = ("их код не делает шага D. 832-24/D. 842-15 « diminué d'un montant représentatif des "
               "contributions sociales …, arrondi à l'euro inférieur, puis majoré de ce montant » "
               "(sources/fr-apl/cch-2021-01.txt:68,102) и не округляет K: текст велит « arrondi à "
               "deux décimales par défaut » (там же, :74,84)")

QUALIFIED["of176-aides-logement-etudiant-01/aide_logement"] = {
    "class": "(б) их дефект против текста",
    "why": ("Комната CROUS, ALS, 02.2021: их код K = 0,90 − R/(cm·N) = 0,70937629 БЕЗ округления, у нас "
            "0,70 (D. 832-25 a) 2°: « arrondi à deux décimales par défaut », cch-2021-01.txt:84); их L0 = "
            "53,6904 — это вторая таблица ст. 31 арретэ (« b) Au deuxième alinéa », 1 423,03 / 2 047,61 / "
            "2 629,85 / 4 095,05), применимая лишь с 01.07.2022, к месяцу 02.2021 (пакет: единая таблица "
            "редакции 2021 года, L0 = 52,988944); L = 169,41 и C = 53,99 совпадают. " + _FOYER_STEP +
            ". Наш ход: Af = 0,70 × (169,41 + 53,99 − 52,988944) = 119,2877392, после минорации ст. 41 "
            "114,2877392, чистый расход 109,11 € выше минимума 15 € (абатмент не нужен), не больше redevance "
            "400 €, шаг взносов 113,571438696, после CRDS 113,00358150252 (aide_nette_precompte_crds). "
            "Их ход: 0,70937629 × (169,41 + 53,99 − 53,690397) = 120,38797 → round2 120,39 − 5 = 115,39 → "
            "× 0,995 = 114,81 = их код (реплика на нашем бареме совпала до цента). Их YAML (114,34) от их "
            "кода отличается в пределах их допуска 1 %"),
}

QUALIFIED["of176-aides-logement-reforme-janvier-2021-08/aide_logement"] = {
    "class": "(б) их дефект против текста",
    "why": ("Класс определён ПОД ПРОЧТЕНИЕМ D-82 (08.10.2026, решение владельца; прочтение §152, основание — "
            "практика CNAF, не текст; hook выбирает его в context). Без выбора прочтения наш ответ — отказ "
            "INEXACT_DIVISION: E0 = (Σ транш + 45,57 × N) / 12 = 21 714 637 / 150 000 = 144,76424666… € не "
            "конечная десятичная дробь, а D. 832-26 (cch-2021-01.txt:93) велит « le total étant divisé par "
            "douze » и округления не называет (04-calcul-foyer.law; STATE.ru.md §5 п. 3). Конвенционированное "
            "фойе, APL, зона III, R = 9 100 €, redevance 612,60 €, 01.2021. Под прочтением "
            "(27-lecture-arrondi-centime.law): E0 = div_round(1 737,17096; 12; 2; HALF_UP) = 144,76; E = 385,78 "
            "(плафон ст. 27 ниже redevance); K = 0,55 (D. 832-25, чтение R. 351-61: « arrondi à deux décimales "
            "par défaut », :74); Af = 0,55 × (385,78 − 144,76) = 132,561; минорация −5 → 127,561; шаг взносов "
            "⌊127,561 − 0,637805⌋ + 0,637805 = 126,637805 (aide_mensuelle); после CRDS наше 126,004615975 "
            "(aide_nette_precompte_crds). Их E0 144,764251 — то же число до float32 БЕЗ округления до сантима "
            "(разница с D-82 0,0042 €, на итог влияет на 0,0023 €, ниже цента); остальное расхождение как "
            "у дела CROUS: их K = 0,95 − (R − r·N)/(cm·N) = 0,55557140 без округления, текст — « arrondi à "
            "deux décimales par défaut » (:74), то есть 0,55; " + _FOYER_STEP + ". Реплика их чтения на "
            "нашем бареме round2(round2(0,55557140 × (385,78 − E0)) − 5) × 0,995 = 128,2555 → 128,26 = их "
            "код до цента — и при E0 по D-82, и при их неокруглённом E0. Расхождение 2,2554 € целиком из K "
            "и последнего шага, а не из E, E0 или N. Ожидания сценария "
            "tests/foyer-apl-e0-arrondi-centime.lawtest — из независимой реплики на дробях с HALF_UP"),
}
