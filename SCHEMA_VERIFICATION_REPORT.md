# 🔍 RAPPORT DE VÉRIFICATION DU SCHÉMA POSTGRESQL

**Date**: 9 novembre 2025  
**Objectif**: Vérifier que le schéma PostgreSQL correspond exactement aux besoins du code

---

## ⚠️ PROBLÈME CRITIQUE IDENTIFIÉ

Le fichier `supabase_schema.sql` (ancien schéma) est **INCOMPATIBLE** avec le code Python actuel.

### 🔴 Incompatibilité #1 : Table `relations`

**Ancien schéma (supabase_schema.sql)** ❌
```sql
CREATE TABLE relations (
    person1_id INTEGER NOT NULL REFERENCES persons(id),  -- IDs
    person2_id INTEGER NOT NULL REFERENCES persons(id),  -- IDs
    ...
);
```

**Code Python actuel** ✅
```python
cursor.execute("""
    SELECT person1, person2, relation_type FROM relations
    WHERE person1 = %s
""", (person_name,))  -- Le code utilise des NOMS (TEXT), pas des IDs
```

**Impact**: Toutes les requêtes sur les relations vont échouer car les colonnes n'existent pas.

---

### 🔴 Incompatibilité #2 : Table `pending_persons`

**Ancien schéma (supabase_schema.sql)** ❌
```sql
CREATE TABLE pending_persons (
    person_name TEXT NOT NULL,  -- Colonne nommée 'person_name'
    ...
);
```

**Code Python actuel** (AVANT CORRECTION)
```python
cur.execute("""
    SELECT id, name, submitted_by, submitted_at, status
    FROM pending_persons  -- Le code utilisait 'name', pas 'person_name'
""")
```

**Status**: ✅ **CORRIGÉ** dans le commit 6c93907 - le code détecte maintenant automatiquement le nom de colonne.

---

## ✅ SOLUTION : Nouveau schéma compatible

Le fichier `postgres_schema_compatible.sql` contient le schéma **CORRECT** qui correspond au code.

### Table `relations` (CORRIGÉE)
```sql
CREATE TABLE relations (
    id SERIAL PRIMARY KEY,
    person1 TEXT NOT NULL,        -- ✅ TEXT (noms)
    person2 TEXT NOT NULL,        -- ✅ TEXT (noms)
    relation_type INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(person1, person2, relation_type)
);
```

### Table `pending_persons` (CORRIGÉE)
```sql
CREATE TABLE pending_persons (
    id SERIAL PRIMARY KEY,
    person_name TEXT NOT NULL,    -- ✅ Nom explicite pour éviter confusion
    submitted_by TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending'
);
```

---

## 📋 CHECKLIST DE VÉRIFICATION PAR FONCTIONNALITÉ

### 1. ✅ Gestion des personnes (`database/persons.py`)

**Tables utilisées**: `persons`

**Colonnes utilisées**:
- ✅ `id` (SERIAL PRIMARY KEY)
- ✅ `name` (TEXT UNIQUE NOT NULL)
- ✅ `gender` (TEXT) - optionnel
- ✅ `sexual_orientation` (TEXT) - optionnel
- ✅ `created_at` (TIMESTAMP)
- ✅ `updated_at` (TIMESTAMP)

**Requêtes SQL vérifiées**:
- ✅ `SELECT id FROM persons WHERE name = %s`
- ✅ `SELECT * FROM persons WHERE id = %s`
- ✅ `SELECT * FROM persons ORDER BY name`
- ✅ `INSERT INTO persons (name) VALUES (%s)`
- ✅ `UPDATE persons SET name = %s WHERE id = %s`
- ✅ `DELETE FROM persons WHERE id = %s`

**Verdict**: ✅ **COMPATIBLE**

---

### 2. ⚠️ Gestion des relations (`database/relations.py`)

**Tables utilisées**: `relations`

**Colonnes REQUISES**:
- ✅ `id` (SERIAL PRIMARY KEY)
- ✅ `person1` (TEXT NOT NULL) ⚠️ ÉTAIT person1_id dans ancien schéma
- ✅ `person2` (TEXT NOT NULL) ⚠️ ÉTAIT person2_id dans ancien schéma
- ✅ `relation_type` (INTEGER)
- ✅ `created_at` (TIMESTAMP)

**Requêtes SQL vérifiées**:
- ✅ `SELECT person1, person2, relation_type FROM relations`
- ✅ `SELECT person2, relation_type FROM relations WHERE person1 = %s`
- ✅ `INSERT INTO relations (person1, person2, relation_type) VALUES (%s, %s, %s)`
- ✅ `UPDATE relations SET relation_type = %s WHERE person1 = %s AND person2 = %s`
- ✅ `DELETE FROM relations WHERE person1 = %s AND person2 = %s`

**Verdict**: ✅ **CORRIGÉ** dans `postgres_schema_compatible.sql`

---

### 3. ✅ Authentification (`database/users.py`)

**Tables utilisées**: `users`, `pending_accounts`

**Colonnes `users`**:
- ✅ `id` (SERIAL PRIMARY KEY)
- ✅ `username` (TEXT UNIQUE NOT NULL)
- ✅ `password_hash` (TEXT NOT NULL)
- ✅ `role` (TEXT DEFAULT 'user')
- ✅ `created_at` (TIMESTAMP)

**Colonnes `pending_accounts`**:
- ✅ `id` (SERIAL PRIMARY KEY)
- ✅ `username` (TEXT UNIQUE NOT NULL)
- ✅ `password_hash` (TEXT NOT NULL)
- ✅ `submitted_at` (TIMESTAMP)
- ✅ `status` (TEXT DEFAULT 'pending')

**Requêtes SQL vérifiées**:
- ✅ `SELECT id, username, password_hash, role FROM users WHERE username = %s`
- ✅ `INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)`
- ✅ `SELECT id, username, submitted_at FROM pending_accounts WHERE status = 'pending'`
- ✅ `INSERT INTO pending_accounts (username, password_hash) VALUES (%s, %s)`
- ✅ `UPDATE pending_accounts SET status = 'approved' WHERE id = %s`

**Verdict**: ✅ **COMPATIBLE**

---

### 4. ✅ Soumissions en attente (`database/pending_submissions.py`)

**Tables utilisées**: `pending_persons`, `pending_relations`

**Colonnes `pending_persons`**:
- ✅ `id` (SERIAL PRIMARY KEY)
- ✅ `person_name` (TEXT NOT NULL) ⚠️ Code adapté pour utiliser person_name
- ✅ `submitted_by` (TEXT NOT NULL)
- ✅ `submitted_at` (TIMESTAMP)
- ✅ `status` (TEXT DEFAULT 'pending')

**Colonnes `pending_relations`**:
- ✅ `id` (SERIAL PRIMARY KEY)
- ✅ `person1` (TEXT NOT NULL)
- ✅ `person2` (TEXT NOT NULL)
- ✅ `relation_type` (INTEGER NOT NULL)
- ✅ `submitted_by` (TEXT NOT NULL)
- ✅ `submitted_at` (TIMESTAMP)
- ✅ `status` (TEXT DEFAULT 'pending')

**Requêtes SQL vérifiées**:
- ✅ `SELECT id, person_name, submitted_by, submitted_at, status FROM pending_persons`
- ✅ `INSERT INTO pending_persons (person_name, submitted_by, submitted_at, status) VALUES (...)`
- ✅ `UPDATE pending_persons SET status = 'approved' WHERE id = %s`
- ✅ `SELECT person1, person2, relation_type FROM pending_relations WHERE status = 'pending'`
- ✅ `INSERT INTO pending_relations (person1, person2, relation_type, submitted_by, ...) VALUES (...)`

**Verdict**: ✅ **CORRIGÉ** dans commit 6c93907 + nouveau schéma

---

### 5. ✅ Historique (`services/history.py`)

**Tables utilisées**: `history`

**Colonnes REQUISES**:
- ✅ `id` (SERIAL PRIMARY KEY)
- ✅ `action_type` (TEXT NOT NULL)
- ✅ `person1` (TEXT)
- ✅ `person2` (TEXT)
- ✅ `relation_type` (INTEGER)
- ✅ `performed_by` (TEXT DEFAULT 'system')
- ✅ `details` (TEXT)
- ✅ `created_at` (TIMESTAMP)

**Requêtes SQL vérifiées**:
- ✅ `INSERT INTO history (action_type, person1, person2, relation_type, performed_by, details) VALUES (...)`
- ✅ `SELECT * FROM history ORDER BY created_at DESC LIMIT 100`

**Verdict**: ✅ **COMPATIBLE** (table déjà présente dans nouveau schéma)

---

## 🎯 RÉSUMÉ DES ACTIONS REQUISES

### ✅ Actions DÉJÀ RÉALISÉES
1. ✅ Correction du code pour détecter `person_name` vs `name` (commit 6c93907)
2. ✅ Création du schéma compatible (`postgres_schema_compatible.sql`)

### 🔄 Actions À FAIRE MAINTENANT

#### Option A : Recréer les tables (SI PAS DE DONNÉES EN PRODUCTION)
```sql
-- Dans le dashboard Render PostgreSQL :

-- 1. Supprimer l'ancienne table relations (ATTENTION : perte de données)
DROP TABLE IF EXISTS relations CASCADE;

-- 2. Recréer avec le bon schéma
CREATE TABLE relations (
    id SERIAL PRIMARY KEY,
    person1 TEXT NOT NULL,
    person2 TEXT NOT NULL,
    relation_type INTEGER DEFAULT 0 CHECK (relation_type >= 0 AND relation_type <= 4),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(person1, person2, relation_type)
);

-- 3. Recréer les index
CREATE INDEX idx_relations_person1 ON relations(person1);
CREATE INDEX idx_relations_person2 ON relations(person2);
CREATE INDEX idx_relations_type ON relations(relation_type);
```

#### Option B : Migrer les données (SI DONNÉES EN PRODUCTION)
```sql
-- 1. Créer la nouvelle table avec le bon schéma
CREATE TABLE relations_new (
    id SERIAL PRIMARY KEY,
    person1 TEXT NOT NULL,
    person2 TEXT NOT NULL,
    relation_type INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(person1, person2, relation_type)
);

-- 2. Migrer les données (conversion ID → nom)
INSERT INTO relations_new (person1, person2, relation_type, created_at)
SELECT 
    p1.name as person1,
    p2.name as person2,
    r.relation_type,
    r.created_at
FROM relations r
JOIN persons p1 ON r.person1_id = p1.id
JOIN persons p2 ON r.person2_id = p2.id;

-- 3. Renommer les tables
DROP TABLE relations;
ALTER TABLE relations_new RENAME TO relations;

-- 4. Recréer les index
CREATE INDEX idx_relations_person1 ON relations(person1);
CREATE INDEX idx_relations_person2 ON relations(person2);
CREATE INDEX idx_relations_type ON relations(relation_type);
```

#### Option C : Exécuter le script complet (RECOMMANDÉ)
```bash
# Dans le dashboard Render PostgreSQL, exécute :
postgres_schema_compatible.sql
```

---

## 🚨 VÉRIFICATION POST-DÉPLOIEMENT

Après avoir appliqué le nouveau schéma, vérifie que :

### Test 1 : Structure des tables
```sql
-- Vérifie la structure de la table relations
\d relations

-- Doit afficher :
-- person1 | text | not null
-- person2 | text | not null
-- (PAS person1_id ni person2_id)
```

### Test 2 : Insertion de test
```sql
-- Insère une personne de test
INSERT INTO persons (name) VALUES ('Test Person') ON CONFLICT (name) DO NOTHING;

-- Insère une relation de test
INSERT INTO relations (person1, person2, relation_type) 
VALUES ('Test Person', 'Test Person 2', 0);

-- Vérifie
SELECT * FROM relations WHERE person1 = 'Test Person';
```

### Test 3 : Application web
1. ✅ Crée une nouvelle personne via l'interface
2. ✅ Crée une relation entre deux personnes
3. ✅ Visualise le graphe de relations
4. ✅ Va dans le panneau admin
5. ✅ Vérifie les soumissions en attente

---

## 📊 ÉTAT FINAL

| Fonctionnalité | Table(s) | Status | Commentaire |
|---|---|---|---|
| Gestion personnes | `persons` | ✅ OK | Compatible |
| Gestion relations | `relations` | ⚠️ NÉCESSITE MIGRATION | Utilise TEXT, pas INTEGER IDs |
| Authentification | `users` | ✅ OK | Compatible |
| Comptes en attente | `pending_accounts` | ✅ OK | Compatible |
| Personnes en attente | `pending_persons` | ✅ CORRIGÉ | Code adapté pour person_name |
| Relations en attente | `pending_relations` | ✅ OK | Compatible |
| Historique | `history` | ✅ OK | Compatible |

---

## 🎓 POURQUOI CETTE ARCHITECTURE ?

Le code actuel utilise les **NOMS des personnes** (TEXT) dans la table `relations` plutôt que des IDs pour plusieurs raisons :

### Avantages ✅
1. **Simplicité** : Pas besoin de jointures pour afficher les relations
2. **Lisibilité** : Les données sont directement compréhensibles
3. **Performance lecture** : Requêtes plus rapides (pas de JOIN)
4. **Compatibilité CSV** : Import/export facilité

### Inconvénients ⚠️
1. **Redondance** : Le nom est dupliqué dans relations
2. **Mises à jour** : Si on renomme une personne, faut mettre à jour relations
3. **Intégrité** : Pas de foreign key pour garantir l'existence

Pour ce projet (réseau social de gossip), les avantages l'emportent sur les inconvénients.

---

## ✅ CONCLUSION

Le nouveau schéma `postgres_schema_compatible.sql` résout tous les problèmes d'incompatibilité.

**Action immédiate** : Exécute ce schéma sur ton instance PostgreSQL Render pour garantir la compatibilité totale.
