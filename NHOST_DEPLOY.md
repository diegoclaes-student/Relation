# Déploiement gratuit : Vercel (Docker) + Nhost (Postgres)

Ce guide décrit, étape par étape, comment déployer votre application `Relation`
gratuitement en combinant Vercel (hébergement du conteneur) et Nhost (Postgres
managé). L'idée : le conteneur exécute Gunicorn / Flask / Dash, et la BD est
hébergée sur Nhost.

PRÉREQUIS
---------
- Compte GitHub (repo poussé)
- Compte Vercel
- Compte Nhost
- Dockerfile présent dans le repo (déjà fourni)
- `vercel.json` présent (déjà fourni)

RAPPEL: l'approche ci‑dessous suppose que vous migrerez SQLite vers Postgres
(Nhost). Si vous préférez rester sur SQLite, Nhost/Vercel n'est pas adapté pour
le stockage local.

1) Créer un projet Nhost
------------------------
1. Allez sur https://nhost.io et inscrivez-vous
2. Créez un nouveau projet (choisir région la plus proche)
3. Dans Dashboard → Settings → Database, récupérez la **Postgres connection string** (DATABASE_URL)

2) Préparer localement la migration
-----------------------------------
1. Créez un environnement virtuel et installez les dépendances:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. Exportez la variable d'environnement:
```bash
export DATABASE_URL='postgres://postgres:[e8ZKjjzDvS5Ap48A]@xaoectybwqoclobtiwvi.db.eu-central-1.nhost.run:5432/xaoectybwqoclobtiwvi'
```
3. Lancez la migration (testez d'abord sur un projet Nhost de staging):
```bash
python scripts/migrate_sqlite_to_postgres.py --sqlite-db ./social_network.db
```
4. Vérifiez les données dans Nhost Dashboard → Table editor (persons, relations, history)

3) Préparer Vercel (déploiement Docker)
---------------------------------------
1. Poussez vos changements sur GitHub
2. Connectez votre repo à Vercel et créez un nouveau projet
3. Dans Project Settings → Environment Variables, ajoutez :
   - `DATABASE_URL` = la connection string fournie par Nhost
   - `SECRET_KEY` = clé secrète
   - `ADMIN_PASSWORD` = mot de passe admin
   - `DEBUG` = False
4. Déployez le projet : Vercel va builder l'image Docker en utilisant `vercel.json`

4) Vérifications post‑déploiement
--------------------------------
- Accédez à l'URL fournie par Vercel
- Effectuez les tests suivants :
  - Créer/éditer/supprimer une personne
  - Vérifier que l'historique enregistre les actions
  - Vérifier que la suppression d'une personne supprime (ou marque supprimée) les relations

5) Backups et maintenance
-------------------------
- Nhost propose des sauvegardes automatiques, mais vérifiez votre plan
- Pour sauvegarder manuellement : export SQL depuis Nhost Dashboard

6) FAQs / problèmes connus
--------------------------
- Erreur d'installation `psycopg2` pendant le build Docker :
  - Dans Dockerfile nous avons déjà `build-essential` installé; si le build
    échoue, assurez-vous que l'image Docker base est `python:3.11-slim` ou
    une image contenant les dépendances de compilation.
- Limites du plan gratuit Nhost : connexions simultanées / stockage, surveillez
  l'utilisation et passez sur un plan supérieur si besoin.

7) Automatisation (optionnel)
----------------------------
- Vous pouvez ajouter un script GitHub Actions qui construit et push l'image puis
  notifie Vercel (ou déclenche un déploiement). Je peux ajouter ce workflow si
  vous le souhaitez.


Si vous voulez, je peux :
- Générer un `VERCEL_DEPLOY.md` avec toutes les valeurs prêtes à copier-coller
- Améliorer le script de migration pour gérer la totalité du schéma `history`
  (old_value/new_value/etc.) si vous me donnez un exemple de lignes
- Créer un workflow GitHub Actions pour automatiser build/push/deploy
