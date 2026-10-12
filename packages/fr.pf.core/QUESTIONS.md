# Questions to the package `fr.pf.core`

<!-- Generated from analysis/questions.json by the catalogue gate (--emit). Do not edit by hand. -->

The catalogue of the §172 queries this package **provides for**, and of what each one is checked by. A card does not mean a positive answer on a case: only an evaluation document with its proof answers. The absence of a card means "not described by the catalogue", not "the law is silent".

## CSS_L511_1

Source units: CSS_L511_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-offrirservicesremuneres` | Which normative positions arose in the case (norms: “Offering services for pre-agreed fees to obtain benefits is prohibited”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «OffrirServicesRemuneres») and what is their status? | positions | norms `OffrirServicesRemuneres` | `evaluate positions(); — expected form position(OffrirServicesRemuneres, <status>)` | — | tests 1 |
| `poziciya-suspendreversementcertificats` | Which normative positions arose in the case (norms: “Payment conditional on certificates (health, schooling): suspension otherwise (period by decree - out of scope)”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «SuspendreVersementCertificats») and what is their status? | positions | norms `SuspendreVersementCertificats` | `evaluate positions(); — expected form position(SuspendreVersementCertificats, <status>)` | — | tests 1 |
| `poziciya-verserprestationsdues` | Which normative positions arose in the case (norms: “The allocataire receives benefits: the debtor body must pay them”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «VerserPrestationsDues») and what is their status? | positions | norms `VerserPrestationsDues` | `evaluate positions(); — expected form position(VerserPrestationsDues, <status>)` | — | tests 2 |

- **Does not answer:** Does the package cover the whole act — does the absence of a card mean the law is silent? — the rule is in the text, the rules are not written yet (CSS_L511_1). Rules are filed for 712 of 973 pinned fragments: the rest are pinned by publication bytes but carry no executable norms. The absence of a card means «no norm in the model», not «the law is silent».
- **Does not answer:** Can a conclusion without a generated scenario be asked? — a limit of the language or of the engine (CSS_L511_1). 4 package conclusions are left without executable witness: their premises contain a disjunction, a text value or a term call, or the head is computed. Such conclusions are recorded in internal and will become cards together with hand-written scenarios.
- **Does not answer:** Are all package positions confirmed by a positive scenario? — the rule is in the text, the rules are not written yet (CSS_L511_1). 2 package norms are confirmed only by a negative scenario («on these facts the position does not arise»): the generating pass could not build a world that activates them. The positive witness is a debt.
- **Does not answer:** What is the last day of the time limit if the case carries no policy and no calendar? — data the case must bring (CSS_L511_1). Time limits are computed by §86 terms: the case must carry a counting policy (ENFANT_VINGT_ANS, PRESCRIPTION_ANNEES, RECOUVREMENT_DELAI), a §85 calendar snapshot and the calendar package itself in the program, otherwise the document answers MISSING_CALENDAR or MISSING_POLICY.

## CSS_L512_2

Source units: CSS_L512_2.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `beneficiaire-plein-droit-etranger` | Is it established that “foreigner in lawful stay receives benefits as of right (L. 512-2)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «beneficiaire_plein_droit_etranger» (p: Personne p)? | truth | `beneficiaire_plein_droit_etranger(p: Personne)` | `evaluate truth(beneficiaire_plein_droit_etranger(<p>));` | — | tests 1 |

## CSS_L512_4

Source units: CSS_L512_4.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `adoption-conforme` | Is it established that “adoption condition for payment met (L. 512-4)” (e: child in respect of whom family benefits are claimed e)?<br>*authored wording:* Is it established that «adoption_conforme» (e: Enfant e)? | truth | `adoption_conforme(e: Enfant)` | `evaluate truth(adoption_conforme(<e>));` | — | tests 1 |

## CSS_L512_5

Source units: CSS_L512_5.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `allocation-differentielle` | Is it established that “differential allowance: difference between French and foreign benefits (L. 512-5)” (p: natural person claiming or receiving family benefits p, montant: monetary amount montant)?<br>*authored wording:* Is it established that «allocation_differentielle» (p: Personne p, montant: Money montant)? | truth | `allocation_differentielle(p: Personne, montant: Money)` | `evaluate truth(allocation_differentielle(<p>, <montant>));` | — | tests 1 |

## CSS_L512_6

Source units: CSS_L512_6.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `droit-metropolitain-ouvert` | Is it established that “entitlement to metropolitan-scheme benefits opened through the metropolitan spouse (L. 512-6 para. 1)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «droit_metropolitain_ouvert» (p: Personne p)? | truth | `droit_metropolitain_ouvert(p: Personne)` | `evaluate truth(droit_metropolitain_ouvert(<p>));` | — | tests 1 |

## CSS_L522_1

Source units: CSS_L522_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `cf-condition-remplie` | Is it established that “complement familial award conditions met (L. 522-1)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «cf_condition_remplie» (p: Personne p)? | truth | `cf_condition_remplie(p: Personne)` | `evaluate truth(cf_condition_remplie(<p>));` | — | tests 1 |

## CSS_L523_2

Source units: CSS_L523_2.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `asf-ouvre-droit` | Is it established that “child opens entitlement to ASF (L. 523-1)” (e: child in respect of whom family benefits are claimed e)?<br>*authored wording:* Is it established that «asf_ouvre_droit» (e: Enfant e)? | truth | `asf_ouvre_droit(e: Enfant)` | `evaluate truth(asf_ouvre_droit(<e>));` | — | tests 2 |

## CSS_L532_1

Source units: CSS_L532_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `cumul-base-cf-refuse` | Is it established that “allocation de base not combined with complement familial (L. 532-1)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «cumul_base_cf_refuse» (p: Personne p)? | truth | `cumul_base_cf_refuse(p: Personne)` | `evaluate truth(cumul_base_cf_refuse(<p>));` | — | tests 1 |

## CSS_L532_2

Source units: CSS_L532_2.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `cumul-prepare-indemnite-refuse` | Is it established that “full-rate PreParE not combined with II payments (L. 532-2 II)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «cumul_prepare_indemnite_refuse» (p: Personne p)? | truth | `cumul_prepare_indemnite_refuse(p: Personne)` | `evaluate truth(cumul_prepare_indemnite_refuse(<p>));` | — | tests 1 |

## CSS_L533_1

Source units: CSS_L533_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `prime-naissance-condition-remplie` | Is it established that “prime a la naissance payment condition met (L. 533-1)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «prime_naissance_condition_remplie» (p: Personne p)? | truth | `prime_naissance_condition_remplie(p: Personne)` | `evaluate truth(prime_naissance_condition_remplie(<p>));` | — | tests 1 |

## CSS_L541_1

Source units: CSS_L541_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `aeeh-ouvre-droit` | Is it established that “AEEH entitlement (L. 541-1, rate by decree - out of scope)” (e: child in respect of whom family benefits are claimed e)?<br>*authored wording:* Is it established that «aeeh_ouvre_droit» (e: Enfant e)? | truth | `aeeh_ouvre_droit(e: Enfant)` | `evaluate truth(aeeh_ouvre_droit(<e>));` | — | tests 1 |

## CSS_L542_9

Source units: CSS_L542_9.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-accorderpretamelioration` | Which normative positions arose in the case (norms: “Schemes may grant improvement loans (conditions and limits by decree - out of scope)”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «AccorderPretAmelioration») and what is their status? | positions | norms `AccorderPretAmelioration` | `evaluate positions(); — expected form position(AccorderPretAmelioration, <status>)` | — | tests 1 |

## CSS_L543_1

Source units: CSS_L543_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `ars-condition-scolarite` | Is it established that “ARS schooling condition met (ceiling by decree - out of scope)” (e: child in respect of whom family benefits are claimed e)?<br>*authored wording:* Is it established that «ars_condition_scolarite» (e: Enfant e)? | truth | `ars_condition_scolarite(e: Enfant)` | `evaluate truth(ars_condition_scolarite(<e>));` | — | tests 1 |

## CSS_L544_10

Source units: CSS_L544_10.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-informerdemandeurajpp` | Which normative positions arose in the case (norms: “The body must inform the AJPP claimant of AEEH and PCH criteria and claim procedure”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «InformerDemandeurAjpp») and what is their status? | positions | norms `InformerDemandeurAjpp` | `evaluate positions(); — expected form position(InformerDemandeurAjpp, <status>)` | — | tests 1 |

## CSS_L544_3

Source units: CSS_L544_3.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `ajpp-dans-limite` | Is it established that “daily allowances do not exceed 310 (L. 544-3 para. 1)” (e: child in respect of whom family benefits are claimed e)?<br>*authored wording:* Is it established that «ajpp_dans_limite» (e: Enfant e)? | truth | `ajpp_dans_limite(e: Enfant)` | `evaluate truth(ajpp_dans_limite(<e>));` | — | tests 2 |

## CSS_L544_9

Source units: CSS_L544_9.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `cumul-ajpp-refuse` | Is it established that “AJPP not combined with the 9 payments and benefits of I of article L. 544-9” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «cumul_ajpp_refuse» (p: Personne p)? | truth | `cumul_ajpp_refuse(p: Personne)` | `evaluate truth(cumul_ajpp_refuse(<p>));` | — | tests 1 |

## CSS_L545_1

Source units: CSS_L545_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `forfait-deces-eligible` | Is it established that “lump-sum death benefit awardable (amount per decree scale indexed on tobacco-free IPC - out of scope)” (p: natural person claiming or receiving family benefits p, e: child in respect of whom family benefits are claimed e)?<br>*authored wording:* Is it established that «forfait_deces_eligible» (p: Personne p, e: Enfant e)? | truth | `forfait_deces_eligible(p: Personne, e: Enfant)` | `evaluate truth(forfait_deces_eligible(<p>, <e>));` | — | tests 1 |

## CSS_L551_1

Source units: CSS_L551_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `base-bmaf-classee` | Is it established that “benefit falls (true) or not (false) under the monthly bases of article L. 551-1” (p: natural person claiming or receiving family benefits p, releve: boolean value releve)?<br>*authored wording:* Is it established that «base_bmaf_classee» (p: Personne p, releve: Boolean releve)? | truth | `base_bmaf_classee(p: Personne, releve: Boolean)` | `evaluate truth(base_bmaf_classee(<p>, <releve>));` | — | tests 2 |

## CSS_L552_6

Source units: CSS_L552_6.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-supporterfraismesure` | Which normative positions arose in the case (norms: “Cost of the measure borne by the paying body (the highest payer where several)”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «SupporterFraisMesure») and what is their status? | positions | norms `SupporterFraisMesure` | `evaluate positions(); — expected form position(SupporterFraisMesure, <status>)` | — | tests 1 |

## CSS_L552_7

Source units: CSS_L552_7.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `ars-due-exceptionnellement` | Is it established that “ARS due despite unmet schooling condition due to death (death on/after 1 June - L. 552-7 para. 4, D. 552-7)” (e: child in respect of whom family benefits are claimed e)?<br>*authored wording:* Is it established that «ars_due_exceptionnellement» (e: Enfant e)? | truth | `ars_due_exceptionnellement(e: Enfant)` | `evaluate truth(ars_due_exceptionnellement(<e>));` | — | tests 1 |
| `prestations-maintenues-deces` | Is it established that “benefits maintained after death for the regulatory period (L. 552-7)” (e: child in respect of whom family benefits are claimed e)?<br>*authored wording:* Is it established that «prestations_maintenues_deces» (e: Enfant e)? | truth | `prestations_maintenues_deces(e: Enfant)` | `evaluate truth(prestations_maintenues_deces(<e>));` | — | tests 1 |

## CSS_L553_1

Source units: CSS_L553_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `action-prescrite` | Is it established that “action (for payment or recovery) time-barred (L. 553-1)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «action_prescrite» (p: Personne p)? | truth | `action_prescrite(p: Personne)` | `evaluate truth(action_prescrite(<p>));` | — | tests 4 |

## CSS_L553_2

Source units: CSS_L553_2.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `indemnite-frais-gestion` | Is it established that “management-cost indemnity: 10% of the amounts claimed (L. 553-2 para. 1)” (p: natural person claiming or receiving family benefits p, montant: monetary amount montant)?<br>*authored wording:* Is it established that «indemnite_frais_gestion» (p: Personne p, montant: Money montant)? | truth | `indemnite_frais_gestion(p: Personne, montant: Money)` | `evaluate truth(indemnite_frais_gestion(<p>, <montant>));` | — | tests 1 |

## CSS_L553_2_1

Source units: CSS_L553_2_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `contrainte-possible` | Is it established that “mise en demeure without effect: the director may issue a contrainte (L. 553-2-1 para. 4)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «contrainte_possible» (p: Personne p)? | truth | `contrainte_possible(p: Personne)` | `evaluate truth(contrainte_possible(<p>));` | — | tests 1 |
| `majoration-mise-en-demeure` | Is it established that “10% increase on unpaid amounts (L. 553-2-1 para. 4)” (p: natural person claiming or receiving family benefits p, montant: monetary amount montant)?<br>*authored wording:* Is it established that «majoration_mise_en_demeure» (p: Personne p, montant: Money montant)? | truth | `majoration_mise_en_demeure(p: Personne, montant: Money)` | `evaluate truth(majoration_mise_en_demeure(<p>, <montant>));` | — | tests 1 |

## CSS_L553_3

Source units: CSS_L553_3.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `majorations-reduites` | Is it established that “increases reduced by the amount of family benefits (L. 553-3 para. 2)” (p: natural person claiming or receiving family benefits p, montant: monetary amount montant)?<br>*authored wording:* Is it established that «majorations_reduites» (p: Personne p, montant: Money montant)? | truth | `majorations_reduites(p: Personne, montant: Money)` | `evaluate truth(majorations_reduites(<p>, <montant>));` | — | tests 1 |

## CSS_L553_4

Source units: CSS_L553_4.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-insaisissabiliteprestations` | Which normative positions arose in the case (norms: “Family benefits are unassignable and unseizable”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «InsaisissabilitePrestations») and what is their status? | positions | norms `InsaisissabilitePrestations` | `evaluate positions(); — expected form position(InsaisissabilitePrestations, <status>)` | — | tests 1 |
| `poziciya-saisiecaslegal` | Which normative positions arose in the case (norms: “1/2 of I: attachment possible for maintenance debts and care, accommodation, education costs”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «SaisieCasLegal») and what is their status? | positions | norms `SaisieCasLegal` | `evaluate positions(); — expected form position(SaisieCasLegal, <status>)` | — | tests 1 |
| `poziciya-saisieindufrauduleux` | Which normative positions arose in the case (norms: “Except recovery of overpayments following a fraudulent scheme or false declaration: attachment possible”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «SaisieInduFrauduleux») and what is their status? | positions | norms `SaisieInduFrauduleux` | `evaluate positions(); — expected form position(SaisieInduFrauduleux, <status>)` | — | tests 1 |

## CSS_L553_5

Source units: CSS_L553_5.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `evaluation-forfaitaire-possible` | Is it established that “lump-sum assessment of lifestyle items may be counted (L. 553-5 para. 1)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «evaluation_forfaitaire_possible» (p: Personne p)? | truth | `evaluation_forfaitaire_possible(p: Personne)` | `evaluate truth(evaluation_forfaitaire_possible(<p>));` | — | tests 1 |

## CSS_L554_2

Source units: CSS_L554_2.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `amende-encourue` | Is it established that “fine of 4,500 euros incurred (L. 554-2)” (i: natural person claiming or receiving family benefits i, montant: monetary amount montant)?<br>*authored wording:* Is it established that «amende_encourue» (i: Personne i, montant: Money montant)? | truth | `amende_encourue(i: Personne, montant: Money)` | `evaluate truth(amende_encourue(<i>, <montant>));` | — | tests 1 |

## CSS_L554_3

Source units: CSS_L554_3.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `cout-insertion-plafond` | Is it established that “insertion cost not above 150 euros (L. 554-3)” (p: natural person claiming or receiving family benefits p, montant: monetary amount montant)?<br>*authored wording:* Is it established that «cout_insertion_plafond» (p: Personne p, montant: Money montant)? | truth | `cout_insertion_plafond(p: Personne, montant: Money)` | `evaluate truth(cout_insertion_plafond(<p>, <montant>));` | — | tests 1 |
| `poziciya-ordonnerinsertionjugement` | Which normative positions arose in the case (norms: “On conviction the court may order insertion of the judgment in newspapers at the convicted person's expense”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «OrdonnerInsertionJugement») and what is their status? | positions | norms `OrdonnerInsertionJugement` | `evaluate positions(); — expected form position(OrdonnerInsertionJugement, <status>)` | — | tests 1 |

## CSS_L581_1

Source units: CSS_L581_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-aiderrecouvrementcreances` | Which normative positions arose in the case (norms: “Bodies may help recover maintenance claims”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «AiderRecouvrementCreances») and what is their status? | positions | norms `AiderRecouvrementCreances` | `evaluate positions(); — expected form position(AiderRecouvrementCreances, <status>)` | — | tests 1 |

## CSS_L581_10

Source units: CSS_L581_10.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-poursuivrerecouvrementdirect` | Which normative positions arose in the case (norms: “After prefet referral and until notified termination: no direct recovery action”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «PoursuivreRecouvrementDirect») and what is their status? | positions | norms `PoursuivreRecouvrementDirect` | `evaluate positions(); — expected form position(PoursuivreRecouvrementDirect, <status>)` | — | tests 1 |

## CSS_L581_2

Source units: CSS_L581_2.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `allocation-acquise-creancier` | Is it established that “differential allowance not recovered, kept by the creditor (L. 581-2 para. 4)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «allocation_acquise_creancier» (p: Personne p)? | truth | `allocation_acquise_creancier(p: Personne)` | `evaluate truth(allocation_acquise_creancier(<p>));` | — | tests 1 |
| `subrogation-organisme` | Is it established that “body subrogated to the creditor's rights (L. 581-2 para. 3)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «subrogation_organisme» (p: Personne p)? | truth | `subrogation_organisme(p: Personne)` | `evaluate truth(subrogation_organisme(<p>));` | — | tests 1 |

## CSS_L581_3

Source units: CSS_L581_3.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `priorite-organisme-sommes` | Is it established that “body entitled by priority over recovered amounts up to the advances (L. 581-3 para. 2)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «priorite_organisme_sommes» (p: Personne p)? | truth | `priorite_organisme_sommes(p: Personne)` | `evaluate truth(priorite_organisme_sommes(<p>));` | — | tests 1 |

## CSS_L581_4

Source units: CSS_L581_4.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `renoncement-effectif` | Is it established that “declinature effective, subrogation kept until full recovery (L. 581-4 para. 2)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «renoncement_effectif» (p: Personne p)? | truth | `renoncement_effectif(p: Personne)` | `evaluate truth(renoncement_effectif(<p>));` | — | tests 1 |
| `suspension-asf-possible` | Is it established that “body may suspend ASF payment (L. 581-4 para. 3)” (o: body owing family benefits (fund) o, p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «suspension_asf_possible» (o: Organisme o, p: Personne p)? | truth | `suspension_asf_possible(o: Organisme, p: Personne)` | `evaluate truth(suspension_asf_possible(<o>, <p>));` | — | tests 1 |

## CSS_L581_6

Source units: CSS_L581_6.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `aide-recouvrement-accordee` | Is it established that “bodies' help recovering due and future instalments (L. 581-6)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «aide_recouvrement_accordee» (p: Personne p)? | truth | `aide_recouvrement_accordee(p: Personne)` | `evaluate truth(aide_recouvrement_accordee(<p>));` | — | tests 1 |

## CSS_L581_9

Source units: CSS_L581_9.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `subrogation-plein-droit` | Is it established that “subrogation as of right up to the advances - against debtor and Treasury (L. 581-9)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «subrogation_plein_droit» (p: Personne p)? | truth | `subrogation_plein_droit(p: Personne)` | `evaluate truth(subrogation_plein_droit(<p>));` | — | tests 1 |

## CSS_L582_1

Source units: CSS_L582_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `penalite-prononcable` | Is it established that “director penalty available (amount <= BMAF by decree - out of scope)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «penalite_prononcable» (p: Personne p)? | truth | `penalite_prononcable(p: Personne)` | `evaluate truth(penalite_prononcable(<p>));` | — | tests 1 |

## CSS_L582_2

Source units: CSS_L582_2.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `titre-executoire-delivre` | Is it established that “agreement given enforceable force: enforceable title (L. 582-2 para. 2)” (p: natural person claiming or receiving family benefits p)?<br>*authored wording:* Is it established that «titre_executoire_delivre» (p: Personne p)? | truth | `titre_executoire_delivre(p: Personne)` | `evaluate truth(titre_executoire_delivre(<p>));` | — | tests 1 |

## CSS_L583_1

Source units: CSS_L583_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-informerallocataires` | Which normative positions arose in the case (norms: “Bodies must inform allocataires of the nature and extent of their rights”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «InformerAllocataires») and what is their status? | positions | norms `InformerAllocataires` | `evaluate positions(); — expected form position(InformerAllocataires, <status>)` | — | tests 1 |
| `poziciya-preterconcoursdemandes` | Which normative positions arose in the case (norms: “Bodies must assist in drawing up claims”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «PreterConcoursDemandes») and what is their status? | positions | norms `PreterConcoursDemandes` | `evaluate positions(); — expected form position(PreterConcoursDemandes, <status>)` | — | tests 1 |

## CSS_L583_2

Source units: CSS_L583_2.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-accorderavancefondssociaux` | Which normative positions arose in the case (norms: “Any unambiguously assessable benefit may be advanced from social funds within established rights”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «AccorderAvanceFondsSociaux») and what is their status? | positions | norms `AccorderAvanceFondsSociaux` | `evaluate positions(); — expected form position(AccorderAvanceFondsSociaux, <status>)` | — | tests 1 |

## CSS_L583_3

Source units: CSS_L583_3.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-suspendreversementcontrole` | Which normative positions arose in the case (norms: “Payment may be suspended where the allocataire refuses checks”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «SuspendreVersementControle») and what is their status? | positions | norms `SuspendreVersementControle` | `evaluate positions(); — expected form position(SuspendreVersementControle, <status>)` | — | tests 1 |

## CSS_L583_4

Source units: CSS_L583_4.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-transmettreindemnitesjournalieres` | Which normative positions arose in the case (norms: “Sickness schemes transmit L. 431-1 2 daily allowances to the fisc (law 78-17)”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «TransmettreIndemnitesJournalieres») and what is their status? | positions | norms `TransmettreIndemnitesJournalieres` | `evaluate positions(); — expected form position(TransmettreIndemnitesJournalieres, <status>)` | — | tests 1 |

## CSS_L583_5

Source units: CSS_L583_5.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `poziciya-transmettrecontributionfisc` | Which normative positions arose in the case (norms: “Bodies transmit the enforceable L. 582-2 contribution to the fisc”), and what is their status?<br>*authored wording:* Which normative positions arose in the case (norms: «TransmettreContributionFisc») and what is their status? | positions | norms `TransmettreContributionFisc` | `evaluate positions(); — expected form position(TransmettreContributionFisc, <status>)` | — | tests 1 |

## CSS_R512_1

Source units: CSS_R512_1.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `residence-maintenue` | Is it established that “child is deemed resident in France (R. 512-1)” (e: child in respect of whom family benefits are claimed e)?<br>*authored wording:* Is it established that «residence_maintenue» (e: Enfant e)? | truth | `residence_maintenue(e: Enfant)` | `evaluate truth(residence_maintenue(<e>));` | — | tests 2 |

## CSS_R532_3

Source units: CSS_R532_3.

| id | question | form | target | template | branches | checked by |
|---|---|---|---|---|---|---|
| `ressources-totales` | Is it established that “total resources counted for the person” (p: natural person claiming or receiving family benefits p, montant: monetary amount montant)?<br>*authored wording:* Is it established that «ressources_totales» (p: Personne p, montant: Money montant)? | truth | `ressources_totales(p: Personne, montant: Money)` | `evaluate truth(ressources_totales(<p>, <montant>));` | — | tests 3 |

## Derivable without a card of its own

Links of the derivation: they are asked through the cards above and are named here so that the surface is closed in both directions.

| predicate | why there is no card |
|---|---|
| `fraude_reiteree` | Conclusion without executable witness: the rule premises contain forms the generated scenario does not build (disjunction, text value or term call), or the head is computed. The card will appear together with a hand-written scenario. |
| `indu_recupere_retenues` | Conclusion without executable witness: the rule premises contain forms the generated scenario does not build (disjunction, text value or term call), or the head is computed. The card will appear together with a hand-written scenario. |
| `indu_rembourse_unique` | Conclusion without executable witness: the rule premises contain forms the generated scenario does not build (disjunction, text value or term call), or the head is computed. The card will appear together with a hand-written scenario. |
| `intermediation_mise_en_oeuvre` | Conclusion without executable witness: the rule premises contain forms the generated scenario does not build (disjunction, text value or term call), or the head is computed. The card will appear together with a hand-written scenario. |
| `allocataire` | Intermediate link: the predicate is derived by a package rule and read by the bodies of other rules (AvanceFondsSociaux, DevoirPayerPrestations, Insaisissabilite…); it is not a standalone question to the package. |
| `annee_reference` | Intermediate link: the predicate is derived by a package rule and read by the bodies of other rules (RessourcesPropres); it is not a standalone question to the package. |
| `delegue_percoit` | Intermediate link: the predicate is derived by a package rule and read by the bodies of other rules (FraisMesureOrganisme); it is not a standalone question to the package. |
| `enfant_ouvre_droit` | Intermediate link: the predicate is derived by a package rule and read by the bodies of other rules (AllocataireChargeEffective); it is not a standalone question to the package. |
| `plafond_remuneration` | Intermediate link: the predicate is derived by a package rule and read by the bodies of other rules (EnfantVingtAns); it is not a standalone question to the package. |

## Summary

Cards 54, boundaries 4, internal links 9; derivable predicates in the CLIR 45, norms 18 — the surface is closed in both directions. The reasons for a particular case come not from the catalogue but from the issues and the why_not of the answer.
