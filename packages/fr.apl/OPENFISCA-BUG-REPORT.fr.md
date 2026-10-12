# Aides au logement : distinguer montant calculé, CRDS et montant versé

Révision du 16 septembre 2026 (première révision : 14 septembre). Document de
travail **non envoyé**. La révision du 14 septembre retire la qualification
antérieure de « quatre défauts démontrés » pour la comparaison des montants
finaux : les résultats comparés ne représentaient pas la même étape. La
révision du 16 septembre ajoute une comparaison sur un échantillon de
2 000 ménages synthétiques à une étape commune, avec deux observations
nouvelles sur le code (section « Comparaison sur échantillon »).

## Périmètre vérifié

Deux cas synthétiques, Cas 8 et Cas 10, du fichier
`tests/formulas/aides_logement_reforme_janvier_2021.yaml`, période janvier 2021,
ont été exécutés sans modifier leurs entrées. Environnement : OpenFisca-France
176.0.9, OpenFisca-Core 44.7.1, NumPy 2.3.5, Python 3.13.13.
Le module installé `aides_logement.py` est identique octet par octet à celui du
[commit b2ab994331f6f35706bbe789ca015b422202530a](https://github.com/openfisca/openfisca-france/tree/b2ab994331f6f35706bbe789ca015b422202530a).
L'ensemble de l'arbre n'a pas fait l'objet de cette vérification.

| Observation | Cas 8 | Cas 10 |
|---|---:|---:|
| Valeur attendue dans le test | 417,48 € | 219,58 € |
| `aide_logement`, affiché au centime | 417,28 € | 220,79 € |
| Base avant retenue effective de CRDS | 419,3725891113281 € | 221,89999389648438 € |
| Valeur absolue de `crds_logement` | 2,09686279296875 € | 1,1094999313354492 € |

La marge relative de 1 % accepte ces écarts. Le décalage entre les attentes
et le code est confirmé pour ces deux cas ; le choix de tolérance n'est pas,
à lui seul, un défaut juridique.

## Retenue effective et calcul du droit

La somme représentative des contributions dans
[D. 823-16](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038878905/2026-04-12)
ne se confond pas avec la retenue effective prévue par
[l'article 14 III de l'ordonnance n° 96-50](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038834962).
Notre sortie `aide_mensuelle` n'effectue pas cette retenue séparée ni
l'arrondi final du versement. La comparer directement à une sortie nette de
CRDS ne permet donc pas de mesurer une erreur de versement d'OpenFisca.

Le [guide ministériel de septembre 2021](https://www.ecologie.gouv.fr/sites/default/files/publications/les_aides_personnelles_au_logement_element_de_calcul_septembre_2021.pdf),
applicable aux calculs de janvier à septembre 2021, décrit la RLS avant la
retenue effective, la troncature de la CRDS au centime et l'arrondi du
versement à l'euro inférieur (pages 22–23 et 50). Le guide constitue une
explication officielle ; il ne remplace ni le texte normatif ni une décision
individuelle de la CAF/MSA.

En appliquant uniquement cette finalisation aux bases mesurées dans OpenFisca :

| Reconstruction, non décision CAF/MSA | Cas 8 | Cas 10 |
|---|---:|---:|
| CRDS tronquée au centime | 2,09 € | 1,10 € |
| Solde après retenue | 417,2825891113281 € | 220,79999389648438 € |
| Versement arrondi à l'euro inférieur | 417 € | 220 € |

Les valeurs de CRDS d'OpenFisca sont ici supérieures de moins d'un centime
aux valeurs tronquées. Ces deux cas ne montrent pas de sous-prélèvement.
L'exemple pédagogique page 24 donne une base de 346,53 € et un versement de
344 € : la vérification du dernier stade donne 1,73 € de CRDS puis 344,80 €,
arrondis à 344 €. La totalité des calculs intermédiaires de cet exemple n'a
pas été réconciliée ; aucune conformité complète n'est revendiquée.

## Comparaison sur échantillon à une étape commune (16 septembre 2026)

Pour éviter de comparer des étapes différentes, 2 000 ménages synthétiques
(locataires, période janvier 2021, même commit `b2ab9943`) ont été calculés
par les deux systèmes avec les mêmes entrées fournies **à la même étape** :
`aide_logement_base_ressources` (déjà arrondie à la centaine d'euros
supérieure, cet arrondi vivant dans votre formule de base), `al_nb_personnes_a_charge`,
`zone_apl`, `loyer`, `logement_conventionne`, `reduction_loyer_solidarite = 0`.
Ce gabarit d'entrée reproduit au centime les cas 8 et 10 de votre fichier
(417,28 € et 220,79 €). L'étape comparée est `aide_logement_montant_brut`
(après dégressivité et minoration forfaitaire, avant RLS et CRDS) contre
notre `aide_apres_minoration`. Métropole, location vide, logement ordinaire,
sans AAH/AEEH ; les autres ménages sont comptés hors contrat, non comme des
écarts.

| Étape commune, 728 ménages comparables | |
|---|---:|
| écart moyen (nous − OpenFisca) | +0,005 € |
| écart absolu moyen | 0,054 € |
| égalité exacte | 116 ménages |
| écart ≤ 1 centime | 563 ménages (77 %) |
| écart maximal | 0,50 € |
| écarts non attribués | 0 |

Chaque écart est reproduit par une réplique de votre lecture (cinq
différences ci-dessous), ce qui n'établit ni l'exhaustivité des causes ni
une conformité juridique. Aux quatre différences déjà décrites (CRDS par
multiplication, ordre RLS/CRDS, loyer arrondi à l'euro, P0/Pp au centime)
s'ajoute une cinquième, invisible sur vos douze cas car elle ne joue que sur
les égalités :

- **Arrondis `round_` à la valeur paire.** `aide_logement_loyer_reel` arrondit
  214,50 € à 214 € ; `aide_logement_taux_loyer` arrondit 0,001125 à 0,00112.
  Les textes disent « arrondi » sans règle explicite ; notre lecture applique
  la demi-unité vers le haut. Reproduction : couple, 3 personnes à charge,
  zone 1, loyer 214,50 €, base 2 400 € (2 336,79 € arrondie) →
  `aide_logement_montant_brut` 264,47 € ; avec 215 € de loyer on obtient
  264,97 €. Couple, 3 personnes à charge, zone 3, loyer 322,09 €, base
  23 300 € → participation personnelle 353,07 € (TL 0,00112) contre 353,22 €
  (TL 0,00113). Effet : au plus un demi-centime de taux et un demi-euro de
  loyer, uniquement sur les égalités.

Deuxième observation, sur l'ordre des opérations :

- **Seuil de versement avant dégressivité et minoration.**
  `aide_logement_montant_brut_avant_degressivite` annule le montant sous le
  seuil de versement avant l'application du coefficient de dégressivité et
  de la minoration forfaitaire ; le seuil se rapporte pourtant au montant à
  verser. Sur l'échantillon, deux ménages sont concernés et leur résultat
  final coïncide (pas de versement dans les deux systèmes) ; un écart de
  résultat n'apparaîtrait que pour un montant au-dessus du seuil avant
  minoration et en dessous après. Ceci est une observation d'ordre, non un
  écart chiffré.

Outil et contrat de comparabilité : `verify/ci/tools/compare_openfisca_bank.py`
et le [rapport](../../../../docs/journal/reports/2026-09-16/2026-09-16-openfisca-bank-comparison.ru.md)
(données complètes dans `docs/journal/reports/2026-09-16-openfisca-bank/`). Cette
comparaison porte sur des modèles ; elle ne dit rien des montants versés par
les CAF/MSA.

## Questions restantes et résultats historiques

- Préciser la destination des sorties nettes et la place des arrondis de
  retenue et de versement dans les usages concernés.
- Vérifier le fondement de l'arrondi du loyer à l'euro. Une référence à
  CSS D. 542-30 abrogé ne prouve pas l'absence d'un autre fondement.
- Retirer l'explication par un « type monétaire au centime » pour P0/Pp : les
  valeurs observées sont des float32 sans arrondi explicite au centime.
- Refaire la qualification juridique des écarts sur des étapes comparables.

La comparaison du 13 septembre portait sur neuf cas, avec une réplique
numérique concordant au centime, et signalait un décalage des attentes dans
douze cas sur douze. Ces mesures restent historiques : seuls deux cas ont
été réexécutés ici. Une réplique numériquement concordante ne démontre pas
l'exhaustivité des causes ni la conformité juridique. Les observations
séparées sur les paramètres n'ont pas été réévaluées dans cet audit.

Aucune donnée de paiement individuel CAF/MSA ni preuve d'utilisation de cette
version dans une chaîne réelle de versement n'a été obtenue. Aucun manque à
gagner public ne peut être chiffré à partir de ces résultats.

Les valeurs complètes, empreintes des sources et scripts de reproduction sont
conservés dans le [dossier d'audit](../../../../docs/journal/reports/2026-09-14/2026-09-14-openfisca-caf-crds-audit.ru.md).
Les normes exécutables et les attentes de tests de `fr.apl` n'ont pas été
modifiées lors de cette révision documentaire.
