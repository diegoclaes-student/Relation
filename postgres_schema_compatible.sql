-- ============================================================================
-- CENTRALE POTINS MAPS - Schema PostgreSQL COMPATIBLE avec le code existant
-- ============================================================================
-- Ce schéma est compatible avec la structure utilisée dans le code Python
-- qui utilise les NOMS des personnes (TEXT) au lieu des IDs
-- ============================================================================

-- ============================================================================
-- 1. Table des personnes
-- ============================================================================
CREATE TABLE IF NOT EXISTS persons (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    gender TEXT,
    sexual_orientation TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour améliorer les performances de recherche par nom
CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name);

-- ============================================================================
-- 2. Table des relations (UTILISE LES NOMS en TEXT, pas les IDs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS relations (
    id SERIAL PRIMARY KEY,
    person1 TEXT NOT NULL,
    person2 TEXT NOT NULL,
    relation_type INTEGER DEFAULT 0 CHECK (relation_type >= 0 AND relation_type <= 4),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(person1, person2, relation_type)
);

-- Index pour améliorer les performances de requêtes
CREATE INDEX IF NOT EXISTS idx_relations_person1 ON relations(person1);
CREATE INDEX IF NOT EXISTS idx_relations_person2 ON relations(person2);
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(relation_type);

-- ============================================================================
-- 3. Table des utilisateurs (authentification)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour améliorer les performances de login
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ============================================================================
-- 4. Table des demandes de compte en attente
-- ============================================================================
CREATE TABLE IF NOT EXISTS pending_accounts (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected'))
);

-- Index pour filtrer par statut
CREATE INDEX IF NOT EXISTS idx_pending_accounts_status ON pending_accounts(status);

-- ============================================================================
-- 5. Table des propositions de personnes (en attente d'approbation)
-- ============================================================================
CREATE TABLE IF NOT EXISTS pending_persons (
    id SERIAL PRIMARY KEY,
    person_name TEXT NOT NULL,
    submitted_by TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected'))
);

-- Index pour filtrer par statut
CREATE INDEX IF NOT EXISTS idx_pending_persons_status ON pending_persons(status);

-- ============================================================================
-- 6. Table des propositions de relations (en attente d'approbation)
-- ============================================================================
CREATE TABLE IF NOT EXISTS pending_relations (
    id SERIAL PRIMARY KEY,
    person1 TEXT NOT NULL,
    person2 TEXT NOT NULL,
    relation_type INTEGER NOT NULL CHECK (relation_type >= 0 AND relation_type <= 4),
    submitted_by TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected'))
);

-- Index pour filtrer par statut
CREATE INDEX IF NOT EXISTS idx_pending_relations_status ON pending_relations(status);

-- ============================================================================
-- 7. Table d'historique (pour audit)
-- ============================================================================
CREATE TABLE IF NOT EXISTS history (
    id SERIAL PRIMARY KEY,
    action_type TEXT NOT NULL,
    person1 TEXT,
    person2 TEXT,
    relation_type INTEGER,
    performed_by TEXT DEFAULT 'system',
    details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_history_action ON history(action_type);
CREATE INDEX IF NOT EXISTS idx_history_created ON history(created_at);

-- ============================================================================
-- 8. Créer un compte admin par défaut
-- ============================================================================
-- Note: Ce mot de passe doit correspondre à celui dans config.py
-- Par défaut dans config.py : ADMIN_PASSWORD = "admin123"

-- Pour générer le hash, utilise :
-- python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('admin123', method='scrypt'))"

-- ⚠️  IMPORTANT : Change ce mot de passe immédiatement après le premier déploiement !

-- Le compte admin sera créé par le code Python au démarrage via config.py

-- ============================================================================
-- 9. Vérification finale
-- ============================================================================
-- Afficher le nombre d'enregistrements dans chaque table

SELECT 
    'persons' as table_name, 
    COUNT(*) as count 
FROM persons

UNION ALL

SELECT 
    'relations' as table_name, 
    COUNT(*) as count 
FROM relations

UNION ALL

SELECT 
    'users' as table_name, 
    COUNT(*) as count 
FROM users

UNION ALL

SELECT 
    'pending_accounts' as table_name, 
    COUNT(*) as count 
FROM pending_accounts

UNION ALL

SELECT 
    'pending_persons' as table_name, 
    COUNT(*) as count 
FROM pending_persons

UNION ALL

SELECT 
    'pending_relations' as table_name, 
    COUNT(*) as count 
FROM pending_relations

UNION ALL

SELECT 
    'history' as table_name, 
    COUNT(*) as count 
FROM history;

-- ============================================================================
-- ✅ SCHEMA CRÉÉ AVEC SUCCÈS !
-- ============================================================================
-- Prochaines étapes :
-- 1. Exécute ce script dans ton dashboard Render PostgreSQL
-- 2. Vérifie que toutes les tables sont créées
-- 3. Migre les données si nécessaire
-- 4. Déploie l'application
-- ============================================================================
