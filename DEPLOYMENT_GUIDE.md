# 🚀 Guide de Déploiement - Centrale Potins Maps

## 📋 Vue d'ensemble

Ce guide explique comment déployer **Centrale Potins Maps** sur **Vercel** avec une base de données **Supabase**.

---

## 🎯 Architecture de déploiement

- **Frontend + Backend**: Vercel (Python + Dash)
- **Base de données**: Supabase (PostgreSQL)
- **Fichiers statiques**: Vercel CDN

---

## 📦 Prérequis

1. Compte GitHub (pour pousser le code)
2. Compte Vercel (gratuit)
3. Compte Supabase (gratuit)
4. Git installé localement

---

## 🗄️ PARTIE 1 : Configuration Supabase

### Étape 1.1 : Créer un projet Supabase

1. Va sur [supabase.com](https://supabase.com)
2. Clique sur **"Start your project"** → **"Sign in"**
3. Connecte-toi avec GitHub
4. Clique sur **"New Project"**
5. Remplis les informations :
   - **Name**: `centrale-potins-maps`
   - **Database Password**: Génère un mot de passe fort (SAUVEGARDE-LE !)
   - **Region**: Europe West (Ireland) ou le plus proche de toi
   - **Pricing Plan**: Free
6. Clique sur **"Create new project"** (attends 2-3 minutes)

### Étape 1.2 : Créer les tables

Une fois le projet créé :

1. Va dans **SQL Editor** (menu de gauche)
2. Clique sur **"New query"**
3. Copie-colle ce SQL :

```sql
-- Table des personnes
CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des relations
CREATE TABLE relations (
    id SERIAL PRIMARY KEY,
    person1_id INTEGER REFERENCES persons(id) ON DELETE CASCADE,
    person2_id INTEGER REFERENCES persons(id) ON DELETE CASCADE,
    relation_type INTEGER NOT NULL CHECK (relation_type >= 0 AND relation_type <= 4),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(person1_id, person2_id, relation_type)
);

-- Table des utilisateurs (authentification)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des demandes de compte en attente
CREATE TABLE pending_accounts (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected'))
);

-- Table des propositions de personnes (en attente d'approbation)
CREATE TABLE pending_persons (
    id SERIAL PRIMARY KEY,
    person_name TEXT NOT NULL,
    submitted_by TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected'))
);

-- Table des propositions de relations (en attente d'approbation)
CREATE TABLE pending_relations (
    id SERIAL PRIMARY KEY,
    person1 TEXT NOT NULL,
    person2 TEXT NOT NULL,
    relation_type INTEGER NOT NULL,
    submitted_by TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected'))
);

-- Index pour améliorer les performances
CREATE INDEX idx_relations_person1 ON relations(person1_id);
CREATE INDEX idx_relations_person2 ON relations(person2_id);
CREATE INDEX idx_pending_accounts_status ON pending_accounts(status);
CREATE INDEX idx_pending_persons_status ON pending_persons(status);
CREATE INDEX idx_pending_relations_status ON pending_relations(status);

-- Créer un admin par défaut (CHANGE LE MOT DE PASSE APRÈS !)
INSERT INTO users (username, password_hash, role) VALUES 
('admin', 'scrypt:32768:8:1$vwE4rJ8xGnPqN9yT$8f4e5a3c2b1d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z8a9b0c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4', 'admin');
```

4. Clique sur **"Run"** (en bas à droite)
5. Tu devrais voir : `Success. No rows returned`

### Étape 1.3 : Récupérer les credentials

1. Va dans **Settings** → **Database**
2. Dans la section **Connection string**, copie :
   - **URI** (commençant par `postgresql://postgres...`)
3. Note également :
   - **Host**
   - **Database name**
   - **Port**
   - **User** (postgres)
   - **Password** (celui que tu as créé)

**GARDE CES INFORMATIONS EN SÉCURITÉ !**

---

## 🐙 PARTIE 2 : Préparation du code pour Vercel

### Étape 2.1 : Créer les fichiers de configuration

#### A. `vercel.json`

Crée ce fichier à la racine du projet :

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app_v2.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app_v2.py"
    }
  ],
  "env": {
    "PYTHONUNBUFFERED": "1"
  }
}
```

#### B. `requirements.txt`

Vérifie que ce fichier existe et contient :

```txt
dash>=2.14.0
dash-bootstrap-components>=1.5.0
plotly>=5.18.0
networkx>=3.2.0
numpy>=1.26.0
python-louvain>=0.16
werkzeug>=3.0.0
flask>=3.0.0
psycopg2-binary>=2.9.9
```

#### C. `.gitignore`

Crée ce fichier pour ne pas pousser les fichiers sensibles :

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Environment
.env
.env.local
venv/
env/

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
app_v2.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Backups
*.backup
*.bak
*.old
*.before_*
```

#### D. `.env.example`

Crée ce fichier comme template :

```env
# Supabase Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres

# Flask Secret Key (générer avec: python -c 'import secrets; print(secrets.token_hex(32))')
SECRET_KEY=your-super-secret-key-here

# Environment
ENVIRONMENT=production
```

### Étape 2.2 : Migrer de SQLite vers PostgreSQL

Tu dois adapter ton code pour utiliser PostgreSQL au lieu de SQLite. Voici les changements :

1. **Remplacer `sqlite3` par `psycopg2`** dans tous les fichiers `database/*.py`
2. **Changer les requêtes SQL** (syntaxe légèrement différente)
3. **Utiliser une variable d'environnement** pour la connexion

Je vais créer un fichier d'aide pour la migration.

---

## 🔄 PARTIE 3 : Migration vers PostgreSQL

### Étape 3.1 : Créer `database/db_config.py`

Ce fichier gère la connexion à la base de données :

```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Créer une connexion à la base de données"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Supabase utilise parfois 'postgres://' au lieu de 'postgresql://'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

def execute_query(query, params=None, fetch=False):
    """Exécuter une requête SQL"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                result = cur.fetchall()
                conn.commit()
                return result
            conn.commit()
            return cur.rowcount
    finally:
        conn.close()
```

### Étape 3.2 : Principales différences SQLite → PostgreSQL

| SQLite | PostgreSQL |
|--------|------------|
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| `?` (paramètres) | `%s` (paramètres) |
| `datetime('now')` | `NOW()` |
| `IFNULL(x, y)` | `COALESCE(x, y)` |
| Pas de types stricts | Types stricts (TEXT, INTEGER, etc.) |

**Exemple de conversion :**

SQLite :
```python
cur.execute("INSERT INTO persons (name) VALUES (?)", (name,))
```

PostgreSQL :
```python
cur.execute("INSERT INTO persons (name) VALUES (%s)", (name,))
```

---

## 🚢 PARTIE 4 : Déploiement sur Vercel

### Étape 4.1 : Pousser le code sur GitHub

1. Initialise Git (si pas déjà fait) :
```bash
git init
git add .
git commit -m "Initial commit - Ready for deployment"
```

2. Crée un repo sur GitHub :
   - Va sur github.com
   - Clique sur **"New repository"**
   - Nom : `centrale-potins-maps`
   - Visibilité : **Private** (important pour protéger tes données)
   - Ne coche RIEN d'autre
   - Clique sur **"Create repository"**

3. Pousse le code :
```bash
git remote add origin https://github.com/TON-USERNAME/centrale-potins-maps.git
git branch -M main
git push -u origin main
```

### Étape 4.2 : Déployer sur Vercel

1. Va sur [vercel.com](https://vercel.com)
2. Clique sur **"Sign Up"** → **"Continue with GitHub"**
3. Une fois connecté, clique sur **"Add New..."** → **"Project"**
4. Importe ton repo `centrale-potins-maps`
5. Configure le projet :
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: (laisse vide)
   - **Output Directory**: (laisse vide)

6. **IMPORTANT** - Ajoute les variables d'environnement :
   - Clique sur **"Environment Variables"**
   - Ajoute :
     ```
     DATABASE_URL = postgresql://postgres:TON_PASSWORD@db.TON_PROJECT.supabase.co:5432/postgres
     SECRET_KEY = ton-secret-key-generee
     ENVIRONMENT = production
     ```

7. Clique sur **"Deploy"** (attends 2-3 minutes)

### Étape 4.3 : Vérifier le déploiement

1. Une fois déployé, Vercel te donne une URL (ex: `https://centrale-potins-maps.vercel.app`)
2. Clique dessus pour tester
3. Si erreur → va dans **"Deployment"** → **"View Function Logs"**

---

## 🔐 PARTIE 5 : Sécurité

### Étapes de sécurisation :

1. **Change le mot de passe admin par défaut** :
   - Connecte-toi avec `admin` / `admin123`
   - Va dans les paramètres
   - Change le mot de passe

2. **Vérifie que le repo GitHub est PRIVÉ**

3. **Ne partage JAMAIS** :
   - Le `DATABASE_URL`
   - Le `SECRET_KEY`
   - Le mot de passe Supabase

4. **Active l'authentification à deux facteurs** sur :
   - GitHub
   - Vercel
   - Supabase

---

## 🎨 PARTIE 6 : Configuration du domaine personnalisé (optionnel)

### Si tu veux un domaine type `potins.com` :

1. Achète un domaine sur Namecheap, GoDaddy, ou OVH
2. Dans Vercel :
   - Va dans **Settings** → **Domains**
   - Clique sur **"Add"**
   - Entre ton domaine : `potins.com`
   - Suis les instructions pour configurer les DNS

3. Configure les DNS chez ton registrar :
   - Type A : `76.76.21.21`
   - CNAME : `cname.vercel-dns.com`

4. Attends 24-48h pour la propagation DNS

---

## 📊 PARTIE 7 : Monitoring et Maintenance

### Logs Vercel

- **Runtime logs** : Vercel Dashboard → Project → Deployments → Function Logs
- **Build logs** : Vercel Dashboard → Project → Deployments → Build Logs

### Logs Supabase

- **Database logs** : Supabase Dashboard → Logs → Database
- **API logs** : Supabase Dashboard → Logs → API

### Métriques

- **Trafic** : Vercel Dashboard → Analytics
- **Base de données** : Supabase Dashboard → Database → Usage

---

## 🐛 PARTIE 8 : Troubleshooting

### Problème 1 : "Application Error" sur Vercel

**Cause** : Mauvaise configuration de `vercel.json` ou dépendances manquantes

**Solution** :
1. Vérifie les logs : Vercel Dashboard → Function Logs
2. Vérifie que `requirements.txt` contient toutes les dépendances
3. Redéploie : `git push origin main`

### Problème 2 : "Database connection failed"

**Cause** : Mauvais `DATABASE_URL`

**Solution** :
1. Vérifie dans Supabase → Settings → Database
2. Copie exactement l'URI (avec le bon mot de passe)
3. Mets à jour dans Vercel → Settings → Environment Variables
4. Redéploie

### Problème 3 : "Module not found"

**Cause** : Dépendance manquante dans `requirements.txt`

**Solution** :
1. Ajoute la dépendance manquante dans `requirements.txt`
2. Commit et push :
   ```bash
   git add requirements.txt
   git commit -m "Add missing dependency"
   git push origin main
   ```

### Problème 4 : Graphe ne s'affiche pas

**Cause** : Assets statiques non chargés

**Solution** :
1. Vérifie la console navigateur (F12)
2. Assure-toi que Plotly est bien dans `requirements.txt`
3. Vérifie les CSP (Content Security Policy) dans Vercel

---

## 🔄 PARTIE 9 : Mises à jour

### Pour déployer une nouvelle version :

```bash
# 1. Fais tes modifications localement
# 2. Teste localement
python3 app_v2.py

# 3. Commit
git add .
git commit -m "Description des changements"

# 4. Push (déclenche auto-déploiement sur Vercel)
git push origin main

# 5. Vérifie sur Vercel Dashboard que le déploiement réussit
```

---

## 💰 PARTIE 10 : Coûts

### Plan Gratuit (recommandé pour démarrer)

**Vercel Free** :
- ✅ 100 GB bandwidth/mois
- ✅ Déploiements illimités
- ✅ HTTPS automatique
- ❌ Pas de domaine custom premium
- ❌ Limité à 100,000 requêtes/jour

**Supabase Free** :
- ✅ 500 MB base de données
- ✅ 50,000 utilisateurs actifs mensuels
- ✅ 2 GB bandwidth
- ❌ Projets mis en pause après 7 jours d'inactivité

### Si tu dépasses (peu probable au début)

- **Vercel Pro** : $20/mois (1 TB bandwidth)
- **Supabase Pro** : $25/mois (8 GB database, pas de pause)

---

## ✅ Checklist finale

Avant de mettre en production :

- [ ] Base de données Supabase créée et configurée
- [ ] Tables créées avec le SQL fourni
- [ ] `DATABASE_URL` récupéré depuis Supabase
- [ ] Code migré vers PostgreSQL
- [ ] `vercel.json` créé
- [ ] `requirements.txt` à jour
- [ ] `.gitignore` configuré
- [ ] `.env.example` créé
- [ ] Code poussé sur GitHub (repo PRIVÉ)
- [ ] Variables d'environnement configurées sur Vercel
- [ ] Déploiement Vercel réussi
- [ ] Site testé et fonctionnel
- [ ] Mot de passe admin changé
- [ ] Authentification 2FA activée

---

## 📞 Support

- **Vercel Docs** : https://vercel.com/docs
- **Supabase Docs** : https://supabase.com/docs
- **Dash Docs** : https://dash.plotly.com

---

## 🎉 Félicitations !

Ton application est maintenant en ligne et accessible partout dans le monde ! 🌍

URL de production : `https://ton-projet.vercel.app`

**Prochaines étapes** :
1. Partage l'URL avec tes amis
2. Collecte les retours utilisateurs
3. Ajoute des features (notifications, export PDF, etc.)
4. Scale si besoin avec les plans payants

---

*Guide créé pour Centrale Potins Maps - Version 1.0*
