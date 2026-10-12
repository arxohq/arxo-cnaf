# Дела Catala (CatalaLang/catala-examples@2694b17d) против fr.pf.af

Класс | дел
--- | ---
(б) их дефект против текста | 3
НЕ_ПЕРЕНОСИТСЯ | 6
РАВНО | 7
РАВНО_ДО_САНТИМА | 2

дело | цель | их | класс | подробность
--- | --- | --- | --- | ---
allocations_familiales-test1 | `montant_parent_partage` | 351.54 | **(б) их дефект против текста** | документ NON_EXECUTABLE: NONEXACT_NARROWING — NONEXACT_NARROWING: rule urn:fr:corpus:clir:pf-af#CoefficientPartage: head computation — urn:fr:corpus:clir:pf-af#coefficient_partage.arg1.return: cannot narrow Number 5/6 to Decimal: not exact (no si — см. «Квалификация расхождений», Test1/Test7
allocations_familiales-test2 | `af_montant_du` | 216.46 | **РАВНО** | 216.46
allocations_familiales-test3 | `af_montant_du` | 24.37 | **РАВНО** | 24.37
allocations_familiales-test4 | `montant_parent_partage` | 99.46 | **РАВНО_ДО_САНТИМА** | наше 99.4575, их 99.46
allocations_familiales-test5 | `af_montant_du` | 0.00 | **РАВНО** | у обоих нет выплаты
allocations_familiales-test6 | `af_montant_du` | 66.30 | **(б) их дефект против текста** | наше 24.37, их 66.30, разница -41.93 — см. «Квалификация расхождений», Test6
allocations_familiales-test7 | `montant_parent_partage` | 417.84 | **(б) их дефект против текста** | документ NON_EXECUTABLE: NONEXACT_NARROWING — NONEXACT_NARROWING: rule urn:fr:corpus:clir:pf-af#CoefficientPartage: head computation — urn:fr:corpus:clir:pf-af#coefficient_partage.arg1.return: cannot narrow Number 5/6 to Decimal: not exact (no si — см. «Квалификация расхождений», Test1/Test7
allocations_familiales-test8 | `af_montant_du` | 197.90 | **РАВНО** | 197.9
allocations_familiales-test9 | `famille_percoit` | 0 | **РАВНО** | у обоих нет выплаты
allocations_familiales-test10 | `montant_parent_partage` | 99.46 | **РАВНО_ДО_САНТИМА** | наше 99.4575, их 99.46
allocations_familiales-test11 | `af_montant_du` | 435.55 | **РАВНО** | 435.55
allocations_familiales-test12 | `i_montant_versé` | 315.84 | **НЕ_ПЕРЕНОСИТСЯ** | Майотта: AF там — режим ордонанса 2002-149 (пакет fr.pf.mayotte), fr.pf.af Майотту не покрывает (B-PFAF-MAYOTTE)
allocations_familiales-test13 | `i_montant_versé` | 34.99 | **НЕ_ПЕРЕНОСИТСЯ** | Майотта: AF там — режим ордонанса 2002-149 (пакет fr.pf.mayotte), fr.pf.af Майотту не покрывает (B-PFAF-MAYOTTE)
allocations_familiales-test14 | `af_montant_du` | 48.77 | **РАВНО** | 48.77
ouverture_droits-test1 | `droit_ouvert(enfant1)` | vrai | **НЕ_ПЕРЕНОСИТСЯ** | наша цель — fr.pf.core::enfant_ouvre_droit (пакет fr.pf.core, вне fr.pf.af): её правила L. 512-3 / R. 512-2 действуют с 01.01.2021 (pf-core/02-enfant-charge.law, EnfantScolarite/EnfantVingtAns), а дело — 01.05.2020, и SMIC 2020 не закреплён; в делах AF той же квалификацией пользуется таблица переноса (с причиной у каждого ребёнка)
ouverture_droits-test1 | `droit_ouvert(enfant2)` | faux | **НЕ_ПЕРЕНОСИТСЯ** | наша цель — fr.pf.core::enfant_ouvre_droit (пакет fr.pf.core, вне fr.pf.af): её правила L. 512-3 / R. 512-2 действуют с 01.01.2021 (pf-core/02-enfant-charge.law, EnfantScolarite/EnfantVingtAns), а дело — 01.05.2020, и SMIC 2020 не закреплён; в делах AF той же квалификацией пользуется таблица переноса (с причиной у каждого ребёнка)
ouverture_droits-test1 | `droit_ouvert(enfant3)` | vrai | **НЕ_ПЕРЕНОСИТСЯ** | наша цель — fr.pf.core::enfant_ouvre_droit (пакет fr.pf.core, вне fr.pf.af): её правила L. 512-3 / R. 512-2 действуют с 01.01.2021 (pf-core/02-enfant-charge.law, EnfantScolarite/EnfantVingtAns), а дело — 01.05.2020, и SMIC 2020 не закреплён; в делах AF той же квалификацией пользуется таблица переноса (с причиной у каждого ребёнка)
ouverture_droits-test1 | `droit_ouvert(enfant4)` | faux | **НЕ_ПЕРЕНОСИТСЯ** | наша цель — fr.pf.core::enfant_ouvre_droit (пакет fr.pf.core, вне fr.pf.af): её правила L. 512-3 / R. 512-2 действуют с 01.01.2021 (pf-core/02-enfant-charge.law, EnfantScolarite/EnfantVingtAns), а дело — 01.05.2020, и SMIC 2020 не закреплён; в делах AF той же квалификацией пользуется таблица переноса (с причиной у каждого ребёнка)

## Как читать

Их числа — только ожидания. Нормативные суммы — закреплённые: BMAF и плафоны D. 521-3 (опубликованные база и надбавка, D-81) — фрагменты `fr.css.revalorisation` через `tools/openfisca_hook.py` (2020-04…2021-03: 414,40 € `DSS_SD2B_2020_33_BMAF`; 2021-04: 414,81 €; 2022-04: 422,28 €; плафоны 2020 — 57 759 / 80 831 + 5 775, `DSS_SD2B_2019_261_PLAFOND_AF`); база L. 755-3 в DOM — та же BMAF (L. 755-3 al. 2, `corpus/laws/fr/pf-dom/01-sources.law:129`). Context — `deadline_policy AGE_ATTEINT; interpretation ArrondiLignesDss` (D-83). Счёт надбавок и forfait (B-PFAF-COMPTAGE) — предварительные пробы самого пакета (`majoration_eligible`, `montant_forfait`; список проб — `montant-verse/manifest.json`, поле `counts`). Кто из детей открывает право (L. 512-3, R. 512-2), задаёт таблица `tools/foreign-map.json` с причиной у каждого ребёнка; SMIC 2020 в корпусе не закреплён — для дел 2020 года это отмечено в причине.

Классы: РАВНО; РАВНО_ДО_САНТИМА (наше точное, их — до сантима); РАВНО_ПО_ПРОЧТЕНИЮ (D-85: без прочтения наш ответ равен их числу — вторая проба); (б) их дефект против текста; НЕ_ПЕРЕНОСИТСЯ. Вторую пробу без `ArrondiLignesDss` получили Test4, Test6, Test10: равенства без прочтения нет, класс прежний.

## Квалификация расхождений

**Test1 и Test7 — (б) их дефект против текста: надбавка за возраст ребёнку, который права не открывает.** Текст: «Chacun des enfants à charge, à l'exception du plus âgé, ouvre droit … à une majoration» (L. 521-3 al. 1, `pf-af/sources/css/L521-3.txt:2`); «à charge» для AF — ребёнок, открывающий право: после обязательного обучения — пока заработок не выше плафона (L. 512-3 2°, `pf-core/sources/css/L512-3.txt:4`) и до двадцати лет (R. 512-2 al. 1, `pf-core/sources/css/R512-2.txt:2`). Ребёнок 2001: в Test1 (05.2020) ему 19 лет при заработке 1 100 € выше плафона 55 % SMIC × 169 (R. 512-2 al. 2, `R512-2.txt:3`; 952,66 € по первому закреплённому SMIC 01.01.2021; их модель — 943,02 €); в Test7 (02.2021) ему уже 20 лет. Реплика их чтения (их модель: сумма надбавок — по ВСЕМ детям ввода, `allocations_familiales/epilogue.catala_fr:42`; `droit_ouvert_majoration` проверяет только возраст и старшинство, `securite_sociale_L.catala_fr:315,332`), BMAF 414,40: база трёх детей 132,61 + 169,90 = 302,51 × 2,5/3 (R. 521-3) = 252,09; надбавка ребёнка 2003 в résidence alternée 66,30 × ½ = 33,15; надбавка ребёнка 2001 — 66,30. Test1: 252,09 + 33,15 + 66,30 = **351,54** (их); Test7: + надбавка ребёнка 2007 (14 лет) 66,30 = **417,84** (их). Их же база считает троих (ребёнка 2001 нет среди `enfants_à_charge_droit_ouvert_prestation_familiale`, `securite_sociale_L.catala_fr:87-89`) — модель противоречит сама себе. Наш ответ: доля родителя R. 521-3 = 5/6 десятично непредставима — отказ `NONEXACT_NARROWING` (граница: доля 5/6 не покрыта D-82/D-83, решение владельца не принято); без этой границы наша сумма всё равно не содержала бы 66,30 за ребёнка 2001. Заметка о структуре: наш `MontantParent` умножает на коэффициент R. 521-3 месячную сумму ВМЕСТЕ с надбавками (`02-allocataire-partage.law:212-219`), их модель — только базу, а надбавку ребёнка в résidence alternée делит пополам (R. 521-4 al. 2); в Test4/Test10 надбавок нет и вопрос не проявляется — открыт владельцу.

**Test6 — (б) их дефект против текста: ребёнок, который родится после месяца права, посчитан на иждивении.** Ребёнок с датой рождения 25.09.2020 в деле на 01.05.2020: «ouvre droit … tout enfant» (L. 512-3, `pf-core/sources/css/L512-3.txt:2-3`) и «charge effective et permanente» (L. 513-1) предполагают рождённого ребёнка. Их модель выводит «obligation scolaire: Avant» из `date_de_naissance + 3 an >= date_courante` (`allocations_familiales/epilogue.catala_fr:123`) — истинно и для отрицательного возраста, — и считает двоих. Реплика их чтения: двое детей в Гваделупе — ставки D. 521-1 (D. 755-5 I), ресурсы 78 830 € между плафоном I (57 759 + 2 × 5 775 = 69 309) и II (80 831 + 2 × 5 775 = 92 381) — полоса 2: 16 % × 414,40 = **66,30** (их). Наше по тексту: один ребёнок в DOM — 5,88 % базы L. 755-3 (D. 755-5 II, `pf-af/sources/css/D755-5.txt:3`), без модуляции (L. 755-12 al. 2) = **24,37**; ребёнок младше 11 лет и старший — надбавки нет.

**Test4, Test10 — РАВНО_ДО_САНТИМА.** Доля R. 521-3 = 1,5/2 = 0,75 точна: 132,61 × 0,75 = 99,4575 (наше), их 99,46 (денежный тип Catala). Без прочтения — 132,608 × 0,75 = 99,456: тоже до сантима, РАВНО_ПО_ПРОЧТЕНИЮ не доказывается. Округления доли родителя текст не называет, D-83 его не покрывает.

## Было (рукописный перенос, `tests/foreign/REPORT.md`, без коммита) → стало (2694b17)

дело | было | стало
--- | --- | ---
Test1 | (c) ставка надбавки (структура при BMAF 400) | (б) их дефект против текста — надбавка ребёнку без права; наш ответ — отказ на доле 5/6
Test2 | (a) | РАВНО 216,46
Test3 | (b) база DOM 1 000 € «заявлена» | РАВНО 24,37 (база L. 755-3 = BMAF)
Test4 | (a)/(b) | РАВНО_ДО_САНТИМА 99,4575 / 99,46
Test5 | (c) форма (нет вывода) | РАВНО — у обоих выплаты нет
Test6 | (b) счёт 2 ребёнка «как у них» | (б) их дефект против текста — нерождённый ребёнок; наше 24,37
Test7 | BLOCKED (REQ-PFAF-03) | (б) их дефект против текста — как Test1; дата 02.2021 исполняется
Test8 | BLOCKED (REQ-PFAF-03) | РАВНО 197,90 (полоса 2 + complément dégressif)
Test9 | (a) служба получает 64,00 при двух детях | РАВНО — семья не получает ничего (ребёнок 2001 права не открывает)
Test10 | (b) | РАВНО_ДО_САНТИМА 99,4575 / 99,46
Test11 | (a) | РАВНО 435,55
Test12, Test13 | не переносились | НЕ_ПЕРЕНОСИТСЯ — Майотта (B-PFAF-MAYOTTE)
Test14 | (c) два «домохозяйства» по 58,80 | РАВНО 48,77 (один ребёнок в DOM + надбавка 16 лет; старший — ребёнок 2001)
ouverture_droits | граница | НЕ_ПЕРЕНОСИТСЯ — цель в fr.pf.core, правила с 2021

Рукописные сценарии `catala-test-*.lawtest` (структура при заявленной BMAF 400, их число не несут) остаются регрессией пакета; сверка с числами Catala — сценарии `montant-verse/` (раскладка `corpus/tools/foreign/finalize.py`: РАВНО — с их числом, РАВНО_ДО_САНТИМА Test4/Test10 — с нашим точным 99,4575 и их числом в шапке; эти девять — в наборе `fr.pf.af#bande-taux`; Test1, Test6, Test7 — `montant-verse/diverging/*.lawtest.off`).
