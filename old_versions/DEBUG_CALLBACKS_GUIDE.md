# 🔍 Debug Guide - app_v2 Callbacks

## Problème: Callbacks ne se déclenchent pas

### ✅ Diagnostic Effectué
- 17 callbacks enregistrés
- Tous les IDs existent et correspondent
- Aucun orphelin détecté
- App démarre sans erreur

### 🧪 Tests à Effectuer

#### 1. Rafraîchir la Page
```
Ctrl+R (Windows/Linux) ou Cmd+R (Mac)
```

#### 2. Vider Cache Navigateur
```
Ctrl+Shift+R (Windows/Linux) ou Cmd+Shift+R (Mac)
```

#### 3. Console Navigateur
1. Ouvrir DevTools: F12
2. Onglet "Console"
3. Chercher erreurs rouges
4. Noter les messages

#### 4. Network Tab
1. DevTools → Network
2. Effectuer action (ex: Add Relation)
3. Chercher requête `/_dash-update-component`
4. Vérifier Status: 200 OK ou erreur?
5. Regarder Response

### 🐛 Problèmes Possibles

#### A. Modal ne s'ouvre pas
**Cause**: Callback toggle modal pas déclenché

**Debug**:
```python
# Dans app_v2.py, ajouter print dans callback
@app.callback(...)
def toggle_add_relation_modal(...):
    print(f"🔍 Modal toggle called: triggered_id={ctx.triggered_id}")
    ...
```

#### B. Modal s'ouvre mais submit ne fait rien
**Cause**: Callback submit pas déclenché ou données invalides

**Debug**:
```python
@app.callback(...)
def submit_add_relation(...):
    print(f"🔍 Submit called: p1={p1_id}, p2={p2_id}, type={rel_type}")
    ...
```

#### C. Dropdowns vides
**Cause**: Options pas chargées

**Vérification**:
- GENDERS dict correct?
- SEXUAL_ORIENTATIONS dict correct?
- RELATION_TYPES dict correct?

#### D. Données pas sauvegardées
**Cause**: Repository failed

**Debug**:
```python
success, message = relation_repository.create(...)
print(f"🔍 Create result: success={success}, message={message}")
```

### 🔧 Quick Fixes

#### Fix 1: Redémarrer app_v2
```bash
pkill -f "python.*app_v2.py"
cd /Users/diegoclaes/Code/Relation
python3 app_v2.py
```

#### Fix 2: Vérifier logs temps réel
```bash
# Terminal 1: Lancer app
cd /Users/diegoclaes/Code/Relation
python3 app_v2.py

# Terminal 2: Surveiller logs
tail -f nohup.out  # Si lancé en background
```

#### Fix 3: Test minimal
```python
# Tester PersonRepository directement
from database.persons import person_repository

# Create
success, msg = person_repository.create("Test Direct", "M", "hetero")
print(f"Create: {success} - {msg}")

# Read all
persons = person_repository.read_all()
print(f"Persons: {len(persons)}")
```

### 📊 Logs Attendus

#### Add Relation Success
```
127.0.0.1 - - [16/Oct/2025 15:50:00] "POST /_dash-update-component HTTP/1.1" 200 -
```

#### Add Relation Error
```
[2025-10-16 15:50:00,000] ERROR in app: Exception on /_dash-update-component [POST]
Traceback (most recent call last):
  ...
```

### ✅ Tests Manuel Rapides

#### Test 1: Add Person (fonctionne déjà)
```
1. Click "Add Person"
2. Fill: "Test Rapide", "M", "hetero"
3. Submit
4. ✅ Modal close + graphe update
```

#### Test 2: Add Relation
```
1. Click "Add Relation"
2. Modal s'ouvre? ✅/❌
3. Dropdowns chargés? ✅/❌
4. Select P1, Type, P2
5. Submit
6. Modal close? ✅/❌
7. Graphe update? ✅/❌
```

#### Test 3: Edit Person
```
1. Click "Edit Person"
2. Modal s'ouvre? ✅/❌
3. Dropdown personnes chargé? ✅/❌
4. Select personne
5. Champs pré-remplis? ✅/❌
6. Modify + Submit
7. Update visible? ✅/❌
```

### 🎯 Si Tout Échoue

#### Option 1: Tester avec app_full.py
```bash
# Pour comparer comportement
python3 app_full.py  # Port 8051
```

#### Option 2: Callback Debugging Version
Créer `app_v2_debug.py` avec prints partout:
```python
@app.callback(...)
def callback_name(...):
    print(f"🔍 CALLED: {ctx.triggered_id}")
    print(f"   Args: {args}")
    try:
        result = do_something()
        print(f"   ✅ Success: {result}")
        return result
    except Exception as e:
        print(f"   ❌ Error: {e}")
        raise
```

#### Option 3: Mode Debug Dash
```python
# Dans app_v2.py, ligne finale
if __name__ == '__main__':
    ...
    app.run(host='0.0.0.0', port=8052, debug=True)  # debug=True
```

### 📝 Rapport Bug Template

Si problème persiste:
```
SYMPTÔME:
- Action: [Click "Add Relation"]
- Attendu: [Modal opens, form filled, submit, modal closes]
- Observé: [Modal opens, submit → nothing happens]

CONSOLE BROWSER:
[Copier erreurs JavaScript]

CONSOLE APP:
[Copier logs Python]

NETWORK TAB:
- Request: POST /_dash-update-component
- Status: [200/500/etc]
- Response: [copier payload]

TESTS EFFECTUÉS:
- [ ] Refresh page
- [ ] Clear cache
- [ ] Check console
- [ ] Test autre callback
- [ ] Restart app
```

---

**💡 Note**: Si "Add Person" fonctionne mais "Add Relation" ne fonctionne pas, c'est probablement:
1. Dropdowns relations vides (persons pas chargés)
2. Validation échoue (p1=p2 ou type invalide)
3. relation_repository.create() échoue

Vérifier console pour voir quelle étape bloque !
