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

3) Vercel (LIMITATIONS)
------------------------
Vercel est optimisé pour les apps front-end et serverless. Déployer une app Dash/Flask persistante sur Vercel est possible mais peu pratique :
- Les fonctions serverless n'ont pas de processus long-running (pas idéal pour websockets / sessions persistantes)
- Pas de disque persistant pour SQLite (les fichiers écrits dans l'environnement sont éphémères)

Si vous tenez à Vercel :
- Utilisez la configuration Docker (Vercel peut déployer des conteneurs) ou
- Migrez la DB vers un service externe (Postgres) et exposez l'app via une fonction serverless (complexe)

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
