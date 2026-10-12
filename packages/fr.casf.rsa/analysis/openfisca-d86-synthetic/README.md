# D-86: синтетические входы hook OpenFisca RSA

Среди переносимых месячных целей выплаты `rsa` в LexImpact 2024 нет семьи 5+ или majoré с ребёнком младше трёх лет. Цели `rsa_base_ressources` относятся к другой стадии и не подтверждают выплату. Эти три синтетических входа проверяют только контракт адаптера; они не объявляются делами OpenFisca и не сравниваются с его денежным результатом. Нормативный расчёт по полученным фактам покрывают `tests/mf-composition-5-couple.lawtest`, `tests/majore-duree-retard.lawtest`, `tests/majore-prolonge.lawtest`.

Запуск из корня репозитория: `.venv-work-profile/bin/python corpus/laws/fr/rsa/analysis/openfisca-d86-synthetic/hook_probe.py`.

| Вход `Ctx` | Выход / граница |
|---|---|
| Месяц права 2024-06, два родителя 1990-01-01, четыре ребёнка 2018-01-01, `rsa_nb_enfants=4`, все à charge, `rsa_majore_eligibilite=false` | 6 фактов `foyer_membre_rang`, 4 `foyer_enfant_charge`, 4 `foyer_naissance`; отсутствуют готовые `foyer_sup_taux40/30`. Пакет выводит две ставки 40 % по персональным рангам 5–6. |
| Месяц права 2024-06, один родитель 1990-01-01, ребёнок 2023-05-15 à charge, `rsa_majore_eligibilite=true` | `isolement_constate` и `foyer_naissance(..., @2023-05-15)`; `majore_debut_mois` не подаётся. Продление до 3 лет выводит пакет по R. 262-2. |
| Месяц права 2024-06, один родитель 1990-01-01, детей нет, `rsa_majore_eligibilite=true` | `Skip`: нет даты déclaration de grossesse или dépôt de demande. |

В остальных полях заглушки: `rsa_eligibilite=true`, жильё `locataire_vide`, доходы и prestations нулевые. Скрипт выполняет assertions на полные группы фактов и отказ.
