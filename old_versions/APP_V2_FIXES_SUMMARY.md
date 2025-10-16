# 🔧 App V2 - Corrections Apportées

## Problèmes Résolus

### ✅ 1. Relations Affichées 2 Fois (A→B et B→A)
**Problème**: Le graphe montrait les relations dans les deux sens
**Cause**: `relation_repository.read_all(deduplicate=False)`
**Solution**: Changé en `deduplicate=True`

```python
# Avant
relations = relation_repository.read_all(deduplicate=False)

# Après  
relations = relation_repository.read_all(deduplicate=True)
```

### ✅ 2. Add Relation - IDs vs Noms
**Problème**: `AttributeError: 'int' object has no attribute 'strip'`
**Cause**: Les dropdowns retournent des IDs (int) mais `RelationRepository.create()` attend des noms (str)
**Solution**: Convertir IDs en noms avant l'appel

```python
# Récupérer les noms à partir des IDs
p1 = person_repository.read(p1_id)
p2 = person_repository.read(p2_id)

relation_repository.create(
    person1=p1['name'],  # Nom, pas ID
    person2=p2['name'],
    relation_type=rel_type
)
```

### ✅ 3. Modal Add Relation Ne Se Ferme Pas
**Problème**: Après submit, le modal restait ouvert
**Cause**: Callback `submit` ne contrôlait pas `modal-add-relation.is_open`
**Solution**: Callback unifié qui gère toggle ET submit

```python
@app.callback(
    [Output('modal-add-relation', 'is_open'),  # Contrôle du modal
     Output('dropdown-add-rel-p1', 'value'),
     Output('dropdown-add-rel-type', 'value'),
     Output('dropdown-add-rel-p2', 'value'),
     Output('add-relation-status', 'children'),
     Output('data-version', 'data', allow_duplicate=True)],
    ...
)
def toggle_and_submit_add_relation(...):
    if triggered_id == 'btn-submit-add-relation':
        # ... créer relation ...
        return False, None, None, None, success_msg, new_version  # Close modal
```

### ✅ 4. Merge Person Ne Fonctionnait Pas
**Problèmes**:
1. Méthode appelée `merge_persons()` au lieu de `merge()`
2. Lecture `source` APRÈS le merge (déjà supprimé)
3. Callback utilisait `allow_duplicate=True` (cause conflits)

**Solution**: Callback unifié + lecture noms AVANT merge

```python
# Get names BEFORE merge (source will be deleted)
source = person_repository.read(source_id)
target = person_repository.read(target_id)
source_name = source['name']
target_name = target['name']

# Merge using correct method name
success, message = person_repository.merge(source_id, target_id)
```

### ✅ 5. Auto-Refresh Après Éditions
**Problème**: Le graphe ne se mettait pas à jour automatiquement après un edit
**Solution**: Système de versioning avec `dcc.Store`

1. **Store caché**: `dcc.Store(id='data-version', data=0)`
2. **Graphe écoute le store**: 
   ```python
   @app.callback(
       Output('network-graph', 'figure'),
       [Input('layout-dropdown', 'value'),
        Input('color-dropdown', 'value'),
        Input('data-version', 'data'),  # ← Trigger refresh!
        Input('auto-refresh', 'n_intervals')]
   )
   ```
3. **Chaque edit bump la version**:
   ```python
   new_version = (current_version or 0) + 1
   return ..., new_version  # ← Force graph refresh
   ```

## Callbacks Modifiés

### ✅ `submit_add_person`
- Ajout Output `data-version`
- Bump version après ajout

### ✅ `toggle_and_submit_add_relation`  
- Callback unifié (toggle + submit)
- Contrôle `modal.is_open`
- Bump version après création
- Conversion IDs → noms

### ✅ `submit_edit_person`
- Ajout Output `data-version`
- Bump version après update

### ✅ `toggle_and_submit_merge_persons`
- Callback unifié (toggle + submit)
- Lecture noms AVANT merge
- Appel `merge()` au lieu de `merge_persons()`
- Bump version après merge

### ✅ `update_graph`
- Ajout Input `data-version`
- Se déclenche automatiquement quand version change

## Architecture Auto-Refresh

```
┌─────────────────┐
│  User Action    │
│  (Add/Edit/...)│
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Callback       │
│  - Create/Update│
│  - Clear cache  │
│  - Bump version │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  data-version   │
│  Store changes  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  update_graph   │
│  Listens to     │
│  data-version   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Graph Refresh  │
│  Automatic! ✨  │
└─────────────────┘
```

## Tests À Effectuer

1. **Add Person** → Graphe se met à jour automatiquement ✅
2. **Add Relation** → Modal se ferme + graphe update ✅
3. **Edit Person** → Graphe se met à jour automatiquement ✅
4. **Merge Person** → Graphe se met à jour automatiquement ✅
5. **Delete Person** → Graphe se met à jour automatiquement ✅
6. **Relations uniques** → Pas de doublons A→B et B→A ✅

## Imports Ajoutés

```python
from dash import ..., no_update  # Pour gérer Outputs conditionnels
```

## Notes

- `allow_duplicate=True` utilisé uniquement pour `data-version` car plusieurs callbacks le modifient
- `no_update` pour ne pas modifier un Output quand non nécessaire
- Logs debug (`print`) ajoutés pour monitoring temps réel
- Cache invalidé (`graph_builder.clear_cache()`) avant chaque bump version
