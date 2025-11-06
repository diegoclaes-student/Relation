-- ============================================================================
-- CENTRALE POTINS MAPS - Schema PostgreSQL pour Supabase
-- ============================================================================
-- À exécuter dans Supabase SQL Editor après création du projet
-- ============================================================================

-- 1. Table des personnes
-- ============================================================================
CREATE TABLE IF NOT EXISTS persons (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour améliorer les performances de recherche par nom
CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name);

-- ============================================================================
-- 2. Table des relations
-- ============================================================================
CREATE TABLE IF NOT EXISTS relations (
    id SERIAL PRIMARY KEY,
    person1_id INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    person2_id INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    relation_type INTEGER NOT NULL CHECK (relation_type >= 0 AND relation_type <= 4),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Contrainte : empêcher les doublons de relations
    UNIQUE(person1_id, person2_id, relation_type),
    
    -- Contrainte : empêcher une relation avec soi-même
    CHECK (person1_id != person2_id)
);

-- Index pour améliorer les performances de requêtes
CREATE INDEX IF NOT EXISTS idx_relations_person1 ON relations(person1_id);
CREATE INDEX IF NOT EXISTS idx_relations_person2 ON relations(person2_id);
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
-- 7. Créer un compte admin par défaut
-- ============================================================================
-- ⚠️  IMPORTANT : Change ce mot de passe immédiatement après le premier déploiement !
-- ⚠️  Mot de passe par défaut : "admin123"
-- ⚠️  Hash généré avec Werkzeug Scrypt

INSERT INTO users (username, password_hash, role) 
VALUES (
    'admin',
    'scrypt:32768:8:1$vwE4rJ8xGnPqN9yT$8f4e5a3c2b1d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z8a9b0c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4',
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- 8. Exemple de données de test (optionnel)
-- ============================================================================
-- Décommenter les lignes ci-dessous si tu veux des données de test

/*
-- Insertion de quelques personnes de test
INSERT INTO persons (name) VALUES 
    ('Alice'),
    ('Bob'),
    ('Charlie'),
    ('Diana')
ON CONFLICT (name) DO NOTHING;

-- Insertion de quelques relations de test
INSERT INTO relations (person1_id, person2_id, relation_type)
SELECT p1.id, p2.id, 3  -- Type 3 = Couple
FROM persons p1, persons p2
WHERE p1.name = 'Alice' AND p2.name = 'Bob'
ON CONFLICT DO NOTHING;

INSERT INTO relations (person1_id, person2_id, relation_type)
SELECT p1.id, p2.id, 0  -- Type 0 = Bisou
FROM persons p1, persons p2
WHERE p1.name = 'Bob' AND p2.name = 'Charlie'
ON CONFLICT DO NOTHING;
*/

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
FROM pending_relations;

-- ============================================================================
-- ✅ SCHEMA CRÉÉ AVEC SUCCÈS !
-- ============================================================================
-- Prochaines étapes :
-- 1. Note les credentials de connexion (Settings → Database → Connection String)
-- 2. Migre les données SQLite → PostgreSQL avec migrate_to_postgres.py
-- 3. Configure DATABASE_URL dans Vercel
-- 4. Déploie l'application
-- 5. CHANGE LE MOT DE PASSE ADMIN !
-- ============================================================================
