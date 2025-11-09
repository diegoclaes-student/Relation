# Correction du Schéma PostgreSQL sur Render

## Problème
La table `users` n'a pas les colonnes nécessaires (`is_admin`, `is_active`, `last_login`). Le script de migration a créé une table `admins` mais l'application attend une table `users`.

## Solution avec Render PostgreSQL

### Étape 1: Accéder à votre base de données Render

1. **Via le Dashboard Render**:
   - Allez sur https://dashboard.render.com
   - Sélectionnez votre service PostgreSQL
   - Cliquez sur "Connect" → "External Connection"
   - Notez les informations de connexion (ou copiez la `DATABASE_URL`)

2. **Récupérer votre DATABASE_URL**:
   - Elle devrait être dans les variables d'environnement de votre web service
   - Format: `postgresql://user:password@host:port/database`

### Étape 2: Exécuter le SQL de correction

#### Option A: Via psql (si installé localement)

```bash
# Connectez-vous avec votre DATABASE_URL
psql "votre_database_url_render"

# Puis exécutez le SQL ci-dessous
```

#### Option B: Via le Shell Render (RECOMMANDÉ)

1. Dans votre dashboard Render, cliquez sur votre service PostgreSQL
2. Cliquez sur "Shell" ou "Connect" → "PSQL Command"
3. Copiez-collez le SQL suivant:

```sql
-- 1. Créer la table users avec tous les champs nécessaires
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. Migrer les données de la table admins vers users
INSERT INTO users (username, password_hash, is_admin, created_at, is_active)
SELECT username, password_hash, TRUE, created_at, TRUE
FROM admins
ON CONFLICT (username) DO NOTHING;

-- 3. Créer la table pending_accounts
CREATE TABLE IF NOT EXISTS pending_accounts (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'
);

-- 4. Vérifier que tout est OK
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'pending_accounts', COUNT(*) FROM pending_accounts
UNION ALL
SELECT 'persons', COUNT(*) FROM persons
UNION ALL
SELECT 'relations', COUNT(*) FROM relations
UNION ALL
SELECT 'history', COUNT(*) FROM history;

-- 5. Afficher les colonnes de users pour vérifier
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
```

#### Option C: Via le script Python

```bash
# 1. Récupérer votre DATABASE_URL depuis Render
# Dans Dashboard → PostgreSQL Service → Connect → Internal Database URL

# 2. Exporter la variable
export DATABASE_URL="votre_database_url_render"

# 3. Installer psycopg2 si nécessaire
pip install psycopg2-binary

# 4. Exécuter le script
python scripts/fix_postgres_schema.py
```

### Étape 3: Vérifier les résultats

Vous devriez voir:
- ✅ **users**: 1 enregistrement (votre admin)
- ✅ **Colonnes**: id, username, password_hash, is_admin, created_at, last_login, is_active

### Étape 4: Redéployer votre application

Render redéploie automatiquement à chaque push sur GitHub, mais vous pouvez aussi:
1. Aller sur votre Web Service dans Render
2. Cliquer "Manual Deploy" → "Deploy latest commit"
3. Attendre que le déploiement soit terminé

### Étape 5: Tester la connexion

1. Accédez à votre application: `https://votre-app.onrender.com`
2. Essayez de vous connecter avec vos identifiants admin
3. ✅ Cela devrait fonctionner!

## Informations Render Importantes

### Variables d'environnement à vérifier

Dans votre Web Service Render, assurez-vous que ces variables sont définies:

```bash
DATABASE_URL=postgresql://...  # Fourni automatiquement par Render
SECRET_KEY=votre_secret_key_unique
ADMIN_PASSWORD=votre_mot_de_passe_admin
DEBUG=False
PORT=10000  # Fourni automatiquement par Render
```

### DATABASE_URL Interne vs Externe

- **Internal Database URL**: À utiliser dans votre application Render (recommandé)
  - Format: `postgresql://user:pass@internal-host/db`
  - Plus rapide car reste sur le réseau interne Render
  
- **External Connection String**: Pour se connecter depuis votre machine
  - Format: `postgresql://user:pass@external-host:port/db`
  - Utilisé pour psql local ou scripts de migration

### Après la correction

Une fois le schéma corrigé:
1. ✅ Login fonctionnera
2. ✅ Toutes les fonctionnalités de l'app seront disponibles
3. ✅ L'historique et les modifications seront enregistrés
4. 🔒 Pensez à changer le mot de passe admin par défaut

## Dépannage

### "column is_admin does not exist"
→ Le SQL de correction n'a pas été exécuté. Retournez à l'étape 2.

### "relation admins does not exist"
→ Pas de problème, cela signifie que la table admins n'existe pas. Le script créera directement la table users vide. Vous devrez créer un admin manuellement.

### "could not connect to server"
→ Vérifiez que vous utilisez la bonne DATABASE_URL (internal pour l'app, external pour votre machine)

### Créer un admin manuellement (si nécessaire)

```sql
-- Générez d'abord le hash du mot de passe
-- Ou utilisez ce SQL directement avec un mot de passe temporaire:
INSERT INTO users (username, password_hash, is_admin, created_at, is_active)
VALUES (
    'admin',
    'votre_hash_bcrypt_ou_sha256',
    TRUE,
    CURRENT_TIMESTAMP,
    TRUE
);
```

Ou via Python:
```bash
python -c "from database.users import UserRepository; UserRepository.create_user('admin', 'votre_password', is_admin=True)"
```
