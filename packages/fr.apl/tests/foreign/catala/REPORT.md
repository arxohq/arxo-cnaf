# Дела Catala (CatalaLang/catala-examples@2694b17d) против fr.apl

Класс | дел
--- | ---
(а) граница | 4
(б) их дефект против текста | 6
НЕ_ПЕРЕНОСИТСЯ | 29
РАВНО | 59
РАВНО_ДО_САНТИМА | 31

дело | цель | их | класс | подробность
--- | --- | --- | --- | ---
al_accession_propriete-exemple1 | `montant` | 96,48 € | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора приобретения аллокаций D. 842-6 = K × (L + C − L0): правило K в модуле 06 не заведено (отсылка к 2° D. 832-25; чтение R. 351-61-1 принято D-83 для фойе), а L0 (деление на 12, D. 832-26 2-й абзац) вне D-82 — граница пакета
al_accession_propriete-exemple1 | `coefficient_prise_en_charge` | 0,62 | **НЕ_ПЕРЕНОСИТСЯ** | K D. 842-6 «calculé selon les dispositions du 2° de l'article D. 832-25»: функция coefficient_k_jeunes_travailleurs есть (модуль 04), но правила для сектора приобретения аллокаций нет (06-calcul-accession-al.law, комментарий «КОЭФФИЦИЕНТА K НЕТ» устарел после D-83) — описано как (а), не исправлено: дело заморское, главы IX–X арретэ вне охвата сектора
al_accession_propriete-exemple1 | `aide_finale_formule_initiale` | 101,90€ | **НЕ_ПЕРЕНОСИТСЯ** | итог формулы сектора приобретения (K × (L + C − L0)): K D. 832-11 / D. 842-6 в секторе приобретения не считается — граница пакета
al_accession_propriete-exemple1 | `mensualite_eligible_al` | 375.2 | **РАВНО** | 375.2
al_accession_propriete-exemple1 | `mensualite_minimale_al` | 267.90 | **(а) граница** | документ NON_EXECUTABLE: INEXACT_DIVISION — (а)-граница: двенадцатая часть суммы транш L0 «le total étant divisé par douze» десятично непредставима, текст политики округления не называет, а прочтение D-82 (ArrondiCentimeHalfUp) L0 не покрывает — DECISIONS D-82 «Не покрыто: L0 фойе и приобретения»; наш ответ — отказ INEXACT_DIVISION по замыслу (§58), их число — округление денежного типа Catala (D. 832-26 2-й абзац через D. 842-6)
al_accession_propriete-exemple2 | `coefficient_prise_en_charge` | 0,66 | **НЕ_ПЕРЕНОСИТСЯ** | K D. 842-6 «calculé selon les dispositions du 2° de l'article D. 832-25»: функция coefficient_k_jeunes_travailleurs есть (модуль 04), но правила для сектора приобретения аллокаций нет (06-calcul-accession-al.law, комментарий «КОЭФФИЦИЕНТА K НЕТ» устарел после D-83) — описано как (а), не исправлено: дело заморское, главы IX–X арретэ вне охвата сектора
al_accession_propriete-exemple2 | `aide_finale_formule_initiale` | 141,99€ | **НЕ_ПЕРЕНОСИТСЯ** | итог формулы сектора приобретения (K × (L + C − L0)): K D. 832-11 / D. 842-6 в секторе приобретения не считается — граница пакета
al_accession_propriete-exemple2 | `montant` | 85,00 € | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора приобретения аллокаций D. 842-6 = K × (L + C − L0): правило K в модуле 06 не заведено (отсылка к 2° D. 832-25; чтение R. 351-61-1 принято D-83 для фойе), а L0 (деление на 12, D. 832-26 2-й абзац) вне D-82 — граница пакета
al_accession_propriete-exemple2 | `mensualité_éligible` | 405,10 € | **НЕ_ПЕРЕНОСИТСЯ** | дело вне таблицы: type_travaux_logement: значение AL.TypeTravauxLogementR842_5.PrévuDansListeR321_15 не в таблице
al_accession_propriete-exemple2 | `mensualité_minimale` | 296,96 € | **НЕ_ПЕРЕНОСИТСЯ** | дело вне таблицы: type_travaux_logement: значение AL.TypeTravauxLogementR842_5.PrévuDansListeR321_15 не в таблице
al_locatif-exemple1 | `aide_mensuelle` | 345.73 | **РАВНО_ДО_САНТИМА** | наше 345.733471, их 345.73
al_locatif-exemple2 | `aide_mensuelle` | 352.77 | **РАВНО_ДО_САНТИМА** | наше 352.7652695, их 352.77
al_locatif-exemple3 | `aide_mensuelle` | 339.70 | **РАВНО_ДО_САНТИМА** | наше 339.70317425, их 339.70
al_locatif-exemple4 | `forfait_charges` | 81.56 | **РАВНО** | 81.56
al_locatif-exemple4 | `plafond_loyer` | 424.22 | **РАВНО** | 424.22
al_locatif-exemple4 | `participation_minimale` | 42.99 | **РАВНО_ДО_САНТИМА** | наше 42.9913, их 42.99
al_locatif-exemple4 | `taux_composition_familiale` | 0.0238 | **РАВНО** | 0.0238
al_locatif-exemple4 | `participation_personnelle` | 131.30 | **РАВНО_ДО_САНТИМА** | наше 131.30095, их 131.30
al_locatif-exemple4 | `aide_mensuelle` | 230.63 | **РАВНО_ДО_САНТИМА** | наше 230.625, их 230.63
al_logement_foyer-castest1 | `equivalence_loyer_retenue` | 206.40 | **РАВНО** | 206.4
al_logement_foyer-castest1 | `loyer_minimal` | 124.64 | **(б) их дефект против текста** | наше 115.18728, их 124.64, разница -9.45272 — (б) их дефект против текста: месяц права 05.2022 (L0 D. 842-15 → второй абзац D. 832-26) — редакция ст. 31 арретэ ARRETE_ED2022_01 (in_force [2022-01-01, 2022-07-01), apl/01-sources.law:228) с ОДНОЙ таблицей для обоих абзацев D. 832-26 («mentionnés à l'article D. 832-26», apl/sources/fr-apl/arrete-2022-01.txt:119) и форфейтом 76,32 второго абзаца; их число — вторая таблица b) редакции с 01.07.2022 (arrete-2022-07.txt:123-124: 0 % до 1 423,03; 2,40 %; 20,80 %; 23,20 %; 32,80 %). Реплика их чтения: те же входы, что apl castest5: 124,64; наше по тексту: 115,18728
al_logement_foyer-castest1 | `coefficient_prise_en_charge` | 0.6 | **РАВНО** | 0.6
al_logement_foyer-castest1 | `aide_mensuelle` | 76.38 | **(б) их дефект против текста** | наше 81.41129816, их 76.38, разница 5.03129816 — (б) следствие строки loyer_minimal того же дела: редакция ст. 31 арретэ ARRETE_ED2022_01 (in_force [2022-01-01, 2022-07-01), apl/01-sources.law:228) с одной таблицей для обоих абзацев D. 832-26 (apl/sources/fr-apl/arrete-2022-01.txt:119); их L0/E0 — вторая таблица b) редакции с 01.07.2022 (arrete-2022-07.txt:123-124). Реплика их чтения нашей же цепочкой D. 842-15 (K = 0,6, L = 206,40 — у обоих РАВНО; C = 54,22): K × (L + C − L0) = 0,6 × (206,40 + 54,22 − 124,64) = 81,588; − минорация ст. 41 5 € = 76,588; шаг взносов (0,5 %: 0,38294; 76,20506 → 76 €; + 0,38294) = 76,38294 → их 76,38. Наше по тексту: 0,6 × (260,62 − 115,18728) = 87,259632 − 5 = 82,259632 → 81 + 0,41129816 = 81,41129816
apl_accession_propriete-exemple1 | `montant` | 181,91 € | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора приобретения APL требует K D. 832-11; его алгебра (R. 351-19) не закреплена — граница пакета (05-calcul-accession.law)
apl_accession_propriete-exemple1 | `coefficient_prise_en_charge_d832_10` | 0,67 | **НЕ_ПЕРЕНОСИТСЯ** | K D. 832-11 (APL, приобретение): алгебра отменённой R. 351-19 не закреплена, формула D. 832-11 в LEGI — картинка; граница пакета
apl_accession_propriete-exemple1 | `aide_finale_formule_initiale` | 187,35€ | **НЕ_ПЕРЕНОСИТСЯ** | итог формулы сектора приобретения (K × (L + C − L0)): K D. 832-11 / D. 842-6 в секторе приобретения не считается — граница пакета
apl_accession_propriete-exemple1 | `mensualite_eligible` | 533.91 | **РАВНО** | 533.91
apl_accession_propriete-exemple1 | `mensualite_minimale` | 332.76 | **РАВНО_ДО_САНТИМА** | наше 332.7558, их 332.76
apl_accession_propriete-exemple2 | `montant` | 67,34 € | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора приобретения APL требует K D. 832-11; его алгебра (R. 351-19) не закреплена — граница пакета (05-calcul-accession.law)
apl_accession_propriete-exemple2 | `coefficient_prise_en_charge_d832_10` | 0,66 | **НЕ_ПЕРЕНОСИТСЯ** | K D. 832-11 (APL, приобретение): алгебра отменённой R. 351-19 не закреплена, формула D. 832-11 в LEGI — картинка; граница пакета
apl_accession_propriete-exemple2 | `aide_finale_formule_initiale` | 72,77€ | **НЕ_ПЕРЕНОСИТСЯ** | итог формулы сектора приобретения (K × (L + C − L0)): K D. 832-11 / D. 842-6 в секторе приобретения не считается — граница пакета
apl_accession_propriete-exemple2 | `mensualite_eligible` | 399.20 | **(а) граница** | у нас вывода нет — (а)-граница: заём подписан 02.12.2019, жильё «Ancien, amélioré par l'occupant» — у подслучаев ст. 18 после 30.09.2017 колонки c) «amélioré par l'occupant» нет (05-calcul-accession.law:457-460): плафон правило не производит, а не выдумывает; их 399,20 — их выбор колонки b) (то же, что Exemple4)
apl_accession_propriete-exemple2 | `mensualite_minimale` | 367.42 | **(а) граница** | документ NON_EXECUTABLE: INEXACT_DIVISION — (а)-граница: двенадцатая часть суммы транш L0 «le total étant divisé par douze» десятично непредставима, текст политики округления не называет, а прочтение D-82 (ArrondiCentimeHalfUp) L0 не покрывает — DECISIONS D-82 «Не покрыто: L0 фойе и приобретения»; наш ответ — отказ INEXACT_DIVISION по замыслу (§58), их число — округление денежного типа Catala (L0 D. 832-15, работы при приобретении)
apl_accession_propriete-exemple3 | `montant` | 181,91 € | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора приобретения APL требует K D. 832-11; его алгебра (R. 351-19) не закреплена — граница пакета (05-calcul-accession.law)
apl_accession_propriete-exemple3 | `coefficient_prise_en_charge_d832_10` | 0,67 | **НЕ_ПЕРЕНОСИТСЯ** | K D. 832-11 (APL, приобретение): алгебра отменённой R. 351-19 не закреплена, формула D. 832-11 в LEGI — картинка; граница пакета
apl_accession_propriete-exemple3 | `aide_finale_formule_initiale` | 187,57€ | **НЕ_ПЕРЕНОСИТСЯ** | итог формулы сектора приобретения (K × (L + C − L0)): K D. 832-11 / D. 842-6 в секторе приобретения не считается — граница пакета
apl_accession_propriete-exemple3 | `mensualite_eligible` | 533.91 | **РАВНО** | 533.91
apl_accession_propriete-exemple3 | `mensualite_minimale` | 332.76 | **РАВНО_ДО_САНТИМА** | наше 332.7558, их 332.76
apl_accession_propriete-exemple4 | `montant` | 118,59 € | **НЕ_ПЕРЕНОСИТСЯ** | итог сектора приобретения APL требует K D. 832-11; его алгебра (R. 351-19) не закреплена — граница пакета (05-calcul-accession.law)
apl_accession_propriete-exemple4 | `coefficient_prise_en_charge_d832_10` | 0,66 | **НЕ_ПЕРЕНОСИТСЯ** | K D. 832-11 (APL, приобретение): алгебра отменённой R. 351-19 не закреплена, формула D. 832-11 в LEGI — картинка; граница пакета
apl_accession_propriete-exemple4 | `aide_finale_formule_initiale` | 123,94 € | **НЕ_ПЕРЕНОСИТСЯ** | итог формулы сектора приобретения (K × (L + C − L0)): K D. 832-11 / D. 842-6 в секторе приобретения не считается — граница пакета
apl_accession_propriete-exemple4 | `mensualite_eligible` | 399.20 | **(а) граница** | у нас вывода нет — (а)-граница: у подслучаев ст. 18 после 30.09.2017 колонки c) «amélioré par l'occupant» нет (05-calcul-accession.law:457-460) — плафон правило не производит, а не выдумывает; их 399,20 — их выбор колонки b)
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
apl_logement_foyer-castest1 | `param:CoefficientRFoyer` | 1217.26 | **РАВНО** | 1217.26 — закреплённый параметр CoefficientRFoyer (bareme/CoefficientRFoyer.lawparam.json, значение с 2019-10-02); сценарий не пишется: параметр не отношение
apl_logement_foyer-castest1 | `param:CoefMultiplicateurFoyerGeneral` | 13393.40 | **РАВНО** | 13393.40 — закреплённый параметр CoefMultiplicateurFoyerGeneral (bareme/CoefMultiplicateurFoyerGeneral.lawparam.json, значение с 2019-10-02); сценарий не пишется: параметр не отношение
apl_logement_foyer-castest1 | `nombre_parts` | 1.8 | **РАВНО** | 1.8
apl_logement_foyer-castest1 | `coefficient_prise_en_charge` | 0.41 | **РАВНО** | 0.41
apl_logement_foyer-castest1 | `plafond_equivalence_loyer` | 450.57 | **РАВНО** | 450.57
apl_logement_foyer-castest1 | `equivalence_loyer_minimale` | 318.13 | **РАВНО** | 318.13
apl_logement_foyer-castest1 | `aide_mensuelle` | 12.06 | **РАВНО_ДО_САНТИМА** | наше 12.0608335, их 12.06
apl_logement_foyer-castest2 | `equivalence_loyer_retenue` | 320.73 | **РАВНО** | 320.73
apl_logement_foyer-castest2 | `forfait_charges_foyer` | 54.22 | **РАВНО** | 54.22
apl_logement_foyer-castest2 | `loyer_minimal` | 307.97 | **(б) их дефект против текста** | наше 365.7683, их 307.97, разница 57.7983 — (б) их дефект против текста: месяц права 04.2022 (L0 D. 842-15 → второй абзац D. 832-26) — редакция ст. 31 арретэ ARRETE_ED2022_01 (in_force [2022-01-01, 2022-07-01), apl/01-sources.law:228) с ОДНОЙ таблицей для обоих абзацев D. 832-26 («mentionnés à l'article D. 832-26», apl/sources/fr-apl/arrete-2022-01.txt:119) и форфейтом 76,32 второго абзаца; их число — вторая таблица b) редакции с 01.07.2022 (arrete-2022-07.txt:123-124: 0 % до 1 423,03; 2,40 %; 20,80 %; 23,20 %; 32,80 %). Реплика их чтения: N = 1,5; Σ транш b) × N = 3 619,26876 + 76,32 = 3 695,58876, /12 = 307,96573 → 307,97; наше по тексту: Σ первой таблицы × 1,5 = 4 312,8996 + 76,32 = 4 389,2196, /12 = 365,7683
apl_logement_foyer-castest2 | `coefficient_prise_en_charge` | 0.43 | **РАВНО** | 0.43
apl_logement_foyer-castest2 | `aide_mensuelle` | 23.12 | **(б) их дефект против текста** | у нас вывода нет — (б) следствие строки loyer_minimal того же дела (месяц права 04.2022): редакция ст. 31 арретэ ARRETE_ED2022_01 (in_force [2022-01-01, 2022-07-01), apl/01-sources.law:228) с одной таблицей для обоих абзацев D. 832-26 (apl/sources/fr-apl/arrete-2022-01.txt:119); их L0/E0 — вторая таблица b) редакции с 01.07.2022 (arrete-2022-07.txt:123-124). Реплика их чтения нашей же цепочкой D. 842-15 (K = 0,43, L = 320,73, C = 54,22 — у обоих РАВНО): 0,43 × (374,95 − 307,97) = 28,8014; − минорация ст. 41 5 € = 23,8014; шаг взносов (0,5 %: 0,119007; 23,682393 → 23 €; + 0,119007) = 23,119007 → их 23,12. Наше по тексту: 0,43 × (374,95 − 365,7683) = 3,948131 − 5 = −1,051869 (проба aide_foyer_apres_minoration) — пособия нет: aide_non_versee TRUE_ONLY, суммы aide_mensuelle у нас нет
apl_logement_foyer-castest3 | `equivalence_loyer_eligible` | 350 | **РАВНО** | 350
apl_logement_foyer-castest3 | `plafond_equivalence_loyer` | 444.43 | **РАВНО** | 444.43
apl_logement_foyer-castest3 | `equivalence_loyer_minimale` | 98.95 | **РАВНО** | 98.95
apl_logement_foyer-castest3 | `coefficient_prise_en_charge` | 0.64 | **РАВНО** | 0.64
apl_logement_foyer-castest3 | `aide_mensuelle` | 154.78 | **РАВНО_ДО_САНТИМА** | наше 154.77836, их 154.78
apl_logement_foyer-castest4 | `equivalence_loyer_eligible` | 350 | **РАВНО** | 350
apl_logement_foyer-castest4 | `plafond_equivalence_loyer` | 446.30 | **РАВНО** | 446.3
apl_logement_foyer-castest4 | `equivalence_loyer_minimale` | 98.95 | **РАВНО** | 98.95
apl_logement_foyer-castest4 | `coefficient_prise_en_charge` | 0.64 | **РАВНО** | 0.64
apl_logement_foyer-castest4 | `aide_mensuelle` | 154.78 | **РАВНО_ДО_САНТИМА** | наше 154.77836, их 154.78
apl_logement_foyer-castest5 | `equivalence_loyer_eligible` | 350 | **РАВНО** | 350
apl_logement_foyer-castest5 | `plafond_equivalence_loyer` | 446.30 | **РАВНО** | 446.3
apl_logement_foyer-castest5 | `equivalence_loyer_minimale` | 124.64 | **(б) их дефект против текста** | наше 115.19, их 124.64, разница -9.45 — (б) их дефект против текста: месяц права 05.2022 — редакция ст. 31 арретэ ARRETE_ED2022_01 (in_force [2022-01-01, 2022-07-01), apl/01-sources.law:228) с ОДНОЙ таблицей для обоих абзацев D. 832-26 («mentionnés à l'article D. 832-26», apl/sources/fr-apl/arrete-2022-01.txt:119) и форфейтом 76,32 второго абзаца; их число — вторая таблица b) редакции с 01.07.2022 (arrete-2022-07.txt:123-124: 0 % до 1 423,03; 2,40 %; 20,80 %; 23,20 %; 32,80 %). Реплика их чтения: N = 1,2; Σ транш b) × N = 1 419,415008 + 76,32 = 1 495,735008, /12 = 124,6446 → 124,64; наше по тексту: Σ транш первой таблицы × 1,2 = 1 305,92736 + 76,32 = 1 382,24736, /12 = 115,18728 (под D-82 — 115,19)
apl_logement_foyer-castest5 | `coefficient_prise_en_charge` | 0.6 | **РАВНО** | 0.6
apl_logement_foyer-castest5 | `aide_mensuelle` | 129.65 | **(б) их дефект против текста** | наше 135.67943, их 129.65, разница 6.02943 — (б) следствие строки equivalence_loyer_minimale того же дела: редакция ст. 31 арретэ ARRETE_ED2022_01 (in_force [2022-01-01, 2022-07-01), apl/01-sources.law:228) с одной таблицей для обоих абзацев D. 832-26 (apl/sources/fr-apl/arrete-2022-01.txt:119); их L0/E0 — вторая таблица b) редакции с 01.07.2022 (arrete-2022-07.txt:123-124). Реплика их чтения нашей же цепочкой D. 832-24 (K = 0,6 и E = 350 — у обоих РАВНО): K × (E − E0) = 0,6 × (350 − 124,64) = 135,216; − минорация ст. 28 5 € = 130,216; шаг взносов D. 823-16 (0,5 %: 0,65108; 129,56492 → 129 €; + 0,65108) = 129,65108 → их 129,65. Наше по тексту: 0,6 × (350 − 115,19) = 140,886 − 5 = 135,886 → 135 + 0,67943 = 135,67943
calculette_globale-exemple2 | `éligibilité` | vrai | **НЕ_ПЕРЕНОСИТСЯ** | право на пособие и выбор вида пособия (их калькулятор) пакет не выводит — граница fr.apl
calculette_globale-exemple2 | `aide_mensuelle` | 230.63 | **РАВНО_ДО_САНТИМА** | наше 230.625, их 230.63
calculette_globale-exemple1 | `éligibilité` | vrai | **НЕ_ПЕРЕНОСИТСЯ** | право на пособие и вид пособия выводит их калькулятор (гражданство, состав, CSS) — пакет право не выводит, граница fr.apl
calculette_globale-exemple1 | `montant_versé` | 245,23 € | **НЕ_ПЕРЕНОСИТСЯ** | ребёнок в garde alternée с коэффициентом 0,7: их калькулятор смешивает два расчёта (с ребёнком и без) по позиции Conseil d'État (их autres_sources.catala_fr), нормы этой пропорции в закреплённом тексте пакета нет; право и вид пособия (APL у bailleur social) выводит их калькулятор — не переносится
couverture_temporelle-couvertureapllocatifm-tropole | `calcul_sans_exception` | 16 дат 2023-10-01…2027-07-01 | **НЕ_ПЕРЕНОСИТСЯ** | тест без утверждения о значении (их «Avertissement»: «aucune assertion sur les valeurs calculées»): проверяет лишь, что их движок не падает на 16 датах; утверждения о числе нет — сверять нечего
couverture_temporelle-couvertureapllocatifcolocation | `calcul_sans_exception` | 16 дат 2023-10-01…2027-07-01 | **НЕ_ПЕРЕНОСИТСЯ** | тест без утверждения о значении (их «Avertissement»: «aucune assertion sur les valeurs calculées»): проверяет лишь, что их движок не падает на 16 датах; утверждения о числе нет — сверять нечего
couverture_temporelle-couvertureapllocatifdrom | `calcul_sans_exception` | 16 дат 2023-10-01…2027-07-01 | **НЕ_ПЕРЕНОСИТСЯ** | тест без утверждения о значении (их «Avertissement»: «aucune assertion sur les valeurs calculées»): проверяет лишь, что их движок не падает на 16 датах; утверждения о числе нет — сверять нечего
eligibilite_apl-exemple1 | `éligible` | — | **НЕ_ПЕРЕНОСИТСЯ** | право на пособие не выводится
eligibilite_apl-exemple2 | `éligible` | AL.TypeÉligibilitéAllocationLogement.AllocationLogementFamiliale | **НЕ_ПЕРЕНОСИТСЯ** | право на пособие не выводится
eligibilite_apl-exemple3 | `éligible` | AL.TypeÉligibilitéAllocationLogement.AllocationLogementFamiliale | **НЕ_ПЕРЕНОСИТСЯ** | право на пособие не выводится

## Как читать

Их числа — только ожидания; нормативные числа — закреплённые параметры и тексты пакета. Context каждого сценария — `interpretation PpPlancherFinal` (обязательная группа exactly_one, D-78) и `interpretation ArrondiCentimeHalfUp` (D-82: деление без политики в тексте — до сантима HALF_UP; пропорция D. 823-16 и E0 «divisé par douze» D. 832-26). Формула K фойе (D. 832-25, через текст R. 351-61 / R. 351-61-1) принята D-83 и считается правилами `04-calcul-foyer.law`; их r и cm (ст. 30 арретэ) сверяются с закреплёнными `bareme/CoefficientRFoyer`, `bareme/CoefMultiplicateurFoyerGeneral` на дату дела, сценарий для параметра не пишется.

Классы: РАВНО; РАВНО_ДО_САНТИМА (наше точное, их — до сантима; сценарий закрепляет НАШЕ число, их — в шапке); РАВНО_ПО_ПРОЧТЕНИЮ (D-85: строка РАСХОДИТСЯ или РАВНО_ДО_САНТИМА получает вторую пробу без `ArrondiCentimeHalfUp`; класс ставится, только если без прочтения наше равно их числу); (а) граница — наш ответ отказ или нет вывода, и причина — у нас (граница текста или пакета); (б) их дефект против текста — с цитатой закреплённого текста, их числом, нашим и репликой их чтения; (в) дата — нет строк; НЕ_ПЕРЕНОСИТСЯ — с причиной.

**Вторая проба (D-85).** Её получили 36 строк: все 31 РАВНО_ДО_САНТИМА и 5 строк РАСХОДИТСЯ до квалификации (`manifest.json`, поле `without_probe`). Ни одна не стала равной их числу без прочтения: РАВНО_ПО_ПРОЧТЕНИЮ — 0 строк. Прочтение D-82 меняет наш ответ лишь через E0 фойе (E0 CasTest5: 115,18728 → 115,19; итоги CasTest1: 12,060842807 → 12,0608335, CasTest3/4: 154,7783591424 → 154,77836) и в пределах сантима к их числу его не приближает и не удаляет.

## Квалификация расхождений

**(б) Таблица ст. 31 арретэ с 01.07.2022 применена к маю и апрелю 2022 года — 6 строк** (L0/E0 и их следствие в итоге). Текст месяца права — редакция ст. 31 `ARRETE_ED2022_01` (in_force [2022-01-01, 2022-07-01), `apl/01-sources.law:228`): одна таблица для обоих абзацев D. 832-26 — «mentionnés à l'article D. 832-26» (`apl/sources/fr-apl/arrete-2022-01.txt:119`); вторая таблица b) «Au deuxième alinéa» (0 % до 1 423,03; 2,40 %; 20,80 %; 23,20 %; 32,80 %) появляется только в редакции с 01.07.2022 (`arrete-2022-07.txt:120,123-124`, `ARRETE_ED2022_07` in_force [2022-07-01, 2023-01-01)). Их числа воспроизводятся этой второй таблицей до цента: apl CasTest5 E0 124,64 (наше 115,18728, под D-82 — 115,19), al CasTest1 L0 124,64 (наше 115,18728), apl CasTest2 L0 307,97 (наше 365,7683). Итоги тех же дел — следствие, реплика их чтения нашей же цепочкой D. 832-24 / D. 842-15 (K, E/L, C у обоих РАВНО; минорация ст. 28/41 — 5 €; шаг взносов D. 823-16): CasTest5 0,6 × (350 − 124,64) − 5 → 129,65108 → их 129,65 (наше 135,67943); al CasTest1 0,6 × (206,40 + 54,22 − 124,64) − 5 → 76,38294 → их 76,38 (наше 81,41129816); apl CasTest2 0,43 × (374,95 − 307,97) − 5 → 23,119007 → их 23,12 (наше: 0,43 × 9,1817 − 5 = −1,051869, пособия нет, `aide_non_versee` TRUE_ONLY). Промежуточные суммы нашей цепочки сняты пробами `aide_foyer_formule` / `aide_foyer_apres_minoration` / `forfait_charges_foyer` того же оракула.

**(а) — наши границы и дефект, 4 строки класса и описание без исправления.**
- L0 «le total étant divisé par douze» (D. 832-26 2-й абзац, `cch-2021-01.txt:94`) для сектора приобретения десятично непредставим, а прочтение D-82 L0 не покрывает (D-82 «Не покрыто: L0 фойе и приобретения») — наш ответ отказ `INEXACT_DIVISION` (§58): al_accession Exemple1 `mensualite_minimale_al` (их 267,90), apl_accession Exemple2 `mensualite_minimale` (их 367,42).
- Колонки c) «amélioré par l'occupant» у подслучаев ст. 18 арретэ после 30.09.2017 нет (`05-calcul-accession.law:457-460`): плафон для заёмов 2019 года на такое жильё правило не производит — apl_accession Exemple2 и Exemple4 `mensualite_eligible` (их 399,20, выбор колонки b)).
- **(а) дефект, описан, не исправлен:** K аллокаций сектора приобретения (D. 842-6: «calculé selon les dispositions du 2° de l'article D. 832-25») пакет не выводит, хотя функция `coefficient_k_jeunes_travailleurs` после D-83 есть (`04-calcul-foyer.law:932`); комментарий «КОЭФФИЦИЕНТА K НЕТ … формула 2° D. 832-25 … картинкой» в `06-calcul-accession-al.law:18-20` устарел. Правило не заведено в этом проходе: итог сектора всё равно упирается в L0 (граница выше), а дела Catala — заморские (главы IX–X арретэ вне охвата сектора); строки al_accession Exemple1/2 `coefficient_prise_en_charge`, `montant`, `aide_finale_formule_initiale` — НЕ_ПЕРЕНОСИТСЯ с этой причиной.
- K D. 832-11 (APL, приобретение) по-прежнему вне пакета: алгебра отменённой R. 351-19 не закреплена (D-83 приняла только формулу фойе).

## Было (ebe5e7c2, `REPORT-ebe5e7c2.md`) → стало (2694b17)

Класс | ebe5e7c2 | 2694b17
--- | --- | ---
РАВНО | 47 | 59
РАВНО_ДО_САНТИМА | 30 | 31
РАВНО_ПО_ПРОЧТЕНИЮ | — | 0
(а) граница / ГРАНИЦА | 5 | 4
(б) их дефект против текста / РАСХОДИТСЯ_(б) | 3 | 6
НЕ_ПЕРЕНОСИТСЯ | 35 | 29
ДЕЛО_ВНЕ_ТАБЛИЦЫ | 4 | 0
Всего строк | 124 | 129

- Формула K фойе (D-83): K шести дел фойе — РАВНО (было НЕ_ПЕРЕНОСИТСЯ), r и cm CasTest1 — РАВНО закреплённым параметрам; итоги фойе впервые исполнены: apl CasTest1/3/4 — РАВНО_ДО_САНТИМА (12,0608335 / 12,06; 154,77836 / 154,78), al CasTest1, apl CasTest2, CasTest5 — (б) как следствие таблицы ст. 31.
- Прочтение D-82: E0 apl CasTest1/3/4 — РАВНО (было РАВНО_ДО_САНТИМА); al_accession Exemple1 `mensualite_eligible_al` — РАВНО 375,20 (было ГРАНИЦА: отказ `INEXACT_DIVISION`).
- (б) прежние три строки — тот же дефект, теперь с цитатой и репликой; к ним добавлены три итога.
- Новое в 2694b17: `tests_calculette_globale` (Exemple2 перенесён таблицей `catala.manual` плоскими входами — РАВНО_ДО_САНТИМА 230,625 / 230,63; Exemple1 и утверждения `éligibilité` — НЕ_ПЕРЕНОСИТСЯ: право и вид пособия выводит их калькулятор), `tests_couverture_temporelle` (3 scope без утверждения о значении — НЕ_ПЕРЕНОСИТСЯ). Дела `eligibilite_apl` прежде одной строкой ДЕЛО_ВНЕ_ТАБЛИЦЫ, теперь — строка на утверждение (`claim_rows`).
- Плафоны AF D-81 к fr.apl не относятся (их применяет сверка fr.pf.af, `pf-af/tests/foreign/catala/REPORT.md`).

Сценарии: РАВНО — с их числом, РАВНО_ДО_САНТИМА — с нашим точным числом и их в шапке (`corpus/tools/foreign/finalize.py`); оба — в наборе `fr.apl#catala-import` (82 сценария). Исключение — шесть сценариев K фойе (`*-coefficient-prise-en-charge*`, Decimal 0,41…0,64): у оракула РАВНО, а lawc отвечает NEITHER — дефект ядра D-11 (сравнение `truth()` с Decimal; тот же, что у шести известных отказов `nombre-parts`/`coefficient-depense-nette`); они вручную отложены в `diverging/*.lawtest.off` с этой причиной до исправления D-11. (а) и (б) — `diverging/*.lawtest.off` с классом и причиной в шапке, в `[tests]` не входят.
