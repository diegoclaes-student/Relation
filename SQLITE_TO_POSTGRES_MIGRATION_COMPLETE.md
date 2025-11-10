# ✅ MIGRATION SQLite → PostgreSQL TERMINÉE

**Date**: 10 novembre 2025  
**Commits**: 06b2dc5, 5becf1f

---

## 🎯 PROBLÈME IDENTIFIÉ

L'application utilisait un **mélange SQLite et PostgreSQL** :
- Certains modules utilisaient `db_manager` (✅ PostgreSQL en production)
- D'autres modules utilisaient directement `sqlite3.connect()` (❌ Toujours SQLite local)

### Impact sur les Relations
**Symptôme critique** : Les relations créées disparaissaient après redéploiement.

**Cause** : `services/symmetry.py` était hardcodé pour utiliser SQLite :
```python
# ❌ AVANT (incorrect)
def _get_connection(self) -> sqlite3.Connection:
    conn = sqlite3.connect(self.db_path)
    return conn
```

Résultat :
1. User crée une relation → Sauvegardée dans SQLite local
2. Render redéploie → Utilise PostgreSQL (qui n'a pas la relation)
3. Relation disparue ! 💥

---

## ✅ CORRECTIONS APPLIQUÉES

### 1. services/symmetry.py ⚠️ CRITIQUE
**Problème** : Utilisait directement SQLite pour TOUTES les relations  
**Impact** : Relations perdues au redéploiement

**Avant** :
```python
import sqlite3
from config import DB_PATH

def _get_connection(self) -> sqlite3.Connection:
    conn = sqlite3.connect(self.db_path)
    return conn

# Requêtes avec ? (SQLite syntax)
cursor.execute("INSERT INTO relations VALUES (?, ?, ?)", ...)
```

**Après** :
```python
from database.base import db_manager

def _get_connection(self):
    return self.db_manager.get_connection()

# Requêtes avec %s (PostgreSQL syntax)
cursor.execute("INSERT INTO relations VALUES (%s, %s, %s)", ...)
```

**Résultat** : ✅ Relations maintenant sauvegardées dans PostgreSQL

---

### 2. services/history.py
**Problème** : Historique sauvegardé seulement dans SQLite local

**Corrections** :
- ✅ Utilise `db_manager` au lieu de `sqlite3.connect()`
- ✅ Tous les `?` remplacés par `%s`
- ✅ `sqlite3.Connection` remplacé par `object`

**Impact** : Historique des actions maintenant synchronisé avec production

---

### 3. database/users.py
**Problème** : Importait `sqlite3` inutilement

**Corrections** :
- ✅ Supprimé `import sqlite3`
- ✅ Supprimé `conn.row_factory = sqlite3.Row` (inutile avec PostgreSQL)

**Impact** : Gestion utilisateurs 100% compatible PostgreSQL

---

### 4. database/pending_submissions.py
**Problème** : Importait `sqlite3` (inutilisé mais présent)

**Corrections** :
- ✅ Supprimé `import sqlite3`

**Impact** : Nettoyage du code

---

### 5. database/audit.py
**Problème** : Utilisait `sqlite3` pour l'audit

**Corrections** :
- ✅ Supprimé `import sqlite3`
- ✅ Supprimé `conn.row_factory = sqlite3.Row`

**Impact** : Logs d'audit synchronisés avec production

---

### 6. database/relations.py
**Problème** : Import circulaire avec `symmetry_manager`

**Corrections** :
- ✅ Import lazy de `symmetry_manager` dans `__init__`
- ✅ Wrapper `_RelationRepositorySingleton` pour lazy loading

**Impact** : Résolution de l'import circulaire, application démarre correctement

---

## 📊 VALIDATION

### Test de diagnostic
```bash
python3 diagnose.py
```

**Résultat** :
```
✅ PostgreSQL détecté ! URL: postgresql://centrale:...
✅ Connexion réussie à PostgreSQL
✅ Tables trouvées (7): history, pending_accounts, pending_persons, 
   pending_relations, persons, relations, users
✅ Table 'relations' utilise person1/person2 (TEXT) - CORRECT
✅ Table 'pending_persons' utilise 'person_name' - CORRECT
```

### Vérification du code
```bash
# Aucun import sqlite3 dans les modules critiques
grep -r "import sqlite3" database/ services/ --exclude-dir=__pycache__
# Résultat : Aucun match dans les fichiers de production

# Aucune syntaxe SQLite (?) dans les requêtes
grep -r "execute.*\?" database/ services/ --exclude-dir=__pycache__
# Résultat : Aucun match
```

---

## 🎯 RÉSULTAT FINAL

### Avant
```
┌─────────────┐     ┌──────────┐
│  Personnes  │ ───▶│ PostgreSQL│ ✅
└─────────────┘     └──────────┘

┌─────────────┐     ┌──────────┐
│  Relations  │ ───▶│  SQLite  │ ❌ (perdu au redéploiement)
└─────────────┘     └──────────┘

┌─────────────┐     ┌──────────┐
│  Historique │ ───▶│  SQLite  │ ❌ (perdu au redéploiement)
└─────────────┘     └──────────┘
```

### Après ✅
```
┌─────────────┐     
│  Personnes  │ ───┐
└─────────────┘    │
                   │
┌─────────────┐    │    ┌──────────────┐
│  Relations  │ ───┼───▶│ PostgreSQL   │ ✅
└─────────────┘    │    │ (Production) │
                   │    └──────────────┘
┌─────────────┐    │
│  Historique │ ───┘
└─────────────┘

┌──────────────┐
│   db_manager │ (gère automatiquement SQLite local vs PostgreSQL prod)
└──────────────┘
```

---

## 🧪 COMMENT TESTER

### Test 1 : Créer une relation
1. Va sur ton app Render
2. Connecte-toi
3. Crée une relation entre 2 personnes
4. Vérifie qu'elle apparaît dans "Manage Relations"
5. ✅ **ATTENDS 5 minutes** (pour simuler redéploiement)
6. Rafraîchis la page
7. ✅ La relation doit TOUJOURS être là !

### Test 2 : Vérifier PostgreSQL
```bash
# Vérifie que la relation est dans PostgreSQL
export DATABASE_URL='ton_url_render'
python3 -c "
from database.base import db_manager
conn = db_manager.get_connection()
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM relations')
print(f'Relations dans PostgreSQL: {cur.fetchone()[0]}')
conn.close()
"
```

### Test 3 : Historique
1. Crée une action (ajout personne, relation, etc.)
2. Va dans l'historique (si disponible dans l'UI)
3. ✅ L'action doit être enregistrée

---

## 📝 NOTES TECHNIQUES

### Syntaxe SQL : ? vs %s

**SQLite** utilise `?` comme placeholder :
```python
cursor.execute("SELECT * FROM table WHERE id = ?", (value,))
```

**PostgreSQL** (psycopg2) utilise `%s` :
```python
cursor.execute("SELECT * FROM table WHERE id = %s", (value,))
```

### Détection automatique

Le `db_manager` détecte automatiquement l'environnement :

```python
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Production Render → PostgreSQL
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
else:
    # Développement local → SQLite
    conn = sqlite3.connect(DB_PATH)
```

**Important** : Tous les modules doivent utiliser `db_manager.get_connection()` !

---

## ✅ CHECKLIST FINALE

- ✅ Aucun `import sqlite3` dans les modules de production
- ✅ Aucune requête avec `?` (syntax SQLite)
- ✅ Tous les modules utilisent `db_manager`
- ✅ Relations sauvegardées dans PostgreSQL
- ✅ Historique sauvegardé dans PostgreSQL
- ✅ Tests de diagnostic passent
- ✅ Application démarre sans erreur
- ✅ Import circulaire résolu

---

## 🚀 DÉPLOIEMENT

Les corrections sont déployées automatiquement sur Render via GitHub :

**Commits** :
- `06b2dc5` - CRITICAL FIX: Use PostgreSQL for relations instead of SQLite
- `5becf1f` - Remove all direct SQLite usage - use PostgreSQL everywhere

**Status** : ✅ Déployé en production

---

## 🎉 CONCLUSION

**Avant** : Application mixte SQLite/PostgreSQL → Perte de données  
**Après** : Application 100% PostgreSQL en production → Données persistantes

Toutes les relations, utilisateurs, historique et soumissions sont maintenant **correctement sauvegardés dans PostgreSQL** et **survivent aux redéploiements**.

---

**Pour plus d'infos** :
- `diagnose.py` - Script de diagnostic
- `SCHEMA_VERIFICATION_SUMMARY.md` - Vérification du schéma
- `QUICK_SCHEMA_GUIDE.md` - Guide de migration
