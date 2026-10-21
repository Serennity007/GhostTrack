# GhostTrack Console

[简体中文](README.zh-CN.md) · [English](README.md) · [日本語](README.ja.md) · [Español](README.es.md) · **Français**

**Un espace de travail OSINT multiplateforme pour explorer les informations publiques sur Windows et Android.**

Réunissez les enregistrements de domaines, le DNS, les certificats TLS, les registres IP / ASN et les profils publics dans une seule console. GhostTrack relie douze outils Windows et onze modules Android à un moteur de requête commun, avec des résultats que vous pouvez filtrer, copier et exporter.

- **Un rapport de domaine en une seule recherche.** Interrogez en parallèle le RDAP, huit types d'enregistrements DNS et les informations HTTPS / TLS, avec un état distinct pour chaque source.
- **Des résultats avec leur contexte.** Consultez les URL sources disponibles et le contexte de la requête en UTC, filtrez les champs, copiez les valeurs et exportez des rapports JSON, CSV ou HTML autonomes.
- **Du bureau au mobile.** Utilisez l'espace de travail Windows à deux colonnes ou l'interface native Android, avec quatre langues d'interface et des paquets prêts à l'emploi sans installation séparée de Python.

> La documentation existe en chinois, anglais, japonais, espagnol et français. L'interface de l'application propose quatre langues : chinois simplifié, anglais, japonais et espagnol. Le français concerne ici la documentation.

## Télécharger et installer

| Plateforme | Téléchargement actuel | Installation |
|---|---|---|
| Windows 10/11 x64 · v1.8.0 | [ZIP portable](https://github.com/Serennity007/GhostTrack/releases/download/windows-v1.8.0/GhostTrack-v1.8.0-Windows-x64.zip) · [Version et SHA256](https://github.com/Serennity007/GhostTrack/releases/tag/windows-v1.8.0) | Extraire toute l'archive puis lancer `GhostTrack/GhostTrack.exe` |
| Android 7.0 ou ultérieur · v1.6.0 | [APK universel](https://github.com/Serennity007/GhostTrack/releases/download/android-v1.6.0/GhostTrack-v1.6.0-Android-universal.apk) · [Version et SHA256](https://github.com/Serennity007/GhostTrack/releases/tag/android-v1.6.0) | Ouvrir l'APK dans le gestionnaire de fichiers du téléphone |

Windows ne nécessite pas d'installation de Python. Conservez l'exécutable avec toutes ses dépendances. L'APK contient ARM64, ARMv7 et x86_64 ; le premier démarrage extrait l'environnement intégré. N'autorisez l'installation que pour l'application utilisée pour ouvrir l'APK. Pour les mises à jour, utilisez les APK de ce dépôt signés avec le même certificat.

[Guide Windows en anglais](docs/windows.md) · [Guide Android et compilation en anglais](docs/android.md) · [Historique des versions en anglais](CHANGELOG.md)

## Interface

![Console d'informations publiques pour Windows](docs/desktop.png)

<img src="docs/android.png" width="320" alt="Console d'informations publiques pour Android" />

Windows v1.8.0 adopte un espace de travail à deux colonnes :

- Saisie, exemples et contexte des sources à gauche ; tableau des résultats et détail de la valeur complète à droite.
- La navigation numérotée et compacte regroupe les douze outils. Les cartes affichent le nombre réel de champs, la durée et l'état de la requête.
- La barre d'actions s'adapte à la largeur de la fenêtre, avec filtrage, copie et export à côté des résultats.

Les éléments graphiques décoratifs n'indiquent pas qu'une cible est analysée par un scanner. Les résultats et états reflètent les données reçues. La dernière version Android reste la v1.6.0.

## Douze outils de recherche

| Outil | Entrée | Informations publiques disponibles |
|---|---|---|
| Archive autorisée | Numéro de téléphone ou mot-clé | Associations téléphone-profil autorisées, enregistrées localement avec source et date |
| Rapport de domaine | Domaine | RDAP, DNS et HTTPS en parallèle, avec un état par source |
| Enregistrement de domaine | Domaine | Bureau d'enregistrement, dates de création/expiration/mise à jour, DNSSEC, serveurs de noms |
| Enregistrements DNS | Domaine | A, AAAA, CNAME, MX, NS, TXT, SOA, CAA et TTL |
| Site web et certificat | URL HTTPS publique | État HTTP, titre, redirections, en-têtes publics, émetteur/validité/SAN TLS |
| Enregistrement IP / ASN | IP publique ou `AS15169` | Plages enregistrées, CIDR, noms de réseau, codes pays et dates |
| Profil public GitHub | Nom d'utilisateur ou URL du profil | Biographie publique, compteurs, date de création et cinq dépôts publics récents |
| Profils de plateformes chinoises | URL de profil, texte partagé ou identifiant utilisateur de la plateforme | Titre et description accessibles, état d'accès, source et heure de recherche |
| Localisation IP | IPv4 / IPv6 publique | Localisation estimée par une base de données, organisation, fournisseur, ASN et fuseau horaire |
| Mon IP publique | Aucune saisie | Adresse IP publique de sortie du réseau actuel |
| Métadonnées téléphoniques | Numéro et région par défaut | Analyse locale de la région de numérotation, de l'opérateur, des fuseaux horaires, des formats et de la validité |
| Liens par nom d'utilisateur | Nom d'utilisateur | Génère des liens GitHub, Instagram et X sans vérifier l'existence du compte |

Plateformes prises en charge : **Douyin, Xiaohongshu, Kuaishou, Bilibili, Weibo, Zhihu et Douban**. Privilégiez l'URL complète du profil. Certains liens courts de partage de profil Douyin et Xiaohongshu peuvent être résolus. Les noms affichés, les pseudonymes Douyin et les liens de vidéos ou de publications ne remplacent pas l'identifiant de profil requis.

## Utiliser les résultats

- Insérer un exemple sans envoyer de requête ; annuler une recherche et ignorer ses réponses tardives.
- Filtrer les champs et leur contenu, lire les valeurs complètes, copier une valeur ou tous les résultats, ouvrir la source.
- Exporter en JSON, CSV UTF-8 avec BOM ou HTML autonome, avec l'outil, la saisie et l'heure UTC. Le CSV protège les textes pouvant être interprétés comme des formules.
- Windows : double-clic / Ctrl+C pour copier, Entrée pour rechercher, Échap pour annuler. Android : commandes tactiles et sélecteur de documents du système pour exporter.
- Windows conserve au maximum 50 entrées dans l'historique de session. La conservation entre sessions est facultative et désactivée par défaut. Android ne conserve pas durablement l'historique des recherches ; seuls la langue et l'outil choisi sont mémorisés.
- « Enregistrer dans l'archive » associe le profil d'un résultat à un numéro vous appartenant ou publié par son titulaire (avec source et date). La boîte de dialogue Archive de la barre latérale supprime et exporte les enregistrements ; l'outil 12 recherche dans cette archive locale par numéro ou mot-clé.

## Sources, confidentialité et limites

Les requêtes utilisent [RDAP](https://about.rdap.org/), [Google Public DNS](https://developers.google.com/speed/public-dns/docs/doh/json), l'[API publique GitHub](https://docs.github.com/en/rest/users/users#get-a-user), ipwho.is, api.ipify.org et les sites ou profils publics saisis. Les recherches réseau transmettent leur cible au service concerné. Les métadonnées téléphoniques sont analysées localement. Le projet n'utilise ni serveur relais, ni connexion à un compte, ni télémétrie d'usage.

Une connexion obligatoire, un CAPTCHA, JavaScript, une limitation de débit ou une panne peut restreindre les résultats. L'application conserve les données obtenues et l'état des sources ; elle ne contourne pas les contrôles d'accès et ne considère pas HTTP 200 comme une identité vérifiée. Les recherches web acceptent uniquement HTTPS public sur le port 443, vérifient les certificats et limitent les redirections et la taille des réponses. Les valeurs manquantes ne sont pas inventées. Les exports RDAP excluent les coordonnées des titulaires.

**Les régions de numérotation et les positions issues de bases IP ne sont pas la position d'un appareil en temps réel. Aucune recherche inversée de comptes privés par téléphone, identification de nom réel ou association d'identités entre plateformes n'est proposée ; l'archive autorisée ne conserve que les associations que vous enregistrez avec une source déclarée, reste sur cet appareil et peut être supprimée à tout moment.** Consultez uniquement les informations publiques auxquelles vous avez le droit d'accéder et respectez les conditions de chaque service.

Les paramètres Windows et l'historique facultatif se trouvent dans `%LOCALAPPDATA%\GhostTrackDesk` ; l'historique peut être effacé dans l'application. Les journaux d'erreurs n'incluent pas le contenu des requêtes. Android ne demande que l'accès à Internet, sans accès à la position, aux contacts, aux SMS, au téléphone ou à l'ensemble du stockage. Les exports, le presse-papiers et les URL partagées peuvent contenir vos recherches : gérez-les en conséquence.

## Développement et compilation

Python 3.11 x64 ; exemple sous Windows :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe desktop.py
.\.venv\Scripts\python.exe build_windows.py
```

Android nécessite JDK 17 et Android SDK Platform 36 / Build Tools 36.0.0. Le dépôt inclut Gradle Wrapper :

```powershell
$env:JAVA_HOME = 'chemin du JDK 17'
$env:ANDROID_HOME = 'chemin du SDK Android'
.\.venv\Scripts\python.exe build_android.py --gradle .\android\gradlew.bat
```

Les scripts exécutent les tests et produisent les fichiers de distribution et leurs sommes SHA256. Android exécute aussi Lint et vérifie la signature de l'APK. Gardez les clés de signature hors de Git et sauvegardez-les selon le [guide Android en anglais](docs/android.md). L'[exemple de workflow Windows](docs/windows-workflow.example.yml) est un modèle, pas une affirmation qu'une CI hébergée est active.

## Crédits et retours

Extension de [HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack), conservant le point d'entrée `GhostTR.py` et le [README d'origine](UPSTREAM_README.md). Ce projet n'est pas un client officiel des plateformes interrogées.

Dans les [signalements](https://github.com/Serennity007/GhostTrack/issues), indiquez le système, la version et les étapes de reproduction. Ne joignez pas de jetons, de clés privées, d'historique personnel ou de liens privés.
