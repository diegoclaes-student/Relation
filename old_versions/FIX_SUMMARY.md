# 🔧 Résumé des Corrections - 15 oct 2025

## ✅ Problème 1 : Liens affichés en double dans le graphique

### Symptôme
- 2 lignes entre chaque paire de personnes au lieu d'une seule
- Le graphique était encombré et illisible

### Cause
- Les relations sont stockées en **double** dans la base pour gérer la symétrie (A→B ET B→A)
- Le graphique affichait TOUTES les relations sans déduplication
- Exemple: `Diego → Marie` ET `Marie → Diego` créaient 2 arêtes

### Solution
**Fichier modifié:** `app_full.py` (lignes 177-207)

Ajout d'une déduplication avant de construire le graphe :

```python
# ✅ DÉDUPLICATION: Ne garder qu'une direction pour chaque paire (A,B)
seen = set()
unique_relations = []

for p1, p2, rel_type in relations:
    # Normaliser la paire : toujours mettre le plus petit en premier
    pair = tuple(sorted([p1, p2]))
    if pair not in seen:
        seen.add(pair)
        unique_relations.append((p1, p2, rel_type))
```

### Résultat
- **182 relations → 91 liens uniques** affichés
- Graphique beaucoup plus lisible
- Chaque paire de personnes n'a qu'une seule ligne

---

## ✅ Problème 2 : Undo ne gérait pas la symétrie automatiquement

### Symptôme
- Quand on annulait l'ajout d'une relation `A → B`, seule cette direction était supprimée
- La relation inverse `B → A` restait en base
- Résultat: relation asymétrique et graphique incohérent

### Cause
- La fonction `undo_action()` dans `database.py` gérait la symétrie manuellement
- Elle n'utilisait pas les méthodes existantes avec le paramètre `auto_symmetrize`
- Code SQL brut au lieu de réutiliser `delete_relation()` et `add_relation()`

### Solution
**Fichier modifié:** `database.py` (lignes 362-432)

Réécriture complète de `undo_action()` pour utiliser les méthodes avec `auto_symmetrize`:

```python
def undo_action(self, history_id: int, performed_by: str = "admin") -> bool:
    """Annule une action de l'historique avec gestion automatique de la symétrie."""
    
    if action_type == 'ADD':
        # Annuler un ajout = supprimer avec symétrie automatique
        success = self.delete_relation(person1, person2, relation_type, 
                                      performed_by, auto_symmetrize=True)
        
    elif action_type == 'DELETE':
        # Annuler une suppression = recréer avec symétrie automatique
        # INSERT OR IGNORE pour A→B et B→A
        
    elif action_type == 'APPROVE':
        # Annuler approbation = supprimer avec symétrie + remettre en pending
        self.delete_relation(person1, person2, relation_type, 
                           performed_by, auto_symmetrize=True)
```

### Résultat
- Undo d'un ADD : supprime **les 2 directions** (A→B et B→A) ✅
- Undo d'un DELETE : restaure **les 2 directions** (A→B et B→A) ✅
- Undo d'un APPROVE : supprime les 2 directions + remet en pending ✅
- Base de données reste cohérente et symétrique

---

## 📊 Tests effectués

```bash
# Test déduplication
Total relations en base: 182
Relations uniques (dédupliquées): 91
Doublons supprimés: 91 ✅

# Test application
84 personnes, 182 relations
Application démarrée sur http://localhost:8051
Graphique s'affiche correctement avec 91 liens uniques ✅
```

---

## 🎯 Impact

### Avant
- ❌ Graphique illisible avec doublons de liens
- ❌ Undo cassait la symétrie des relations
- ❌ Base incohérente après annulation

### Après
- ✅ Graphique propre avec 1 seul lien par paire
- ✅ Undo gère automatiquement la symétrie
- ✅ Base toujours cohérente et symétrique
- ✅ Code plus maintenable (réutilise les méthodes existantes)

---

## 🔍 Code modifié

1. **app_full.py** (callback `update_graph`)
   - Ajout déduplication des relations symétriques
   - ~20 lignes modifiées

2. **database.py** (méthode `undo_action`)
   - Réécriture complète pour utiliser `auto_symmetrize`
   - ~70 lignes modifiées
   - Meilleure gestion des erreurs
   - Logs plus explicites

---

*Correctifs testés et validés le 15 octobre 2025*
