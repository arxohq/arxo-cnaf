# Construction et promotion autonomes du MCP CNAF

La seule source de données est ce dépôt arxo-cnaf. Aucun checkout law-dsl,
index global, compilation Rust, installation npm/pip/apt ou import Python
externe n'intervient dans la construction autonome.

## Aperçu publié

La [release acceptée du 13 octobre 2026](https://github.com/arxohq/arxo-cnaf/releases/tag/preview-ec69e273384934eaea10f4117d7954ffa90e4848)
fixe le commit `ec69e273384934eaea10f4117d7954ffa90e4848`.
Son `release.json` donne l'image à déployer :

```text
ghcr.io/arxohq/arxo-cnaf-mcp@sha256:e26418ad7caf7dd961e4b7fcab8d95382179683f8c1369c7c72b250bede075e4
```

Le config digest accepté est
`sha256:7ecb4904555d645d32e5b6fdd2cfdc9301a90af42bb6c8c3bfe71a398dba808e` ;
il est distinct du digest de manifest du registre. Le reçu externe
`candidate.json` a pour SHA-256
`cb4e0dfb396850adfdd56f1fb0ac35c728b49c2e46c4aaf2685a7c2f47bb45f2`.
L'archive OCI, le runtime, leurs pins et les reçus sont attachés à cette release.

## Entrées et acquisition

Choisir un commit Git exact, puis vérifier `mcp/input-inventory.json`, le canon,
les politiques, le tree pin accepté `mcp/tree.pin.json` et le host accepté dans `mcp/runtime.lock.json`. Le host est une
publication binaire exacte dont l'archive et le binaire extrait sont vérifiés
par SHA-256. Les assets nécessaires sont locaux et également épinglés.

`mcp/build.lock.json` fixe les manifests Linux amd64 du builder Python 3.13.7 et
de la base Debian par digest. Le builder utilise exclusivement la bibliothèque
standard : il n'y a aucune installation de dépendance cachée après acquisition.
Sur une machine avec Docker et Python 3, dans le checkout exact :

```sh
python3 tools/acquire_mcp.py --root . --output /tmp/cnaf-acquired
python3 tools/build_mcp.py --root . --acquired /tmp/cnaf-acquired \
  --output /tmp/cnaf-candidate --source-commit '<SHA-Git-exact>' \
  --image 'arxo-cnaf-mcp:preview-<SHA-Git-exact>'
```

Le second répertoire doit être neuf. La première commande est la seule étape
réseau : elle acquiert les bytes binaires et les deux images épinglées. La
seconde réutilise ces entrées. Deux matérialisations indépendantes, les
vérificateurs et les archives normalisées doivent produire la même identité.
Le materializer conserve les bytes CLIR, locks et ressources, sans recompiler
les modèles ni modifier leurs versions.

La porte finale exige un runtime contract accepté, une preuve Linux compatible
liée au SHA du binaire et au commit du host, et un tree pin généré identique au
pin accepté dans le dépôt. Aucun reçu natif seul ni statut `not_checked` de
Linux ne permet de créer un candidat accepté.

Pour amorcer la preuve d'un nouveau host, invoquer `tools/offline_mcp.py
--diagnostic` dans le builder épinglé, avec les mêmes mounts et `--network none`.
Cette voie produit un arbre et un smoke diagnostiques, sans candidat OCI ni
release. Après réception de la preuve Linux et fixation du tree pin,
`tools/build_mcp.py --reuse-offline` revérifie l'arbre, l'archive et les entrées
du smoke avant de passer toutes les portes finales, sans répéter le smoke
offline déjà réussi.

Les tests ciblés, le smoke réel stdio/HTTP et la création des archives tournent
dans le builder avec `--network none`, sans mount law-dsl. Le build Docker
consomme uniquement le runtime accepté, l'entrypoint et NOTICE. Son réseau de
build est également désactivé. Le conteneur final, en lecture seule et sans
réseau sortant, est ensuite soumis au même handshake, aux contrôles
authentification/Origin et aux cas CNAF. Seules des réponses et preuves réelles
peuvent satisfaire les attentes écrites avant l'exécution.

## Artifacts acceptés

Le répertoire de sortie contient :

- `runtime.tar.gz` et son SHA-256 externe ;
- `tree.pin.json`, inventaire canonique externe au runtime ;
- `materialization.json`, les reçus offline/image smoke et la politique Docker ;
- `image.tar`, l'image exacte acceptée avec son ID Docker ;
- `candidate.json` qui lie les SHA-256 de ces artifacts et son checksum externe.

Ne placez ni le tree pin ni les reçus à l'intérieur de l'arbre hashé. Ne
réécrivez aucun artifact publié. Les archives normalisées sont déterministes ;
le digest OCI est l'identité de l'image réellement acceptée et promue, sans
promesse de rebuild Docker bit-à-bit. `fullCorpus: not_checked` et
`releaseVerified: false` restent inchangés.

## CI et promotion

La CI des modèles (`ci.yml`) est filtrée sur les modèles, le registry et leurs
entrées de toolchain ; son lancement manuel reste disponible. Une modification
MCP ou de documentation ne relance pas les 21 reconstructions ni la récupération
de sources retenues. Ce fichier généré peut être réémis par un futur export de
paquets : conserver alors ses filtres. Le recipe d'export ne possède pas la
livraison autonome, qui reste définie par les workflows MCP de ce dépôt.

`mcp-verify.yml` ne checkout que arxo-cnaf et n'a pas de credential de
publication. Il sépare acquisition en ligne et vérification offline. Son
artifact GitHub Actions est immuable et expire après 30 jours. La promotion
publie ensuite l'archive runtime, l'archive d'image OCI `image.tar`, leurs pins et reçus dans une release GitHub
durable, sans écraser un tag ou une release existants.

`mcp-release.yml` est déclenché explicitement avec le run de vérification, le
commit exact et le SHA-256 externe de `candidate.json`. Seul un run réussi
`push` de `main`, dans ce dépôt et ce workflow, est admissible. Une archive PR
ne peut pas être promue. Le job de promotion est le seul à recevoir
`packages: write` et `contents: write` (publication durable des artifacts de
release GitHub) ; aucun build n'y est exécuté.

La promotion vérifie tous les SHA-256 et les reçus, charge `image.tar`, vérifie
l'ID accepté et publie sous `ghcr.io/arxohq/arxo-cnaf-mcp:preview-<SHA-complet>`.
Un tag existant n'est pas écrasé. Le config digest du manifest de registre
(obtenu par son digest immutable) doit égaler l'ID de l'image réellement
testée ; un manifest multi-platforme ou un autre config est refusé. Lors de
la première publication GHCR, le package est initialement privé : le rendre
public dans les paramètres du package, puis vérifier un pull par digest sans
credential avant le staging. L'héritage des permissions du dépôt ne rend pas
automatiquement le package public. Ne distribuer aucun credential de registre
dans le runtime. `release.json` fournit le digest de registre à
utiliser pour le staging et le déploiement. La commande équivalente est :

```sh
python3 tools/promote_mcp.py --directory /tmp/cnaf-candidate \
  --receipt-sha256 '<SHA-256-accepté-de-candidate.json>' \
  --source-commit '<SHA-Git-exact>' \
  --image 'ghcr.io/arxohq/arxo-cnaf-mcp:preview-<SHA-Git-exact>'
```

## Staging, activation et retour arrière

Tirer le digest de registre accepté sur le serveur, sans checkout law-dsl.
Si l'accès au registre est indisponible, télécharger `image.tar` et
`candidate.json` de la release publique exacte, vérifier le SHA-256
`candidate.json.files["image.tar"]`, puis charger l'archive avec `docker load`.
L'ID obtenu doit être exactement `candidate.json.imageId` ; aucun rebuild
n'intervient. Garder aussi le checksum externe de `candidate.json` fixé lors
de l'acceptation, car un checksum et des bytes pris ensemble sans pin
indépendant n'établissent pas l'origine. Garder le digest et la configuration courante
avant activation. Configurer un conteneur CNAF distinct et le proxy TLS,
appliquer Compose, puis exécuter `tools/mcp_smoke.py --transport http --url
https://<hôte>/mcp --cases mcp/cases/acceptance.json --source-policy mcp/source-policy.json --receipt <nouveau-reçu>`
avec le jeton et l'Origin autorisés dans l'environnement. `--health-url` permet
un chemin de santé externe distinct et `--expected-host-sha256` fixe l'identité
du binaire attendue dans les preuves. Un proxy expressément public peut être
vérifié avec `--auth-mode public` : ce choix ne modifie pas l'authentification
du conteneur, et le reçu distingue accès public et refus Bearer. Les latences
de chaque appel HTTP sont mesurées dans `measurements`. Conserver les mesures
effectives de démarrage, mémoire, latence, délai et redémarrage avec le reçu.

Pour revenir à une release précédente, rétablir son digest et sa configuration
puis relancer Compose et le smoke, sans rebuild. Lors de la première
activation, le retour consiste à retirer la nouvelle route et arrêter le
conteneur CNAF ; les autres services Arxo conservent leur configuration.
Tester aussi le lancement sur un second site propre avec ces seuls artifacts.
Une preuve de staging ou d'activation doit nommer le digest réellement servi.
