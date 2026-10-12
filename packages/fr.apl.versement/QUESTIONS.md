# Вопросы к пакету `fr.apl.versement`

<!-- Порождено из analysis/questions.json: python3 verify/ci/gates/coverage/check_package_questions.py --emit. Не править руками. -->

Каталог **предусмотренных** запросов §172 и того, чем каждый проверен (DECISION-0190). Карточка не означает положительного ответа по делу: ответ даёт только evaluation-документ с доказательством. Отсутствие карточки означает «не описано каталогом», а не «право молчит».

## Финализация фактически выплачиваемой суммы

Единицы источника: GUIDE_P22_DEGRESSIVITE_RLS, GUIDE_P23_CRDS_ARRONDI, GUIDE_P24_EXEMPLE, GUIDE_P50_ARRONDIS.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `assiette-crds` | Установлено ли, что «база фактического удержания CRDS для финализации выплаты» (m: Menage m, montant: денежная сумма montant)?<br>*авторская формулировка:* Какая сумма после RLS и представительных взносов служит базой удержания CRDS перед выплатой? | truth | `assiette_crds(m: Menage, montant: Money)` | `evaluate truth(assiette_crds(m: <m>, montant: <montant>));` | l'assiette mesurée dans OpenFisca est isolée pour reproduire les deux cas de l'audit (`AssietteAuditOpenFisca`); la somme après RLS et contributions représentatives entre dans la finalisation du versement (`AssietteDepuisAideMensuelle`) | тестов 1 |
| `crds-precomptee` | Установлено ли, что «удерживаемая CRDS, усечённая до нижнего сантима» (m: Menage m, montant: денежная сумма montant)?<br>*авторская формулировка:* Какова удерживаемая CRDS с учётом территории и усечения до нижнего сантима? | truth | `crds_precomptee(m: Menage, montant: Money)` | `evaluate truth(crds_precomptee(m: <m>, montant: <montant>));` | la CRDS au taux de 0,5 % est précomptée et arrondie au centime inférieur (`RetenueCRDSMetropole`); la CRDS au taux de 0,5 % est précomptée et arrondie au centime inférieur (`RetenueCRDSOutreMer`); à Saint-Pierre-et-Miquelon aucune contribution n'est précomptée dans ce calcul (`SansCRDSSaintPierre`) | тестов 2 |
| `montant-verse` | Установлено ли, что «выплачиваемая сумма пособия, округлённая вниз до евро» (m: Menage m, montant: денежная сумма montant)?<br>*авторская формулировка:* Какова фактически выплачиваемая сумма после удержания CRDS и округления вниз до евро? | truth | `montant_verse(m: Menage, montant: Money)` | `evaluate truth(montant_verse(m: <m>, montant: <montant>));` | — | тестов 6 |

- **Не отвечает:** Являются ли правила округления на страницах 23–24 и 50 самостоятельной нормой закона? — открытое прочтение, принятое до решения (GUIDE_P23_CRDS_ARRONDI, GUIDE_P24_EXEMPLE, GUIDE_P50_ARRONDIS). Порядок удержания и округления взят из министерского Guide des aides au logement 2021 как из канона исполнения, а не выдан за текст закона; нормативные акты закрепляют ставку CRDS и территориальную применимость, но найденный корпус закона не содержит той же полной последовательности округлений. Связанный вопрос: `montant-verse`.
- **Не отвечает:** Как согласовать напечатанный промежуточный итог 346,53 евро с арифметическим итогом приведённых слагаемых 346,69420 евро? — открытое прочтение, принятое до решения (GUIDE_P24_EXEMPLE). Официальный пример на странице 24 печатает 346,53 EUR до CRDS, тогда как сложение приведённых там слагаемых даёт 346,69420 EUR; пакет проверяет напечатанный результат как вход стадии выплаты и не выдумывает отсутствующую операцию согласования. Связанный вопрос: `montant-verse`.
- **Не отвечает:** Верно ли рассчитана входная сумма пособия до удержания CRDS? — источник отсылает вовне (GUIDE_P22_DEGRESSIVITE_RLS, GUIDE_P23_CRDS_ARRONDI). Пакет отвечает только за стадию выплаты: расчёт входной суммы после RLS остаётся обязанностью fr.apl; отдельный эмпирический вход assiette_crds_auditee_openfisca существует лишь для воспроизведения аудита и не приписывается CAF/MSA. Связанный вопрос: `assiette-crds`.

## Выводимое без собственной карточки

Звенья вывода: спрашиваются через карточки выше, названы здесь ради полноты поверхности в обе стороны.

| предикат | почему без карточки |
|---|---|
| `decision_non_versement` | Решение импортирует результат aide_non_versee расчётного пакета и проверено отдельным сценарием; самостоятельного локального источника стадии выплаты у него нет. |
| `decision_versement` | Служебное решение выводится из проверяемого montant_verse; отдельный вопрос дублировал бы итоговую карточку выплаты. |
| `montant_net_crds` | Промежуточное звено между проверяемыми crds_precomptee и montant_verse; собственная бизнес-операция отсутствует. |

## Итог

Карточек 3, границ 3, внутренних звеньев 3; выводимых предикатов в CLIR 6, норм 0 — поверхность закрыта в обе стороны. Причины по конкретному делу берутся не из каталога, а из issues и why_not ответа.
