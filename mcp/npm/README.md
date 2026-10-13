# @arxo/mcp-cnaf

Les modèles CNAF d'Arxo comme serveur MCP local sur **stdio**. Le paquet
contient le même jeu de données épinglé que le conteneur autonome ; le moteur
vient d'un paquet de host commun, à version exacte. Node.js **20+**, Linux x64
et macOS arm64.

```sh
npx -y @arxo/mcp-cnaf@0.1.0
```

Le serveur attend les messages JSON-RPC du client MCP sur stdin et répond sur
stdout. Une attente sans affichage est normale. Configuration d'un client :

```json
{
  "mcpServers": {
    "arxo-cnaf": {
      "command": "npx",
      "args": ["-y", "@arxo/mcp-cnaf@0.1.0"]
    }
  }
}
```

Pour afficher la version : `npx -y @arxo/mcp-cnaf@0.1.0 --version`.
Les autres arguments ne sont pas transmis au moteur : le profil reste CNAF.
Ne pas omettre les dépendances optionnelles, qui fournissent le binaire natif.
Sur une autre plateforme, utilisez le [MCP hébergé](https://mcp.arxo.io/mcp/cnaf).

Les requêtes s'exécutent localement. L'installation npm télécharge les
paquets ; aucun téléchargement de corpus ni service auxiliaire n'est nécessaire
pendant l'exécution. Le launcher n'hérite pas des variables LAW_ du terminal.
Son état temporaire privé est supprimé à la sortie normale et après un signal.
Cette commande native n'impose pas le sandbox réseau/ressources du conteneur.
`CNAF_MCP_CALL_TIMEOUT` règle le temps de réponse (entier 1–110 secondes,
30 par défaut) ; un calcul synchrone déjà commencé peut finir après le timeout.

Avant de démarrer, le launcher vérifie les bytes de chaque fichier de données,
la version du host et son SHA-256. `pin.json` conserve séparément l'identité du
runtime OCI d'origine, l'inventaire des données sans binaire et les pins de
chaque plateforme. Les modèles, locks et ressources ne sont pas recompilés.

Le [guide MCP](https://github.com/arxohq/arxo-cnaf/blob/main/docs/mcp.md) donne
un exemple AJPP complet, les outils disponibles et le contexte temporel
explicite requis. Les 21 modèles sont indépendants de la CNAF ; les réponses
ne constituent pas une décision de l'administration. Les droits des textes
restent ceux des éditeurs : voir `NOTICE`. Les quatre fichiers withheld ne
sont pas réintroduits. Le corpus complet n'a pas été accepté par ce canal :
`fullCorpus: not_checked`, `releaseVerified: false`.
