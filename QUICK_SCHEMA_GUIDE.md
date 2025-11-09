# 🚀 GUIDE RAPIDE : Vérifier et Corriger le Schéma PostgreSQL

## 🎯 Objectif
S'assurer que la base de données Render PostgreSQL a le bon schéma pour que toutes les fonctionnalités marchent.

---

## ⚡ MÉTHODE RAPIDE (5 minutes)

### Étape 1 : Vérifier le schéma actuel

1. Va sur ton **dashboard Render** : https://dashboard.render.com
2. Clique sur ton service **PostgreSQL**
3. Clique sur l'onglet **"Connect"**
4. Note la commande de connexion (quelque chose comme `psql postgres://...`)
5. Dans ton terminal local :

```bash
# Exporte l'URL de la base de données (copie depuis Render dashboard)
export DATABASE_URL='postgresql://...'

# Vérifie le schéma actuel
python3 check_render_schema.py
```

### Étape 2 : Interpréter les résultats

Le script va te dire :

#### ✅ Si tu vois : "relations uses TEXT columns (person1, person2) - CORRECT"
→ **Tout est bon !** Aucune action nécessaire.

#### ❌ Si tu vois : "relations uses INTEGER columns (person1_id, person2_id) - INCOMPATIBLE"
→ **Tu dois migrer la table** (voir Étape 3)

#### ⚠️ Si la table n'existe pas
→ **Tu dois créer le schéma complet** (voir Étape 4)

---

### Étape 3 : MIGRATION (si nécessaire) ⚠️

**ATTENTION** : Cette opération modifie la base de données. Fais une sauvegarde d'abord !

#### Option A : Via Dashboard Render (RECOMMANDÉ)

1. Va sur **Render Dashboard** → Ton PostgreSQL
2. Clique sur **"Shell"** ou **"Connect"**
3. Connecte-toi avec `psql`
4. Copie-colle le contenu de `migrate_relations_to_text.sql`
5. Exécute et attends la confirmation ✅

#### Option B : Via Terminal Local

```bash
# Récupère l'URL de connexion depuis Render
export DATABASE_URL='postgresql://...'

# Exécute le script de migration
psql $DATABASE_URL < migrate_relations_to_text.sql
```

---

### Étape 4 : CRÉATION COMPLÈTE (si base vide)

Si la base est complètement vide ou si les tables n'existent pas :

```bash
# Via Dashboard Render → Shell → psql, exécute :
psql $DATABASE_URL < postgres_schema_compatible.sql
```

Ou copie-colle le contenu du fichier `postgres_schema_compatible.sql` dans l'éditeur SQL du dashboard.

---

## 🔍 VÉRIFICATIONS POST-MIGRATION

### Test 1 : Structure de la table

```sql
-- Dans psql :
\d relations

-- Tu dois voir :
-- person1      | text      | not null
-- person2      | text      | not null
-- (PAS person1_id ni person2_id)
```

### Test 2 : Comptage des tables

```sql
SELECT 
    'persons' as table_name, COUNT(*) as count FROM persons
UNION ALL
SELECT 
    'relations', COUNT(*) FROM relations
UNION ALL
SELECT 
    'users', COUNT(*) FROM users
UNION ALL
SELECT 
    'pending_persons', COUNT(*) FROM pending_persons
UNION ALL
SELECT 
    'pending_relations', COUNT(*) FROM pending_relations;
```

Tu dois voir toutes les tables avec leurs comptages.

### Test 3 : Application Web

1. Va sur ton app Render : `https://ton-app.onrender.com`
2. ✅ Connecte-toi avec ton compte admin
3. ✅ Va dans le panneau admin
4. ✅ Vérifie que les inscriptions en attente s'affichent (pas d'erreur "column name does not exist")
5. ✅ Crée une personne de test
6. ✅ Crée une relation de test
7. ✅ Visualise le graphe

Si tout fonctionne → ✅ **SUCCÈS !**

---

## 📋 CHECKLIST COMPLÈTE

### Tables Requises
- ✅ `persons` (id, name, gender, sexual_orientation, created_at, updated_at)
- ✅ `relations` (id, **person1**, **person2**, relation_type, created_at) ← TEXT, pas IDs !
- ✅ `users` (id, username, password_hash, role, created_at)
- ✅ `pending_accounts` (id, username, password_hash, submitted_at, status)
- ✅ `pending_persons` (id, **person_name**, submitted_by, submitted_at, status)
- ✅ `pending_relations` (id, person1, person2, relation_type, submitted_by, submitted_at, status)
- ✅ `history` (id, action_type, person1, person2, relation_type, performed_by, details, created_at)

### Index Requis pour Performance
```sql
-- Sur persons
CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name);

-- Sur relations
CREATE INDEX IF NOT EXISTS idx_relations_person1 ON relations(person1);
CREATE INDEX IF NOT EXISTS idx_relations_person2 ON relations(person2);
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(relation_type);

-- Sur users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Sur pending_*
CREATE INDEX IF NOT EXISTS idx_pending_accounts_status ON pending_accounts(status);
CREATE INDEX IF NOT EXISTS idx_pending_persons_status ON pending_persons(status);
CREATE INDEX IF NOT EXISTS idx_pending_relations_status ON pending_relations(status);
```

---

## 🚨 PROBLÈMES COURANTS

### Problème 1 : "column name does not exist"
**Cause** : La table `pending_persons` utilise `name` au lieu de `person_name`  
**Solution** : Migration déjà faite dans le code (commit 6c93907), juste redéployer

### Problème 2 : "column person1 does not exist" 
**Cause** : La table `relations` utilise `person1_id` au lieu de `person1`  
**Solution** : Exécuter `migrate_relations_to_text.sql`

### Problème 3 : Render redéploie mais l'erreur persiste
**Cause** : Le schéma de la DB n'a pas été mis à jour  
**Solution** : Connecte-toi à la DB et applique le schéma manuellement

### Problème 4 : "table does not exist"
**Cause** : Les tables n'ont jamais été créées  
**Solution** : Exécuter `postgres_schema_compatible.sql` complet

---

## 🎓 COMPRENDRE L'ARCHITECTURE

### Pourquoi person1/person2 en TEXT au lieu d'IDs ?

**Architecture actuelle** (simplifiée) :
```
relations
├── person1: "Alice" (TEXT)
├── person2: "Bob" (TEXT)
└── relation_type: 3
```

**Avantages** :
- ✅ Pas de JOIN nécessaire pour afficher
- ✅ Données lisibles directement
- ✅ Compatible avec import/export CSV
- ✅ Code plus simple

**Alternative** (normalisée) :
```
relations
├── person1_id: 1 (INTEGER → persons.id)
├── person2_id: 2 (INTEGER → persons.id)
└── relation_type: 3

Nécessite JOIN pour afficher les noms
```

Pour ton projet, l'approche TEXT est plus adaptée car :
1. Les noms ne changent pas souvent
2. Performance lecture > écriture
3. Simplicité du code

---

## ✅ VALIDATION FINALE

Après avoir tout configuré, cette commande devrait réussir sans erreur :

```bash
export DATABASE_URL='postgresql://...'
python3 check_render_schema.py
```

**Output attendu** :
```
✅ Table 'relations' uses TEXT columns (person1, person2) - CORRECT
✅ Table 'pending_persons' uses 'person_name' column - CORRECT (code adapted)
```

---

## 📞 AIDE

Si tu rencontres des problèmes :

1. **Vérifie les logs Render** : Dashboard → Ton Service → Logs
2. **Teste en local** : Utilise SQLite pour vérifier que le code fonctionne
3. **Sauvegarde d'abord** : Toujours faire un backup avant migration
4. **Contacte moi** avec l'output de `check_render_schema.py`

---

**Dernière mise à jour** : 9 novembre 2025  
**Commit associé** : 6c93907 (fix pending_persons)
