# Arxo CNAF MCP — aperçu technique

Ce serveur expose un **modèle indépendant Arxo** de 21 modèles français du
corpus CNAF. Il ne s'agit pas d'un service officiel de la CNAF ou de la CAF.
`fullCorpus: not_checked` et `releaseVerified: false` décrivent la portée réelle :
les vérifications portent sur le paquet, le transport et les cas publiés dans
`mcp/cases/acceptance.json`, sans nouvelle réception de tout le corpus.

Le catalogue (`law_packages`), la recherche lexicale locale (`law_search`), les
sources (`law_sources`), les règles et contrats d'entrée (`law_rules`) et
l'exécution (`law_ask`) sont disponibles. Les facettes rédaction, adversarial,
édition et les autres facettes non acceptées sont refusées même par appel
direct. Le calendrier français n'est pas accepté : `calendarPackage: null` et
`law_ask(kind="deadline")` refuse la demande. Certains outils de publication
appartiennent à la facette exécution et peuvent être annoncés par le host ;
l'absence d'un service de publication leur impose un refus documenté.

LawQL (`law_query`) accepte les requêtes structurelles inline sur le catalogue
local sélectionné. `law_ask.package` utilise la clé runtime
(`fr-pf-ajpp`), tandis que `law_query.corpus` utilise le nom de publication
(`fr.pf.ajpp`) ou un glob sur ces noms. L'inférence LawQL, les matérialisations, les sources de
fichiers et les questions nommées sont refusées par
`STRICT_CONTEXT_QUERY_UNSUPPORTED` : utiliser `law_ask` avec contexte explicite
pour une question juridique. Le registre global de passeports et les affaires
authored ne sont pas distribués ; `law_passport` et `law_case_ask` annoncent
leur indisponibilité même avec un identifiant de publication complet ou un
chemin de paquet légal présent.

Une réponse `NEITHER` signifie que les prémisses n'établissent pas le résultat.
Elle ne constitue pas une décision de refus d'une prestation. Les montants
retenus fournis par l'utilisateur restent des faits d'entrée ; leur présence ne
prouve pas qu'ils sont applicables à une affaire réelle.

## Connexion HTTP

L'adresse du transport est `https://<votre-hôte>/mcp`, derrière un proxy TLS.
Le client envoie `Authorization: Bearer <jeton>` et négocie le protocole MCP par
`initialize`. Pour un client Web, son `Origin` doit figurer exactement dans
`CNAF_MCP_ALLOWED_ORIGINS` (valeurs séparées par des virgules). Les autres
origines sont refusées. `/healthz` indique la disponibilité du processus ; ce
contrôle n'est pas une validation du corpus.

Chaque question d'exécution doit préciser la date du droit et le contexte :

```json
{
  "kind": "truth",
  "package": "fr-pf-ajpp",
  "predicate": "ajpp_droit_ouvert",
  "args": ["urn:case:enfant"],
  "legalTime": "2024-03-15",
  "context": {
    "timezone": "Europe/Paris",
    "decisionTime": "2024-03-15T12:00:00Z",
    "knowledgeTime": "2024-03-15T12:00:00Z"
  },
  "facts": [],
  "proof": true
}
```

Les instants sont explicites et leur décalage UTC est conservé. Les faits portent
une `provenance` avec leur origine (`case_input`, `adjudicated`, etc.). Les
interprétations sont choisies explicitement dans `selectedInterpretations` par
leur StableId. Vérifiez les signatures et les sources de la publication choisie
avant de poser la question. La provenance et la preuve donnent la date, les
empreintes et les règles effectivement utilisées.

## Lancer le conteneur accepté

Utilisez l'image **par digest** publié dans `release.json` ; aucun `latest` n'est
prévu. Conservez le jeton dans l'environnement de déploiement, hors du dépôt :

```sh
export CNAF_MCP_IMAGE='ghcr.io/arxohq/arxo-cnaf-mcp@sha256:<digest-accepté>'
export CNAF_MCP_TOKEN='<jeton>'
export CNAF_MCP_ALLOWED_ORIGINS='https://<origine-du-client>'
docker compose up -d
```

Le port local par défaut est `127.0.0.1:8723`, pour le proxy TLS du serveur.
L'image fonctionne avec UID/GID 65532, système de fichiers en lecture seule,
aucune capability et `no-new-privileges`. Le dataset et le host sont immuables.
Les instantanés d'exécution vont dans `/state/artifacts`, un tmpfs borné à 64 MiB
et perdu au redémarrage. La taille de la réponse et les limites de calcul
restent celles du host épinglé ; les appels sont limités à 30 secondes, le
processus à 512 MiB et 128 PID. Aucun SLA n'est déduit de ces limites.

Le réseau Compose est `internal: true` : le processus ne reçoit pas d'accès
sortant. Les tests offline utilisent effectivement `--network none`. Un flag
ou un reçu ne remplace pas cette isolation d'infrastructure. L'entrypoint
transmet seulement le jeton, les origines, le délai et ses paramètres fixes ;
les variables héritées de services de réponses, neural ou OTLP sont éliminées.

## Sources et identité

Les quatre fichiers PDF/TXT retenus hors distribution publique ne sont pas
récupérés. Les cinq extraits déjà présents dans les publications verrouillées
restent identiques, selon `mcp/source-policy.json`. Les textes de sources ne
sont pas redigés ni rendus officiels par Arxo ; leurs statuts sont ceux de leurs
passeports et les limites du public scope s'appliquent aussi aux réponses API.

`mcp/input-inventory.json` fixe le commit des publications. Le commit de
l'implémentation, le host téléchargé, le digest du runtime et l'image sont liés
par `candidate.json` puis `release.json`. Conservez les reçus externes et leurs
SHA-256 avec les artifacts. Voir [la procédure autonome](mcp-release.md).

Le même arbre runtime peut servir au transport stdio avec le host épinglé :
`runtime/bin/law-mcp-server --root runtime --profile cnaf`. Les tests de paquet
couvrent ce transport ; la publication d'un client npm reste un canal distinct.
