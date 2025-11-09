-- Script pour corriger le schéma PostgreSQL sur Nhost
-- Exécutez ce script dans la console SQL de Nhost

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

-- 2. Migrer les données de la table admins vers users (si elle existe)
-- Tous les admins ont is_admin = TRUE
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'admins') THEN
        INSERT INTO users (username, password_hash, is_admin, created_at, is_active)
        SELECT username, password_hash, TRUE, created_at, TRUE
        FROM admins
        ON CONFLICT (username) DO NOTHING;
        
        -- Optionnel: supprimer l'ancienne table admins après migration
        -- DROP TABLE admins;
    END IF;
END $$;

-- 3. Créer la table pending_accounts pour les demandes de compte
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
