-- ============================================================================
-- SCRIPT DE MIGRATION : Relations ID → TEXT
-- ============================================================================
-- Ce script migre la table 'relations' d'un schéma basé sur IDs
-- vers un schéma basé sur NOMS (TEXT) pour correspondre au code Python
-- ============================================================================

-- ÉTAPE 1 : Vérifier si la migration est nécessaire
-- ============================================================================
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'relations' AND column_name = 'person1_id'
    ) THEN
        RAISE NOTICE '⚠️  Migration nécessaire : relations utilise person1_id/person2_id';
    ELSIF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'relations' AND column_name = 'person1'
    ) THEN
        RAISE NOTICE '✅ Migration déjà effectuée : relations utilise person1/person2';
        RAISE EXCEPTION 'Migration déjà appliquée, arrêt du script';
    ELSE
        RAISE EXCEPTION 'Table relations non trouvée ou structure inconnue';
    END IF;
END $$;

-- ÉTAPE 2 : Sauvegarder les données existantes
-- ============================================================================
CREATE TABLE IF NOT EXISTS relations_backup AS 
SELECT * FROM relations;

RAISE NOTICE '✅ Backup créé : relations_backup';

-- ÉTAPE 3 : Créer la nouvelle table avec le bon schéma
-- ============================================================================
CREATE TABLE relations_new (
    id SERIAL PRIMARY KEY,
    person1 TEXT NOT NULL,
    person2 TEXT NOT NULL,
    relation_type INTEGER DEFAULT 0 CHECK (relation_type >= 0 AND relation_type <= 4),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(person1, person2, relation_type)
);

RAISE NOTICE '✅ Nouvelle table créée : relations_new';

-- ÉTAPE 4 : Migrer les données (conversion ID → nom)
-- ============================================================================
INSERT INTO relations_new (id, person1, person2, relation_type, created_at)
SELECT 
    r.id,
    p1.name as person1,
    p2.name as person2,
    r.relation_type,
    r.created_at
FROM relations r
JOIN persons p1 ON r.person1_id = p1.id
JOIN persons p2 ON r.person2_id = p2.id
ON CONFLICT (person1, person2, relation_type) DO NOTHING;

-- Compter les enregistrements migrés
DO $$ 
DECLARE
    old_count INTEGER;
    new_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO old_count FROM relations;
    SELECT COUNT(*) INTO new_count FROM relations_new;
    RAISE NOTICE '✅ Migration : % relations → % dans relations_new', old_count, new_count;
    
    IF old_count != new_count THEN
        RAISE WARNING '⚠️  Attention : nombre différent (duplicates ou orphelins ignorés)';
    END IF;
END $$;

-- ÉTAPE 5 : Mettre à jour la séquence ID
-- ============================================================================
SELECT setval('relations_new_id_seq', (SELECT MAX(id) FROM relations_new));

RAISE NOTICE '✅ Séquence ID mise à jour';

-- ÉTAPE 6 : Remplacer l'ancienne table par la nouvelle
-- ============================================================================
DROP TABLE relations CASCADE;
ALTER TABLE relations_new RENAME TO relations;

RAISE NOTICE '✅ Ancienne table remplacée';

-- ÉTAPE 7 : Recréer les index pour performances
-- ============================================================================
CREATE INDEX idx_relations_person1 ON relations(person1);
CREATE INDEX idx_relations_person2 ON relations(person2);
CREATE INDEX idx_relations_type ON relations(relation_type);

RAISE NOTICE '✅ Index créés';

-- ÉTAPE 8 : Vérification finale
-- ============================================================================
DO $$ 
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count 
    FROM information_schema.columns 
    WHERE table_name = 'relations' 
    AND column_name IN ('person1', 'person2');
    
    IF col_count = 2 THEN
        RAISE NOTICE '✅ MIGRATION RÉUSSIE : Table relations utilise maintenant person1/person2 (TEXT)';
    ELSE
        RAISE EXCEPTION '❌ Migration échouée : colonnes non trouvées';
    END IF;
END $$;

-- ÉTAPE 9 : Afficher un exemple de données
-- ============================================================================
SELECT 
    'relations' as table_name,
    person1,
    person2,
    relation_type,
    created_at
FROM relations
LIMIT 5;

-- ============================================================================
-- ✅ MIGRATION TERMINÉE
-- ============================================================================
-- La table 'relations_backup' contient les anciennes données au cas où.
-- Tu peux la supprimer avec : DROP TABLE relations_backup;
-- ============================================================================
