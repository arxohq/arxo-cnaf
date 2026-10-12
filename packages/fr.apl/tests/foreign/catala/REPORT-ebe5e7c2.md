# Дела Catala (CatalaLang/catala-examples@ebe5e7c2) против fr.apl — ИСТОРИЯ (снимок прогона ebe5e7c2; действующий отчёт — REPORT.md, коммит 2694b17)

Класс | дел
--- | ---
ГРАНИЦА | 5
ДЕЛО_ВНЕ_ТАБЛИЦЫ | 4
НЕ_ПЕРЕНОСИТСЯ | 35
РАВНО | 47
РАВНО_ДО_САНТИМА | 30
РАСХОДИТСЯ_(б) | 3

дело | цель | их | класс | подробность
--- | --- | --- | --- | ---
al_accession_propriete-exemple1 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
al_accession_propriete-exemple1 | `coefficient_prise_en_charge` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
al_accession_propriete-exemple1 | `aide_finale_formule_initiale` | — | **НЕ_ПЕРЕНОСИТСЯ** | формула K (D. 832-11/D. 832-25) отсутствует в открытых данных — итог секторов фойе и приобретения не вычисляется
al_accession_propriete-exemple1 | `mensualite_eligible_al` | 375.2 | **ГРАНИЦА** | документ NON_EXECUTABLE: INEXACT_DIVISION — известная граница: двенадцатая часть суммы транш L0 (D. 832-26 второй абзац) десятично непредставима, а норма округления не называет — тот же отказ закреплён сценарием tests/outremer-guadeloupe-mensualite-minimale-inexacte.lawtest; Catala округляет до цента молча
al_accession_propriete-exemple1 | `mensualite_minimale_al` | 267.90 | **ГРАНИЦА** | документ NON_EXECUTABLE: INEXACT_DIVISION — известная граница: двенадцатая часть суммы транш L0 (D. 832-26 второй абзац) десятично непредставима, а норма округления не называет — тот же отказ закреплён сценарием tests/outremer-guadeloupe-mensualite-minimale-inexacte.lawtest; Catala округляет до цента молча
al_accession_propriete-exemple2 | `coefficient_prise_en_charge` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
al_accession_propriete-exemple2 | `aide_finale_formule_initiale` | — | **НЕ_ПЕРЕНОСИТСЯ** | формула K (D. 832-11/D. 832-25) отсутствует в открытых данных — итог секторов фойе и приобретения не вычисляется
al_accession_propriete-exemple2 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
al_accession_propriete-exemple2 | `—` | — | **ДЕЛО_ВНЕ_ТАБЛИЦЫ** | type_travaux_logement: значение AL.TypeTravauxLogementR842_5.PrévuDansListeR321_15 не в таблице
al_locatif-exemple1 | `aide_mensuelle` | 345.73 | **РАВНО_ДО_САНТИМА** | наше 345.733471, их 345.73
al_locatif-exemple2 | `aide_mensuelle` | 352.77 | **РАВНО_ДО_САНТИМА** | наше 352.7652695, их 352.77
al_locatif-exemple3 | `aide_mensuelle` | 339.70 | **РАВНО_ДО_САНТИМА** | наше 339.70317425, их 339.70
al_locatif-exemple4 | `forfait_charges` | 81.56 | **РАВНО** | 81.56
al_locatif-exemple4 | `plafond_loyer` | 424.22 | **РАВНО** | 424.22
al_locatif-exemple4 | `participation_minimale` | 42.99 | **РАВНО_ДО_САНТИМА** | наше 42.9913, их 42.99
al_locatif-exemple4 | `taux_composition_familiale` | 0.0238 | **РАВНО** | 0.0238
al_locatif-exemple4 | `participation_personnelle` | 131.30 | **РАВНО_ДО_САНТИМА** | наше 131.30095, их 131.30
al_locatif-exemple4 | `aide_mensuelle` | 230.63 | **РАВНО_ДО_САНТИМА** | наше 230.625, их 230.63
al_logement_foyer-castest1 | `coefficient_prise_en_charge` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
al_logement_foyer-castest1 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
al_logement_foyer-castest1 | `equivalence_loyer_retenue` | 206.40 | **РАВНО** | 206.4
al_logement_foyer-castest1 | `loyer_minimal` | 124.64 | **РАСХОДИТСЯ_(б)** | наше 115.18728, их 124.64, разница -9.45272 — их дефект: те же входы и та же вторая таблица до её применимости (см. castest5)
apl_accession_propriete-exemple1 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
apl_accession_propriete-exemple1 | `coefficient_prise_en_charge_d832_10` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
apl_accession_propriete-exemple1 | `aide_finale_formule_initiale` | — | **НЕ_ПЕРЕНОСИТСЯ** | формула K (D. 832-11/D. 832-25) отсутствует в открытых данных — итог секторов фойе и приобретения не вычисляется
apl_accession_propriete-exemple1 | `mensualite_eligible` | 533.91 | **РАВНО** | 533.91
apl_accession_propriete-exemple1 | `mensualite_minimale` | 332.76 | **РАВНО_ДО_САНТИМА** | наше 332.7558, их 332.76
apl_accession_propriete-exemple2 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
apl_accession_propriete-exemple2 | `coefficient_prise_en_charge_d832_10` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
apl_accession_propriete-exemple2 | `aide_finale_formule_initiale` | — | **НЕ_ПЕРЕНОСИТСЯ** | формула K (D. 832-11/D. 832-25) отсутствует в открытых данных — итог секторов фойе и приобретения не вычисляется
apl_accession_propriete-exemple2 | `mensualite_eligible` | 399.20 | **ГРАНИЦА** | документ NON_EXECUTABLE: INEXACT_DIVISION — известная граница: двенадцатая часть L0 (D. 832-15, работы для приобретения) непредставима, норма округления не названа; Catala округляет молча
apl_accession_propriete-exemple2 | `mensualite_minimale` | 367.42 | **ГРАНИЦА** | документ NON_EXECUTABLE: INEXACT_DIVISION — известная граница: двенадцатая часть L0 (D. 832-15, работы для приобретения) непредставима, норма округления не названа; Catala округляет молча
apl_accession_propriete-exemple3 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
apl_accession_propriete-exemple3 | `coefficient_prise_en_charge_d832_10` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
apl_accession_propriete-exemple3 | `aide_finale_formule_initiale` | — | **НЕ_ПЕРЕНОСИТСЯ** | формула K (D. 832-11/D. 832-25) отсутствует в открытых данных — итог секторов фойе и приобретения не вычисляется
apl_accession_propriete-exemple3 | `mensualite_eligible` | 533.91 | **РАВНО** | 533.91
apl_accession_propriete-exemple3 | `mensualite_minimale` | 332.76 | **РАВНО_ДО_САНТИМА** | наше 332.7558, их 332.76
apl_accession_propriete-exemple4 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
apl_accession_propriete-exemple4 | `coefficient_prise_en_charge_d832_10` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
apl_accession_propriete-exemple4 | `aide_finale_formule_initiale` | — | **НЕ_ПЕРЕНОСИТСЯ** | формула K (D. 832-11/D. 832-25) отсутствует в открытых данных — итог секторов фойе и приобретения не вычисляется
apl_accession_propriete-exemple4 | `mensualite_eligible` | 399.20 | **ГРАНИЦА** | у нас вывода нет — текст: у подслучаев ст. 18 после 30.09.2017 колонки c) «amélioré par l'occupant» нет — плафон правило не производит, а не выдумывает (README, сектор приобретения)
apl_accession_propriete-exemple4 | `mensualite_minimale` | 290.21 | **РАВНО_ДО_САНТИМА** | наше 290.2091, их 290.21
apl_locatif-exemple1 | `aide_non_versee` | True | **РАВНО** | наш ответ TRUE_ONLY
apl_locatif-exemple1 | `forfait_charges` | 91.09 | **РАВНО** | 91.09
apl_locatif-exemple1 | `plafond_loyer` | 524.20 | **РАВНО** | 524.2
apl_locatif-exemple1 | `participation_minimale` | 52.30 | **РАВНО_ДО_САНТИМА** | наше 52.29965, их 52.30
apl_locatif-exemple1 | `taux_composition_familiale` | 0.0201 | **РАВНО** | 0.0201
apl_locatif-exemple1 | `participation_personnelle` | 714.35 | **РАВНО_ДО_САНТИМА** | наше 714.345, их 714.35
apl_locatif-exemple2 | `aide_mensuelle` | 352.77 | **РАВНО_ДО_САНТИМА** | наше 352.7652695, их 352.77
apl_locatif-exemple2 | `forfait_charges` | 78.80 | **РАВНО** | 78.8
apl_locatif-exemple2 | `plafond_loyer` | 409.88 | **РАВНО** | 409.88
apl_locatif-exemple2 | `participation_minimale` | 41.54 | **РАВНО_ДО_САНТИМА** | наше 41.5378, их 41.54
apl_locatif-exemple2 | `taux_composition_familiale` | 0.0238 | **РАВНО** | 0.0238
apl_locatif-exemple2 | `participation_personnelle` | 130.63 | **РАВНО_ДО_САНТИМА** | наше 130.6261, их 130.63
apl_locatif-exemple3 | `aide_mensuelle` | 321.61 | **РАВНО_ДО_САНТИМА** | наше 321.60933775, их 321.61
apl_locatif-exemple3 | `forfait_charges` | 91.09 | **РАВНО** | 91.09
apl_locatif-exemple3 | `plafond_loyer` | 425.80 | **РАВНО** | 425.8
apl_locatif-exemple3 | `participation_minimale` | 42.42 | **РАВНО_ДО_САНТИМА** | наше 42.42265, их 42.42
apl_locatif-exemple3 | `taux_composition_familiale` | 0.0201 | **РАВНО** | 0.0201
apl_locatif-exemple3 | `participation_personnelle` | 172.22 | **РАВНО_ДО_САНТИМА** | наше 172.22245, их 172.22
apl_locatif-exemple4 | `aide_non_versee` | True | **РАВНО** | наш ответ TRUE_ONLY
apl_locatif-exemple4 | `forfait_charges` | 66.51 | **РАВНО** | 66.51
apl_locatif-exemple4 | `plafond_loyer` | 406.30 | **РАВНО** | 406.3
apl_locatif-exemple4 | `participation_minimale` | 40.19 | **РАВНО_ДО_САНТИМА** | наше 40.18885, их 40.19
apl_locatif-exemple4 | `taux_composition_familiale` | 0.027 | **РАВНО** | 0.027
apl_locatif-exemple4 | `participation_personnelle` | 1015.68 | **РАВНО_ДО_САНТИМА** | наше 1015.68191, их 1015.68
apl_locatif-exemple5 | `aide_mensuelle` | 311.56 | **РАВНО_ДО_САНТИМА** | наше 311.5595, их 311.56
apl_locatif-exemple5 | `forfait_charges` | 54.22 | **РАВНО** | 54.22
apl_locatif-exemple5 | `plafond_loyer` | 298.07 | **РАВНО** | 298.07
apl_locatif-exemple5 | `participation_minimale` | 35.39 | **РАВНО** | 35.39
apl_locatif-exemple5 | `taux_composition_familiale` | 0.0283 | **РАВНО** | 0.0283
apl_locatif-exemple5 | `participation_personnelle` | 35.39 | **РАВНО** | 35.39
apl_locatif-exemple6 | `aide_non_versee` | True | **РАВНО** | наш ответ TRUE_ONLY
apl_locatif-exemple6 | `forfait_charges` | 54.22 | **РАВНО** | 54.22
apl_locatif-exemple6 | `plafond_loyer` | 317.97 | **РАВНО** | 317.97
apl_locatif-exemple6 | `participation_minimale` | 35.39 | **РАВНО** | 35.39
apl_locatif-exemple6 | `taux_composition_familiale` | 0.0315 | **РАВНО** | 0.0315
apl_locatif-exemple6 | `participation_personnelle` | 477.32 | **РАВНО_ДО_САНТИМА** | наше 477.31905, их 477.32
apl_locatif-exemple7 | `aide_mensuelle` | 153.77 | **РАВНО_ДО_САНТИМА** | наше 153.76931525, их 153.77
apl_locatif-exemple7 | `forfait_charges` | 127.96 | **РАВНО** | 127.96
apl_locatif-exemple7 | `plafond_loyer` | 618.20 | **РАВНО** | 618.2
apl_locatif-exemple7 | `participation_minimale` | 55.67 | **РАВНО_ДО_САНТИМА** | наше 55.6716, их 55.67
apl_locatif-exemple7 | `taux_composition_familiale` | 0.0173 | **РАВНО** | 0.0173
apl_locatif-exemple7 | `participation_personnelle` | 496.10 | **РАВНО_ДО_САНТИМА** | наше 496.09695, их 496.10
apl_locatif-exemple8 | `aide_mensuelle` | 11.06 | **РАВНО_ДО_САНТИМА** | наше 11.05561205, их 11.06
apl_locatif-exemple8 | `forfait_charges` | 54.22 | **РАВНО** | 54.22
apl_locatif-exemple8 | `plafond_loyer` | 268.26 | **РАВНО** | 268.26
apl_locatif-exemple8 | `participation_minimale` | 35.39 | **РАВНО** | 35.39
apl_locatif-exemple8 | `taux_composition_familiale` | 0.0315 | **РАВНО** | 0.0315
apl_locatif-exemple8 | `participation_personnelle` | 306.36 | **РАВНО_ДО_САНТИМА** | наше 306.35759, их 306.36
apl_locatif-exemple9 | `aide_mensuelle` | 211.06 | **РАВНО_ДО_САНТИМА** | наше 211.05532525, их 211.06
apl_logement_foyer-castest1 | `coefficient_r_d832_25` | — | **НЕ_ПЕРЕНОСИТСЯ** | часть формулы K
apl_logement_foyer-castest1 | `coefficient_multiplicateur_d832_25` | — | **НЕ_ПЕРЕНОСИТСЯ** | часть формулы K
apl_logement_foyer-castest1 | `coefficient_prise_en_charge_d832_25` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
apl_logement_foyer-castest1 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
apl_logement_foyer-castest1 | `nombre_parts` | 1.8 | **РАВНО** | 1.8
apl_logement_foyer-castest1 | `plafond_equivalence_loyer` | 450.57 | **РАВНО** | 450.57
apl_logement_foyer-castest1 | `equivalence_loyer_minimale` | 318.13 | **РАВНО_ДО_САНТИМА** | наше 318.12546, их 318.13
apl_logement_foyer-castest2 | `coefficient_prise_en_charge` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
apl_logement_foyer-castest2 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
apl_logement_foyer-castest2 | `equivalence_loyer_retenue` | 320.73 | **РАВНО** | 320.73
apl_logement_foyer-castest2 | `forfait_charges_foyer` | 54.22 | **РАВНО** | 54.22
apl_logement_foyer-castest2 | `loyer_minimal` | 307.97 | **РАСХОДИТСЯ_(б)** | наше 365.7683, их 307.97, разница 57.7983 — их дефект: апрель 2022 года, числа редакции с 1 июля 2022 года (замер 14.09.2026, README «Квалификация расхождений»)
apl_logement_foyer-castest3 | `coefficient_prise_en_charge_d832_25` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
apl_logement_foyer-castest3 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
apl_logement_foyer-castest3 | `equivalence_loyer_eligible` | 350 | **РАВНО** | 350
apl_logement_foyer-castest3 | `plafond_equivalence_loyer` | 444.43 | **РАВНО** | 444.43
apl_logement_foyer-castest3 | `equivalence_loyer_minimale` | 98.95 | **РАВНО_ДО_САНТИМА** | наше 98.950268, их 98.95
apl_logement_foyer-castest4 | `coefficient_prise_en_charge_d832_25` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
apl_logement_foyer-castest4 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
apl_logement_foyer-castest4 | `equivalence_loyer_eligible` | 350 | **РАВНО** | 350
apl_logement_foyer-castest4 | `plafond_equivalence_loyer` | 446.30 | **РАВНО** | 446.3
apl_logement_foyer-castest4 | `equivalence_loyer_minimale` | 98.95 | **РАВНО_ДО_САНТИМА** | наше 98.950268, их 98.95
apl_logement_foyer-castest5 | `coefficient_prise_en_charge_d832_25` | — | **НЕ_ПЕРЕНОСИТСЯ** | коэффициент K — картинка в LEGI, граница пакета
apl_logement_foyer-castest5 | `montant` | — | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора требует коэффициента K (D. 832-11/D. 832-25), формула которого в открытых данных — картинка; граница пакета
apl_logement_foyer-castest5 | `equivalence_loyer_eligible` | 350 | **РАВНО** | 350
apl_logement_foyer-castest5 | `plafond_equivalence_loyer` | 446.30 | **РАВНО** | 446.3
apl_logement_foyer-castest5 | `equivalence_loyer_minimale` | 124.64 | **РАСХОДИТСЯ_(б)** | наше 115.18728, их 124.64, разница -9.45272 — их дефект: месяц права май 2022 года, а число 124,64 € — вторая таблица ст. 31, применимая лишь к престациям с 1 июля 2022 года; по тексту месяца права — первая таблица × N + 76,32 = 115,19 €
eligibilite_apl-exemple1 | `éligible` | — | **НЕ_ПЕРЕНОСИТСЯ** | право на пособие не выводится
eligibilite_apl-exemple1 | `—` | — | **ДЕЛО_ВНЕ_ТАБЛИЦЫ** | право на пособие (гражданство, состав семьи, ресурсы по CSS) пакет не выводит — граница fr.apl
eligibilite_apl-exemple2 | `éligible` | — | **НЕ_ПЕРЕНОСИТСЯ** | право на пособие не выводится
eligibilite_apl-exemple2 | `—` | — | **ДЕЛО_ВНЕ_ТАБЛИЦЫ** | право на аллокацию (условия L. 822-*, CSS) пакет не выводит — граница fr.apl
eligibilite_apl-exemple3 | `éligible` | — | **НЕ_ПЕРЕНОСИТСЯ** | право на пособие не выводится
eligibilite_apl-exemple3 | `—` | — | **ДЕЛО_ВНЕ_ТАБЛИЦЫ** | право на аллокацию (условия L. 822-*, CSS) пакет не выводит — граница fr.apl
