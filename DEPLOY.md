# Déploiement de l'application

Ce document explique comment déployer l'application `Relation` sur un hébergeur cloud.

Important: l'application utilise actuellement SQLite (`social_network.db`) dans le répertoire de l'application. Pour un déploiement en production, préférez :
- utiliser un disque persistant (Render/Fly volumes) pour conserver le fichier SQLite, ou
- migrer vers une base de données gérée (Postgres) si vous attendez une charge concurrente.

Options recommandées
---------------------
1) Render (recommandé pour simplicité)
-------------------------------------
- Avantages : support Docker/Gunicorn, disques persistants, déploiement depuis GitHub

Étapes (Render):
1. Connectez votre repo GitHub à Render
2. Créez un **Web Service** -> Choisissez Dockerfile (le repo contient un `Dockerfile`)
3. Configurez la variable d'environnement `PORT=8051` (Render la fournira automatiquement parfois)
4. Si vous restez sur SQLite, activez un **Persistent Disk** et définissez `DB_PATH=/data/social_network.db` (ou modifiez `config.py` pour lire DB_PATH depuis l'env)
5. Déployez et surveillez les logs depuis le dashboard

2) Fly.io (très bon pour Docker + volumes)
-----------------------------------------
- Avantages : facile d'utiliser Docker, volumes persistants, proxys et scaling.

Étapes (Fly.io):
1. Installez `flyctl`
2. Initialisez l'app: `flyctl launch` (suivez l'assistant, choisissez région)
3. Créez un volume pour sqlite: `flyctl volumes create data --size 10` et montez-le sur `/data`
4. Définissez `PORT=8051` et autres secrets via `flyctl secrets set ADMIN_PASSWORD=...`
5. `flyctl deploy`

3) Vercel (déploiement Docker possible, limites et procédure)
------------------------------------------------------------
Vercel est historiquement orienté front-end et serverless, mais il supporte le
déploiement de conteneurs Docker. Voici comment procéder si vous voulez
absolument déployer sur Vercel en conservant votre application Dash/Flask.

Limites importantes à connaître
--------------------------------
- Vercel ne fournit pas de disque persistant pour les conteneurs. Tout fichier
	écrit dans le système de fichiers du conteneur est éphémère (sera perdu au
	redéploiement ou scale). Par conséquent, **SQLite ne doit pas être utilisé
	comme stockage principal** sur Vercel à moins d'avoir une stratégie externe
	de sauvegarde / synchronisation.
- Les fonctions serverless Vercel (Serverless Functions) ne sont pas adaptées
	pour un processus long-running comme Gunicorn; vous devez déployer en
	conteneur Docker afin d’exécuter Gunicorn.

Deux approches sur Vercel
-------------------------
1) Docker sur Vercel (recommandé si vous voulez rester sur votre code sans
	 réécrire la partie DB)
	 - Avantages : vous pouvez lancer Gunicorn dans le container exactement
		 comme localement.
	 - Inconvénients : pas de disque persistant -> vous devrez utiliser une DB
		 externe (Postgres) ou un service de stockage externe pour les backups.

2) Migrer la DB vers un service externe (Postgres/RDS/Cloud SQL)
	 - Avantages : scalabilité, backups gérés, connexion via `DATABASE_URL`.
	 - Inconvénients : travail de migration (scripts, dépendances et tests).

Procédure Docker pour Vercel (pas à pas)
----------------------------------------
1. Assurez-vous que votre repo contient un `Dockerfile` (déjà présent).
2. Ajoutez `vercel.json` à la racine (une version d'exemple est fournie dans
	 le repo). Le contenu instructe Vercel d'utiliser le builder Docker.
3. Configurez les variables d'environnement dans le dashboard Vercel :
	 - `DATABASE_URL` (si vous utilisez Postgres)
	 - `ADMIN_PASSWORD`, `SECRET_KEY`, `DB_PATH` (si vous utilisez un stockage
		 externe monté ailleurs), `DEBUG=False`.
4. Si vous restez sur SQLite malgré les limites, configurez un processus
	 externe qui synchronise régulièrement le fichier DB vers un stockage
	 (e.g., S3) — NOTE: c'est fragile et non recommandé pour production.
5. Déployez depuis Git (Vercel buildera l'image Docker et l'exécutera).

Exemples de variables ENV à définir dans Vercel
-----------------------------------------------
- `SECRET_KEY` = votre clé secrète
- `ADMIN_PASSWORD` = mot de passe admin
- `DATABASE_URL` = postgres://user:pass@host:port/dbname (préféré)
- `DEBUG` = False

Vaut-il le coup de déployer sur Vercel ?
-------------------------------------
Si vous voulez simplicité et que vous êtes prêts à migrer vers Postgres ou à
utiliser un autre service pour la persistance (S3/DB), Vercel est acceptable.
Si vous voulez garder SQLite sur un volume persisté, préférez Render ou Fly.io.

Ajouts pratiques fournis dans le repo
-------------------------------------
- `Dockerfile` : image et commande Gunicorn (déjà fournie)
- `vercel.json` : fichier de configuration pour builder Docker (ajouté)

Souhaitez-vous que je génère automatiquement :
- un `Dockerfile` adapté (déjà présent),
- une mise à jour de `config.py` pour utiliser `DATABASE_URL` si présent,
- un script d'init pour créer la DB sur le volume / script de migration vers
	Postgres ?


4) Vercel + Nhost (déploiement gratuit possible)
---------------------------------------------
Si vous souhaitez une option gratuite, combiner Vercel (pour l'hébergement
du conteneur) et Nhost (Postgres managé dans le plan gratuit) est une très
bonne solution pour mettre en production rapidement sans coût.

Pourquoi Nhost ?
- Nhost fournit une base Postgres managée, API GraphQL, Auth et Storage (S3
	compatible) et propose un plan gratuit adapté aux petits projets.
- Ici nous n'utiliserons que la base Postgres (DATABASE_URL) pour remplacer
	SQLite.

Étapes globales :
1. Créez un compte sur https://nhost.io et créez un nouveau projet (choisissez la région)
2. Dans le Dashboard Nhost, récupérez la `DATABASE_URL` (Connection string Postgres)
3. Dans votre repo, `vercel.json` est déjà présent pour builder le Dockerfile
4. Dans Vercel Dashboard -> Project Settings -> Environment Variables, ajoutez :
	 - `DATABASE_URL` = la valeur fournie par Nhost
	 - `SECRET_KEY` = une clé secrète
	 - `ADMIN_PASSWORD` = mot de passe admin
	 - `DEBUG` = False
5. Déployez sur Vercel : le container aura accès à la base Nhost et stockera
	 les données dans Postgres

Migration des données locales (SQLite -> Nhost/Postgres):
- Localement, installez `psycopg2-binary` et définissez `DATABASE_URL` vers
	votre instance Nhost de test.
- Lancez `python scripts/migrate_sqlite_to_postgres.py --sqlite-db ./social_network.db`
- Vérifiez dans Nhost Dashboard que les tables `persons`, `relations`, `history` ont bien été créées et importées.

Conseils et limites:
- Le plan gratuit Nhost a des quotas de stockage/connexion; vérifiez qu'il
	convient à votre usage de production.
- Testez toujours la migration sur un projet Nhost de test avant la prod.



Autres alternatives
-------------------
- Railway.app : bon pour prototypage (héberge Docker ou services)
- DigitalOcean App Platform / Droplets
- Heroku (dépréciée pour nouveaux projets mais simple : utilise Procfile)

Préparations recommandées avant déploiement
-------------------------------------------
1. Rendre `DB_PATH` configurable via variable d'environnement. Exemple minimal :

```python
# dans config.py
import os
from pathlib import Path
BASE_DIR = Path(__file__).parent
DB_PATH = Path(os.getenv('DB_PATH', BASE_DIR / 'social_network.db'))
```

Je peux appliquer ce changement si vous voulez.

2. Assurez-vous que `server.secret_key` est défini via `os.environ` en prod (changer la valeur codée en dur).

3. Configurez les variables d'environnement sur le host :
- `ADMIN_USERNAME`, `ADMIN_PASSWORD`
- `DB_PATH` (p.ex. `/data/social_network.db` si vous utilisez un volume)
- `SECRET_KEY` (ou `FLASK_SECRET_KEY`)

Commandes utiles (local / Docker)
---------------------------------
Construire l'image Docker localement :

```bash
cd /Users/diegoclaes/Code/Relation
docker build -t relation-app .
```

Lancer en local :

```bash
docker run --rm -p 8051:8051 -e ADMIN_PASSWORD=yourpass -e DB_PATH=/data/social_network.db relation-app
```

Si vous utilisez un volume local pour SQLite :

```bash
docker run --rm -p 8051:8051 -v $(pwd)/data:/data -e DB_PATH=/data/social_network.db relation-app
```

Déploiement GitHub → Render (rapide)
-----------------------------------
1. Poussez vos changements sur GitHub
2. Créez un service Web sur Render et connectez votre repo
3. Choisissez Docker et laissez Render builder
4. Ajoutez les secrets/env vars (ADMIN_PASSWORD, DB_PATH si nécessaire)

Checklist de production
-----------------------
- [ ] DB persistante (volume ou DB managée)
- [ ] Secrets en variables d'environnement
- [ ] `DEBUG=False` en production (modifier `config.py` ou via env)
- [ ] Utiliser un vrai `SECRET_KEY`
- [ ] Monitoring/logs (Render / Fly / Papertrail)

Si vous voulez, je peux :
- Modifier `config.py` pour lire `DB_PATH` et `SECRET_KEY` depuis l'environnement
- Ajouter un script d'initialisation pour créer le fichier SQLite sur le volume
- Créer une configuration `fly.toml` pour Fly.io

Dites-moi laquelle des options (Render / Fly / Vercel / Railway) vous préférez, je prépare les étapes exactes et je peux générer les fichiers de configuration automatiquement.
