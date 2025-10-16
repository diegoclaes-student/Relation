# 🧪 Tests Manuels app_v2 - Guide Pas à Pas

## URL: http://localhost:8052

---

## Test 1: Vérification Initiale ✅

1. Ouvrir http://localhost:8052
2. **Vérifier**:
   - [ ] Page charge sans erreur
   - [ ] Graphe s'affiche au centre
   - [ ] Panneau contrôles à droite visible
   - [ ] Header "Social Network Analyzer" + badge "V2 - Clean Architecture"

**Résultat attendu**: Interface moderne avec gradient violet/bleu

---

## Test 2: Graphe Interactif 🎨

### A. Layouts
1. Sélectionner "🎯 Community" dans Layout Algorithm
   - [ ] Graphe se réorganise (communautés groupées)
2. Sélectionner "🌸 Spring"
   - [ ] Graphe change de disposition (force-directed)
3. Sélectionner "🔷 Kamada-Kawai"
   - [ ] Disposition change à nouveau
4. Sélectionner "⭐ Spectral"
   - [ ] Disposition spectrale appliquée

**Résultat**: 4 layouts différents fonctionnent

### B. Couleurs
1. Sélectionner "🎨 By Community"
   - [ ] Nœuds colorés par communauté
2. Sélectionner "📈 By Connections"
   - [ ] Couleurs basées sur degré

**Résultat**: 2 schémas de couleur fonctionnent

### C. Interactions
1. **Zoom**: Scroller avec molette
   - [ ] Graphe zoom in/out
2. **Pan**: Cliquer-glisser sur graphe
   - [ ] Graphe se déplace
3. **Hover**: Passer souris sur nœud
   - [ ] Nom de la personne s'affiche

**Résultat**: Interactions fluides et responsives

---

## Test 3: Statistiques 📊

1. Vérifier panneau "Network Statistics"
2. Noter les valeurs actuelles:
   - Persons: ___
   - Relations: ___
   - Symmetry: devrait être "✅ 100%"

**Résultat**: Stats affichées correctement

---

## Test 4: Add Person ➕

1. Cliquer bouton "Add Person"
   - [ ] Modal s'ouvre

2. Remplir formulaire:
   - Name: "Test Alice"
   - Gender: "Female" (F)
   - Orientation: "Bisexual" (bi)

3. Cliquer "Add Person"
   - [ ] Modal se ferme
   - [ ] "Test Alice" apparaît dans graphe
   - [ ] Stats: Persons +1

4. Vérifier "Recent Actions":
   - [ ] Nouvelle entrée: "ADD_PERSON - Test Alice"

**Résultat**: Personne ajoutée et visible

---

## Test 5: Add Relation 🔗

1. Cliquer bouton "Add Relation"
   - [ ] Modal s'ouvre

2. Remplir:
   - Person 1: "Test Alice"
   - Relation Type: "Friend" (ou autre)
   - Person 2: (Sélectionner autre personne)

3. Cliquer "Add Relation"
   - [ ] Modal se ferme
   - [ ] Nouvelle arête visible dans graphe
   - [ ] Stats: Relations +1

4. **IMPORTANT - Vérifier Symétrie**:
   - Ouvrir console terminal app_v2
   - [ ] Aucune erreur asymétrie
   - [ ] Relation créée dans les 2 sens

**Résultat**: Relation ajoutée avec symétrie garantie

---

## Test 6: Edit Person ✏️

1. Cliquer bouton "Edit Person"
   - [ ] Modal s'ouvre

2. Sélectionner "Test Alice" dans dropdown
   - [ ] Champs se pré-remplissent avec données actuelles

3. Modifier:
   - Name: "Alice Modified"
   - Gender: "Non-binary" (NB)

4. Cliquer "Save Changes"
   - [ ] Modal se ferme
   - [ ] Nom updated dans graphe
   - [ ] Recent Actions updated

**Résultat**: Modification sauvegardée et visible

---

## Test 7: Merge Persons 👥

### Préparation
1. Ajouter "Bob Test" (Add Person)
2. Créer relation: Alice → Bob (Friend)

### Test Merge
1. Cliquer "Merge Persons"
   - [ ] Modal s'ouvre

2. Sélectionner:
   - Source: "Bob Test"
   - Target: "Alice Modified"

3. Vérifier preview:
   - [ ] Message "Bob Test → Alice Modified" s'affiche
   - [ ] Info relations à transférer

4. Cliquer "Merge"
   - [ ] Modal se ferme
   - [ ] "Bob Test" disparaît du graphe
   - [ ] Toutes relations de Bob transférées à Alice
   - [ ] Stats: Persons -1

**Résultat**: Fusion réussie, relations préservées

---

## Test 8: Delete Person 🗑️

### Préparation
1. Ajouter "Charlie Test"
2. Créer relation: Alice → Charlie

### Test Delete (Cascade=True)
1. Cliquer "Delete Person"
   - [ ] Modal s'ouvre

2. Sélectionner "Charlie Test"
   - [ ] Info affiche nombre de relations

3. **Vérifier checkbox "Also delete all relations" est cochée**

4. Cliquer "Delete"
   - [ ] Modal se ferme
   - [ ] "Charlie Test" disparaît
   - [ ] Ses relations disparaissent aussi
   - [ ] Stats: Persons -1, Relations -1

**Résultat**: Suppression cascade fonctionne

### Test Delete (Cascade=False)
1. Ajouter "David Test"
2. Créer relation: Alice → David
3. Delete "David Test" SANS cocher cascade
   - [ ] David supprimé
   - [ ] Relations orphelines (à vérifier si gérées)

**Résultat**: Suppression sans cascade

---

## Test 9: Historique 📝

1. Vérifier panneau "Recent Actions"
2. Effectuer plusieurs actions (add/edit/delete)
3. **Vérifier**:
   - [ ] 5 dernières actions affichées
   - [ ] Format: `timestamp: action_type - person`
   - [ ] Actions apparaissent en temps réel

**Résultat**: Historique tracked correctement

---

## Test 10: Auto-Refresh ⏱️

1. Noter stats actuelles
2. Attendre 30 secondes
3. **Vérifier**:
   - [ ] Stats se refresh automatiquement
   - [ ] Graphe se redessine
   - [ ] Historique se met à jour

**Résultat**: Auto-refresh fonctionne

---

## Test 11: Validation & Erreurs ⚠️

### A. Add Person - Nom Vide
1. Add Person sans remplir nom
2. Cliquer "Add Person"
   - [ ] Erreur affichée ou bloqué

### B. Add Relation - Self-Relation
1. Add Relation: Alice → Alice
2. Cliquer "Add Relation"
   - [ ] Erreur: "Cannot create self-relation"

### C. Merge - Same Person
1. Merge: Alice → Alice
2. **Vérifier**:
   - [ ] Preview affiche warning
   - [ ] Merge bloqué

**Résultat**: Validations protègent contre données invalides

---

## Test 12: Performance ⚡

1. Ajouter 10 personnes rapidement
2. Créer 20 relations
3. **Vérifier**:
   - [ ] Interface reste fluide
   - [ ] Graphe se redessine rapidement
   - [ ] Pas de lag perceptible

**Résultat**: Performance acceptable avec dataset moyen

---

## Test 13: Symétrie Garantie 🔐

### Vérification Automatique
1. Redémarrer app_v2: `pkill -f app_v2; python3 app_v2.py`
2. Vérifier output console:
   ```
   ✅ Symmetry: 100% guaranteed
   ```
3. Si asymétries détectées:
   ```
   ⚠️ Warning: X asymmetric relations found
   🔧 Auto-fixing...
   ✅ Fixed X asymmetries
   ```

**Résultat**: Aucune asymétrie ou auto-correction

### Vérification Manuelle DB
```bash
cd /Users/diegoclaes/Code/Relation
python3 -c "
from database.relations import relation_repository
from services.symmetry import symmetry_manager

# Check symétrie
asymmetric = symmetry_manager.audit_symmetry()
print(f'Asymétries: {len(asymmetric)}')

# Afficher relations
relations = relation_repository.read_all(deduplicate=False)
print(f'Total relations (both dirs): {len(relations)}')

unique = relation_repository.read_all(deduplicate=True)
print(f'Unique relations: {len(unique)}')
print(f'Ratio: {len(relations) / (len(unique) * 2) if unique else 0}')
"
```

**Résultat attendu**: 
- Asymétries: 0
- Ratio: 1.0 (parfaite symétrie)

---

## 📋 Checklist Globale

### Interface ✅
- [ ] Page charge
- [ ] Graphe visible
- [ ] Contrôles fonctionnent
- [ ] Modals s'ouvrent/ferment
- [ ] Stats affichées

### CRUD Personnes ✅
- [ ] Add person
- [ ] Edit person
- [ ] Merge persons
- [ ] Delete person (cascade)
- [ ] Delete person (no cascade)

### Relations ✅
- [ ] Add relation
- [ ] Symétrie garantie (2 directions)
- [ ] Edit relation ⏸️ (non implémenté)
- [ ] Delete relation ⏸️ (non implémenté)

### Graphe ✅
- [ ] 4 layouts fonctionnent
- [ ] 2 color schemes
- [ ] Zoom/Pan
- [ ] Hover noms

### Qualité ✅
- [ ] Pas d'erreurs console
- [ ] Historique tracked
- [ ] Validations actives
- [ ] Performance acceptable
- [ ] Symétrie 100%

---

## 🐛 Bugs à Reporter

Si vous trouvez des bugs, noter:
1. **Action effectuée**: (ex: "Clicked Add Person")
2. **Résultat attendu**: (ex: "Modal opens")
3. **Résultat observé**: (ex: "Error in console")
4. **Erreur console**: (copier message)
5. **Screenshot**: (si possible)

**Format**:
```
BUG #1: Modal ne se ferme pas après add person
- Action: Add Person > Fill form > Submit
- Attendu: Modal closes
- Observé: Modal stays open
- Console: [copier erreur]
```

---

## ✅ Tests Réussis → Prochaines Étapes

Si tous les tests passent:
1. ✅ app_v2 est validée fonctionnellement
2. 🔜 Implémenter Edit/Delete Relations
3. 🔜 Tests performance (100+ personnes)
4. 🔜 Migration production (app_v2 → app)

**Temps estimé tests manuels**: 20-30 minutes

---

**🚀 Bonne chance ! L'app est stable et prête pour validation !**
