"""Перенос формульных дел OpenFisca-France 176.1.2 в fr.casf.rsa (corpus/tools/foreign/openfisca_formulas.py).

Исполняется в их venv. Факты дела берутся из ИХ ПРОГОНА: состав и даты рождения — из входа,
месячные ресурсы, prestations, aide au logement и статусы — из значений их переменных на нужный
месяц (D-85: LexImpact задаёт брутто и статусы, а не готовый salaire_net, поэтому доход из одного
входного ключа больше не берётся). Их вычисленные суммы САМОГО ПОСОБИЯ (rsa, rsa_montant,
rsa_socle) в факты не идут: это ожидания.

Нормативных ЧИСЕЛ адаптер не несёт. Montant forfaitaire (base личности, L. 262-2)
строит сам пакет из закреплённого декрета ревалоризации (параметр
MontantForfaitaireDecret, правило MfBaseDecret, `01-sources.law` фрагменты
DEC<год>_<номер>_ART1; DECISION-0452: сумма строится, а не подставляется), состав
домохозяйства — по шкале R. 262-1 (mf_menage), а в fr.minima.ressources он
передаётся правилами MfMoisReference1..3 и MfCompositionMinima (чужая голова
`then fr.minima.ressources::mf_mois(...)`): дело не подаёт ни mf_base, ни
mf_mois, ни mf_composition. Адаптер лишь решает, ПЕРЕНОСИТЬ ли дело: месяц права
обязан лежать в закреплённом ряду декретов (`sources/decrets-mf/manifest.json`:
окна start_month; окно 2022-07…2023-03 закрыто мостом — ст. 9 закона 2022-1158, правило
MfBaseLoi2022 под прочтением MfJuillet2022ArrondiCentime; ряд заканчивается за год после
последнего декрета); сумм в hook нет.

Прочтения (§152) выбираются в context каждого дела (PACKAGE["context"]), основание — практика
касс, а не текст: округление неточного квартального среднего R. 262-7 до сантима HALF_UP
(fr.minima.ressources::MoyenneArrondieCentime, решение владельца 08.10.2026) и округление
суммы после ст. 9 закона 2022-1158 (MfJuillet2022ArrondiCentime). Без выбора дело #19
(334/3) — INEXACT_DIVISION, окно 2022-07…2023-03 без построенной базы.

Соответствие их переменных нашим входам fr.minima.ressources (режим до 01.03.2025, R. 262-7
ред. 2017–2025: три месяца, предшествующих месяцу права; месяцы отсчёта m = M-3, M-2, M-1)
----------------------------------------------------------------------------------------------
Наш вход — месячный итог, их переменные — слагаемые того же месяца m, которые hook суммирует
по членам, принимаемым в расчёт (родители и дети с их rsa_enfant_a_charge: у них формула
rsa_base_ressources весит каждого (не ребёнок + ребёнок à charge)):

* `declare_total_mois(m)` — R. 262-7 II 1° «ressources perçues» (после вычета взносов по
  R. 262-12 II, то есть «нетто»; их salaire_net — нетто после cotisations и CSG/CRDS, брутто
  LexImpact — salaire_de_base — их движок сам доводит до salaire_net). Слагаемые — ровно перечень
  их `calcul_revenu_moyenne` (доходы от деятельности: salaire_net, indemnites_chomage_partiel,
  remuneration_apprenti, indemnites_volontariat, revenus_stage_formation_pro, bourse_recherche,
  hsup, etr, rpns_auto_entrepreneur_benefice, rsa_indemnites_journalieres_activite), перечень
  `calcul_revenu_pro` и `calcul_revenu_non_pro` (chomage_net, retraite_nette,
  allocation_securisation_professionnelle, dedommagement_victime_amiante, gains_exceptionnels,
  pensions_alimentaires_percues, pensions_invalidite, prestation_compensatoire,
  prime_forfaitaire_mensuelle_reprise_activite, rsa_base_ressources_patrimoine_individu,
  rsa_indemnites_journalieres_hors_activite) и `calcul_minima_sociaux` (ass, aah, asi, caah:
  у них те же три месяца усреднения; ASPA — месяц права, не переносится).
* `prestation_service_mois(m)` — R. 262-7 II 2° «prestations versées par l'organisme chargé du
  service»: их `rsa_base_ressources_prestations_familiales` (af_base/af, cf non majoré,
  rsa_forfait_asf, paje_*), уже после их forfaitisation ASF (R. 262-10-1). Стадия: их формула
  берёт значение МЕСЯЦА ПРАВА M для всего квартала, наше правило II 2° («intégralement affectées
  au mois de perception») — значение каждого месяца отсчёта; hook подаёт значение месяца m.
* `aide_logement_percue(m)` — их `aide_logement` месяца m (у владельца fr.apl это вход
  контракта APL-FORFAIT-PENDING); планку R. 262-10 применяет пакет. Их rsa_forfait_logement
  берёт aide_logement месяца права M, у нас — по месяцу отсчёта (тот же разрыв стадии).
* `logement` — их statut_occupation_logement месяца права: locataire_* → AUTRE (forfait
  логемент у арендатора — только планка помощи), loge_gratuitement без participation_frais →
  LOGE_GRATUIT (R. 262-9 «à titre gratuit»); с participation_frais — AUTRE; собственник и accédant
  не переносятся.
* `nb_personnes_forfait`, `foyer_nb_personnes` — число членов в расчёте (родители + их
  rsa_nb_enfants); `foyer_nb_parents` — число родителей (1 или 2),
  `foyer_membre_rang` и `foyer_enfant_charge` — факты о каждом члене. Классификация рангов 5+ (40/30 %)
  выполняется правилами пакета только для состава «родители + дети».

Чего hook НЕ переносит и почему (дело получает причину «не переносится»; числа не придумываются):
* нейтрализация прерванных ресурсов (их «interrompus au mois M», R. 262-13) и любой не названный
  выше компонент: страж разложения сверяет их `rsa_base_ressources` месяца права с суммой
  перенесённых слагаемых и отказывает при расхождении (> 0,02 EUR);
* ASPA, TNS-годовой показатель (ppa_rsa_derniers_revenus_tns_annuels_connus), rente viagère;
* majoré (L. 262-9) sans enfant de moins de trois ans : у них нет даты подачи заявления
  или декларации беременности R. 262-2, поэтому двенадцатимесячный срок не вывести;
  с ребёнком младше трёх лет продление строится пакетом от его даты рождения;
* состав из пяти и более человек теперь переносится, если расчёт включает только родителей
  и их детей на иждивении: hook подаёт число детей как факт состава, а ставки 40/30 % строит пакет;
* студент (etudiant), их rsa_eligibilite = false, молодой без условия часов (L. 262-4 1°);
* их флаг departement_experimentation_rsa (B-RSA-EXPERIMENTATION-2024).

Расхождение стадий (не дефект hook): наше среднее — до сантима HALF_UP (D-82), их — без округления.
"""
from __future__ import annotations

import json
import calendar
from datetime import date
from pathlib import Path

PACKAGE = {"package": "fr.casf.rsa", "version": "0.1.0", "namespace": "urn:fr:corpus:clir:rsa",
           "prefix": "fr-rsa", "timezone": "Europe/Paris",
           "world": ["fr.casf.rsa", "fr.minima.ressources"],
           "resolve": ["fr.casf.rsa", "fr.minima.ressources"],
           "context": ("deadline_policy RSA_MOIS; "
                       "interpretation fr.minima.ressources::MoyenneArrondieCentime; "
                       "interpretation MfJuillet2022ArrondiCentime;")}

# COVERAGE_START не объявляется: все правила пакета и fr.minima.ressources действуют
# с 2021-01-01 (effective), первая редакция CASF — CASF_ED2021_01; реестр (2021-01) верен.

TARGETS = {
    # Их rsa_forfait_logement у получателя aide au logement — планка R. 262-10 (шкала R. 262-9 1°).
    "rsa_forfait_logement": {"predicate": "fr.minima.ressources::plafond_forfait_logement", "kind": "Money"},
    # Их `rsa` — сумма за месяц права; у нас трёхместное allocation_mensuelle(p, mois, montant):
    # запрос по шаблону драйвера (08.10.2026), прежняя ручная проба — ниже для истории.
    "rsa": {"predicate": "allocation_mensuelle", "kind": "Money",
            "pattern": "allocation_mensuelle({subject}, {month}, v)"},
    "rsa_base_ressources": {"predicate": "base_ressources_mois", "kind": "Money"},
    # Проба 08.10.2026 (оракул, те же факты, что в analysis/openfisca-176/of176-rsa-1{6,7}-*.lawtest):
    # montant_du_trimestre −462.5008 (#16) и −445.5008 (#17), droit_rsa NEITHER,
    # allocation_mensuelle пусто — выплаты нет; их код rsa = 0 → РАВНО.
}

# Дело #19 больше не граница модели: среднее 334/3 округляется прочтением MoyenneArrondieCentime
# (см. контекст PACKAGE); класс каждой цели определяет сверка, а не запись здесь.
QUALIFIED: dict = {}

#: Причина, по которой `rsa_base_ressources` не сверяется (и по которой hook не тратит прогон на дело,
#: где это единственная цель).
BASE_REASON = ("их rsa_base_ressources — ресурсы БЕЗ aide au logement и forfait logement (они вычитаются отдельно, "
               "rsa_forfait_logement); наша база месяца включает планку помощи или forfait (R. 262-7 II 2°, "
               "R. 262-10, R. 262-9) и локальна в 02-trimestre.law (base_ressources_mois), публичной величины "
               "«ресурсы без жилья» у fr.minima.ressources нет (кандидат: pub-отношение суммы moyenne_declaree "
               "и prestation_service_mois)")


def skip_target(ctx, variable):
    if variable == "rsa_base_ressources":
        return BASE_REASON
    return None


MF_DIR = Path(__file__).resolve().parents[1] / "sources/decrets-mf"

#: Слагаемые месячного итога «ressources perçues» (R. 262-7 II 1°) — перечни их формул rsa.py
#: (`calcul_revenu_moyenne`, `calcul_revenu_pro`, `calcul_revenu_non_pro`, `calcul_minima_sociaux`).
RESSOURCES_ACTIVITE = ("salaire_net", "indemnites_chomage_partiel", "remuneration_apprenti",
                       "indemnites_volontariat", "revenus_stage_formation_pro", "bourse_recherche", "hsup", "etr",
                       "rpns_auto_entrepreneur_benefice", "rsa_indemnites_journalieres_activite")
RESSOURCES_AUTRES = ("chomage_net", "retraite_nette", "allocation_securisation_professionnelle",
                     "dedommagement_victime_amiante", "gains_exceptionnels", "pensions_alimentaires_percues",
                     "pensions_invalidite", "prestation_compensatoire", "prime_forfaitaire_mensuelle_reprise_activite",
                     "rsa_base_ressources_patrimoine_individu", "rsa_indemnites_journalieres_hors_activite")
MINIMA_SOCIAUX = ("ass", "aah", "asi", "caah")
RESSOURCES_INDIVIDU = RESSOURCES_ACTIVITE + RESSOURCES_AUTRES + MINIMA_SOCIAUX

#: Допуск стража разложения (их значения — float32).
GUARD_TOLERANCE = 0.02


def series_window(period: str) -> str | None:
    """Причина, по которой месяц права вне ряда закреплённых декретов, либо None.

    Только годность дела для переноса; сумм здесь нет (их строит пакет из декрета; окно
    `bridges` — из ст. 9 закона 2022-1158 по прочтению, оно в ряду). Окно декрета — год с
    месяца, названного в его статье 1.
    """
    manifest = json.loads((MF_DIR / "manifest.json").read_text(encoding="utf-8"))
    first = manifest["decrets"][0]["start_month"]
    last = manifest["decrets"][-1]["start_month"]
    if period < first:
        return f"месяц {period} раньше первого закреплённого декрета ({first})"
    if period >= f"{int(last[:4]) + 1}{last[4:]}":
        return f"месяц {period}: ряд закреплённых декретов кончается весной {int(last[:4]) + 1}"
    return None


def _month_minus(period: str, k: int) -> str:
    year, month = map(int, period.split("-"))
    month -= k
    while month <= 0:
        month, year = month + 12, year - 1
    return f"{year:04d}-{month:02d}"


def _input(ctx, entity_key: str):
    return ctx.item["input"].get(entity_key) or {}


def _output_variables(item: dict) -> set[str]:
    """Имена их переменных выхода дела — плоского и вложенного по сущностям."""
    names: set[str] = set()
    for key, raw in (item.get("output") or {}).items():
        if key in ("familles", "individus", "menages", "foyers_fiscaux") and isinstance(raw, dict) \
                and all(isinstance(v, dict) for v in raw.values()):
            for fields in raw.values():
                names.update(fields)
        else:
            names.add(key)
    return names


def _number(ctx, variable: str, period: str, index: int = 0) -> float:
    return float(ctx.value(variable, period=period, index=index) or 0)


def _money(value: float) -> str:
    """Денежный литерал факта: их значение с точностью до 4 знаков, но не короче двух.

    Их производные суммы (rsa_forfait_asf = 22,5 % BMAF = 100,334) не округляются до цента:
    округление в факте внесло бы в ответ ошибку представления (0,004 → 0,01 в итоге); округление
    до сантима остаётся прочтением пакета (D-82). Хвост float32 их движка отсекается на 4-м знаке.
    """
    text = f"{value:.4f}"
    while text.endswith("0") and len(text.split(".")[1]) > 2:
        text = text[:-1]
    return f"{text} EUR"


def facts(ctx) -> list[str]:
    famille = _input(ctx, "famille")
    people = _input(ctx, "individus")
    parents = list(famille.get("parents") or [])
    enfants = list(famille.get("enfants") or [])
    if ctx.period >= "2025-03":
        raise ctx.Skip("месяц права после 01.03.2025: окно M-4…M-2 и блоки DSN (R. 262-7 нов. ред.) — "
                       "перенос их salaire_net в dsn_pro_mois не заведён")
    # Дело, где единственная цель — rsa_base_ressources (не сверяется), не исполняется: факты ни к чему.
    if not (_output_variables(ctx.item) & {"rsa", "rsa_forfait_logement"}):
        raise ctx.Skip(BASE_REASON)
    experimentation = famille.get("departement_experimentation_rsa")
    if experimentation is True or (isinstance(experimentation, dict) and any(experimentation.values())):
        raise ctx.Skip("их флаг departement_experimentation_rsa=true (окно M-4…M-2 с 10.2024 у получателей CAF "
                       "пяти департаментов): основание закреплено (décret 2024-693, arrêté du 7 juillet 2024 — "
                       "fr.minima.ressources/sources/experimentation-2024), но режим не смоделирован "
                       "(B-RSA-EXPERIMENTATION-2024, README пакетов); закреплённый R. 262-7 (ред. 2017–2025) — "
                       "окно трёх предыдущих месяцев")
    if len(parents) not in (1, 2) or len(people) != len(parents) + len(enfants):
        raise ctx.Skip(f"foyer из {len(people)} чел. (родителей {len(parents)}, детей {len(enfants)}): "
                       "перенос заведён для одного родителя или пары и их детей; иные члены домохозяйства "
                       "в расчёт не берутся")
    if len(ctx.item["input"].get("familles") or {}) > 1:
        raise ctx.Skip("в деле несколько семей: перенос заведён для одной")
    if any(float(v or 0) for person in parents for v in (people[person].get("salaire_imposable") or {}).values()):
        raise ctx.Skip("ненулевой salaire_imposable: фискальная величина, не ресурс R. 262-6 — перенос не заведён")
    names = list(people)
    position = {name: names.index(name) for name in names}

    # Члены в расчёте: родители и дети с их rsa_enfant_a_charge (месяц права).
    counted_children = [child for child in enfants if bool(ctx.value("rsa_enfant_a_charge", index=position[child]))]
    counted = parents + counted_children
    n, n_parents = len(counted), len(parents)
    if n != len(parents) + int(ctx.value("rsa_nb_enfants")):
        raise ctx.Skip("число детей в расчёте расходится с их rsa_nb_enfants")
    majoration_theirs = bool(ctx.value("rsa_majore_eligibilite"))
    under_three = []
    right_year, right_month = map(int, ctx.period.split("-"))
    right_last = date(right_year, right_month, calendar.monthrange(right_year, right_month)[1])
    for child in counted_children:
        birth = date.fromisoformat(str(ctx.value("date_naissance", index=position[child]))[:10])
        third_year = birth.year + 3
        third = date(third_year, birth.month,
                     min(birth.day, calendar.monthrange(third_year, birth.month)[1]))
        if right_last < third:
            under_three.append(child)
    if majoration_theirs and (n_parents != 1 or not under_three):
        raise ctx.Skip("majoré L. 262-9/R. 262-2 sans enfant à charge de moins de trois ans : "
                       "date de déclaration de grossesse ou de dépôt de demande absente du cas ; "
                       "le mois du droit ne prouve pas le début des douze mois")
    if any(bool(ctx.value("etudiant", index=position[person])) for person in parents):
        raise ctx.Skip("родитель — студент (etudiant): etudiant_conge адаптером не переносится (L. 262-4 3°)")
    if not bool(ctx.value("rsa_eligibilite")):
        raise ctx.Skip("их rsa_eligibilite=false (условия L. 262-4: возраст, гражданство, TNS): условия "
                       "пакета подаются как установленные факты, ложное условие не переносится")
    outside = series_window(ctx.period)
    if outside:
        raise ctx.Skip(f"{outside}: montant forfaitaire не строится, дело сравнивать не с чем (B-RSA-MF-EURO)")

    year, month = map(int, ctx.period.split("-"))
    for person in parents:
        birth = str(ctx.value("date_naissance", index=position[person]))[:10]
        age = year - int(birth[:4]) - (1 if (month, 1) < (int(birth[5:7]), int(birth[8:10])) else 0)
        hours = bool(people[person].get("rsa_jeune_condition_heures_travail_remplie")) \
            or bool(ctx.value("rsa_jeune_condition_heures_travail_remplie", index=position[person]))
        if age < 25 and not hours and not counted_children:
            raise ctx.Skip(f"возраст {age} < 25 без условия часов и без детей (L. 262-4 1°, D. 262-25-1): "
                           "перенос не заведён")

    # Жильё: их статус месяца права.
    statut = str(ctx.value("statut_occupation_logement"))
    refs = [_month_minus(ctx.period, k) for k in (3, 2, 1)]
    aides = {m: _number(ctx, "aide_logement", m) for m in refs}
    if statut in ("locataire_vide", "locataire_meuble", "locataire_hlm"):
        logement = "AUTRE"
    elif statut == "loge_gratuitement":
        if bool(ctx.value("participation_frais")):
            logement = "AUTRE"
        elif any(aides.values()):
            raise ctx.Skip("hébergé à titre gratuit с aide au logement: у них max(планка помощи, forfait в натуре), "
                           "у нас помощь исключает forfait (R. 262-9 «ne bénéficiant pas d'aide»): перенос не заведён")
        else:
            logement = "LOGE_GRATUIT"
    else:
        raise ctx.Skip(f"statut_occupation_logement={statut!r}: перенос заведён для съёмщика и для hébergé à titre gratuit")

    # Ресурсы: месячные слагаемые их формул по членам в расчёте (см. docstring).
    if _number(ctx, "aspa", ctx.period):
        raise ctx.Skip("ненулевая ASPA месяца права: у них месяц права, а не усреднение — стадия не переносится")
    if _number(ctx, "ppa_rsa_derniers_revenus_tns_annuels_connus", str(year), index=position[parents[0]]):
        raise ctx.Skip("годовой показатель TNS (ppa_rsa_derniers_revenus_tns_annuels_connus): R. 262-18/19 "
                       "адаптером не переносится")
    monthly = {m: sum(_number(ctx, var, m, index=position[person])
                      for person in counted for var in RESSOURCES_INDIVIDU) for m in refs}
    prestations = {m: _number(ctx, "rsa_base_ressources_prestations_familiales", m) for m in refs}
    # Страж разложения: их rsa_base_ressources месяца права = среднее слагаемых + prestations месяца права.
    theirs = _number(ctx, "rsa_base_ressources", ctx.period)
    rebuilt = sum(monthly.values()) / 3 + _number(ctx, "rsa_base_ressources_prestations_familiales", ctx.period)
    if abs(theirs - rebuilt) > GUARD_TOLERANCE:
        raise ctx.Skip(f"их rsa_base_ressources {theirs:.2f} ≠ {rebuilt:.2f} (среднее перенесённых слагаемых + prestations): "
                       "нейтрализация прерванных ресурсов (R. 262-13) или не перенесённый компонент")

    # Montant forfaitaire НЕ подаётся: base — из декрета (MfBaseDecret), состав — по R. 262-1 (mf_menage),
    # mf_mois / mf_composition записывает сам пакет (MfMoisReference1..3, MfCompositionMinima).
    out = ["fr.minima.ressources::foyer_du_cas({main})",
           f"fr.minima.ressources::mois_demande(@{ctx.period}-01)",
           "fr.minima.ressources::mois_reference(" + ", ".join(f"@{m}-01" for m in refs) + ")",
           f"fr.minima.ressources::nb_personnes_forfait({{main}}, {n})",
           f"fr.minima.ressources::logement({{main}}, fr.minima.ressources::{logement})",
           f"foyer_nb_personnes({{main}}, {n})",
           f"foyer_nb_parents({{main}}, {n_parents})",
           f"mois_droit({{main}}, @{ctx.period}-01)",
           # Их вход не задаёт иного: резиденция, гражданство/пребывание, учёба — по умолчанию их модели
           # (страж rsa_eligibilite выше отсёк дела, где их условие ложно).
           "residence_stable({main})",
           "sejour_travail_condition({main})",
           "conjoint_enfants_comptes({main})",
           # 25+ — по дате рождения; 18–25 — их вход rsa_jeune_condition_heures_travail_remplie
           # или дети в расчёте (шов README: синтез возраста 18–25 в age_charge_condition — фонд).
           "age_charge_condition({main})"]
    # Только принадлежность и фактический ранг конкретного человека; класс ставки
    # и оба итоговых счётчика выводит пакет по R. 262-1.
    if majoration_theirs and under_three and n_parents == 1:
        out.append("isolement_constate({main})")
    for rank, person in enumerate(counted, 1):
        member = "{main}" if rank == 1 else f'entity_ref("urn:fr-rsa:of176:{ctx.item["name"]}:member-{rank}")'
        out.append(f"foyer_membre_rang({{main}}, {member}, {rank})")
        if person in counted_children:
            out.append(f"foyer_enfant_charge({{main}}, {member})")
            birth = str(ctx.value("date_naissance", index=position[person]))[:10]
            out.append(f"foyer_naissance({{main}}, {member}, @{birth})")
    for m in refs:
        # Ресурсы домохозяйства за месяц — сумма слагаемых всех членов в расчёте
        # (fr.minima.ressources::declare_total_mois ключуется по домохозяйству, не по личности).
        out += [f"fr.minima.ressources::declare_total_mois({{main}}, @{m}-01, {_money(monthly[m])})",
                f"fr.minima.ressources::prestation_service_mois({{main}}, @{m}-01, "
                + ("0 EUR)" if abs(prestations[m]) < 0.00005 else f"{_money(prestations[m])})")]
        if aides[m] > 0:
            out.append(f"fr.minima.ressources::aide_logement_percue({{main}}, @{m}-01, {_money(aides[m])})")
    return out
