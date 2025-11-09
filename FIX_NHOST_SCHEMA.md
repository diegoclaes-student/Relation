# Correction du Schéma PostgreSQL sur Nhost

## Problème
La table `users` n'a pas les colonnes nécessaires (`is_admin`, `is_active`, `last_login`). L'application utilise une table `users` mais la migration a créé une table `admins`.

## Solution

### Étape 1: Accéder à Nhost SQL Editor
1. Allez sur https://app.nhost.io
2. Sélectionnez votre projet
3. Allez dans "Database" → "SQL Editor"

### Étape 2: Exécuter ce SQL

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
SELECT 'Table créée avec succès' as status;

-- 5. Afficher le nombre d'enregistrements dans chaque table
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'pending_accounts', COUNT(*) FROM pending_accounts
UNION ALL
SELECT 'persons', COUNT(*) FROM persons
UNION ALL
SELECT 'relations', COUNT(*) FROM relations
UNION ALL
SELECT 'history', COUNT(*) FROM history;

-- 6. Afficher les colonnes de la table users pour vérifier
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
```

### Étape 3: Vérifier les résultats
Vous devriez voir:
- ✅ users: 1 enregistrement (votre admin migré depuis la table admins)
- ✅ Les colonnes: id, username, password_hash, is_admin, created_at, last_login, is_active

### Étape 4: Redéployer sur Render
Une fois le schéma corrigé, l'application sur Render pourra se connecter correctement.
Le redéploiement se fera automatiquement si vous faites un commit/push, ou manuellement depuis le dashboard Render.

## Alternative: Exécuter depuis votre machine

Si vous voulez utiliser le script Python au lieu du SQL Editor:

```bash
# Vérifier que psycopg2 est installé
pip install psycopg2-binary

# Exécuter le script
export PGHOST=xaoectybwqoclobtiwvi.db.eu-central-1.nhost.run
export PGPORT=5432
export PGUSER=postgres
export PGPASSWORD=e8ZKjjzDvS5Ap48A
export PGDATABASE=xaoectybwqoclobtiwvi
python scripts/fix_postgres_schema.py
```

Note: Si vous avez un problème de DNS, utilisez l'IP directe de votre instance Nhost ou utilisez le SQL Editor web (recommandé).
