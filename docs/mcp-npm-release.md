# Livraison npm du MCP CNAF

`@arxo/mcp-cnaf@0.1.0` est la livraison stdio du même runtime CNAF accepté
pour l'OCI preview. Les données proviennent uniquement de l'archive runtime
de la [release épinglée](https://github.com/arxohq/arxo-cnaf/releases/tag/preview-ec69e273384934eaea10f4117d7954ffa90e4848),
SHA-256 `e258242678f7a9c1b5bf8f8eadd16a4ad44b9ce580f92c515f259a5c681bd890`.
Le tree pin original `mcp/tree.pin.json` reste
`sha256:1c924738a10bf4a4c5db52809a078ac56c5a1c3e8d5e4c44723124cf178d0939`.

L'archive npm contient tous ses fichiers de données, byte pour byte, en
retirant seulement le binaire et son répertoire vide. Cette projection a son
propre inventaire et digest, distincts du tree pin OCI. Le binaire vient des
paquets communs `@arxo/mcp-host-linux-x64` et
`@arxo/mcp-host-darwin-arm64`, version exacte `0.4.2-cnafpreview.1`.
Linux réutilise le binaire accepté ; Darwin est construit avec Rust1.94.1,
Cargo locked et le même source commit
`0a07391da494237f3c2d911a6df867cb871277fc`, puis vérifié sur les cas CNAF.
Les versions et SHA de chaque plateforme sont dans `mcp/npm/host-pins.json`.
Ce fichier ne remplace ni les pins OCI, ni les pins des autres canons.

## Préparer

Python **3.12+**, npm et les binaires épinglés sont nécessaires au packaging.
Depuis le checkout immuable de ce dépôt, avec les artifacts déjà acquis :

```sh
python3 tools/mcp_npm.py pack \
  --runtime-archive /path/runtime.tar.gz \
  --binary linux-x64=/path/linux/law-mcp-server \
  --binary darwin-arm64=/path/darwin/law-mcp-server \
  --source-commit '<SHA-exact-de-ce-checkout>' --out /path/new-candidate
python3 tools/mcp_npm.py smoke /path/new-candidate --npx \
  --receipt /path/installed-smoke.json
```

Le packaging refuse tout archive/runtime/binaire qui ne correspond pas aux
pins. Il ne compile pas les modèles, ne relock pas le corpus et ne restaure
aucune source withheld. `npm-release.json` nomme les trois archives, leurs
SHA, l'ordre de publication et les fichiers de la réception par leurs SHA.
Les tarballs/generated data restent hors Git. Les tests du launcher contrôlent
les fichiers extra/modifiés/manquants, les symlinks, l'environnement et les
arguments. Le consumer smoke compare tous les fichiers npm installés aux
tarballs gelés avant d'exécuter les vrais cas/proofs sur stdio.

## Publier et vérifier

Le canal CI existant de livraison MCP reçoit un candidat gelé ; aucune
publication locale n'est effectuée. Les deux hosts sont rendus disponibles
avant la publication de la wrapper. Leur tag est `cnaf-preview` : les tags
stables et les versions des autres profils restent inchangés. La wrapper est
publiée sous `latest`. Un retry ne remplace jamais une version : des bytes
déjà publiés doivent avoir exactement la même identité.

Le consommateur anonyme est réinstallé depuis npm après publication, avec
Node20 et un répertoire/cache neufs. Les mêmes protocol/cas/guards s'exécutent
par `npx`. Les SHA des archives publiées et les résultats de macOS/Linux
sont conservés dans les receipts de la livraison. Les workflows des modèles
et les livraisons OCI sont indépendants de la wrapper npm.

`fullCorpus: not_checked` et `releaseVerified: false` restent explicites.
Une réception de transport et de scénarios ciblés ne vaut pas une réception
normative du corpus entier.
