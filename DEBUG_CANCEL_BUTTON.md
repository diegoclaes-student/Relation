# 🔧 Débogage Bouton "Annuler" - Guide de Test

## 📝 État Actuel

Le bouton "Annuler" a été implémenté avec une approche à 2 callbacks :
1. **Clientside Callback** (JavaScript) : Détecte le clic et met à jour un Store
2. **Server Callback** (Python) : Lit le Store et effectue l'annulation

## 🧪 Comment Tester

### Étape 1 : Ouvrir la Console du Navigateur
1. Allez sur http://localhost:8052
2. Appuyez sur **F12** pour ouvrir les DevTools
3. Allez sur l'onglet **Console**

### Étape 2 : Se Connecter et Aller sur Historique
1. Connectez-vous en tant qu'admin
2. Cliquez sur l'onglet **"📋 Historique"**
3. Vous devriez voir la liste des modifications récentes

### Étape 3 : Cliquer sur "Annuler"
1. Trouvez une action récente avec un bouton "Annuler"
2. Cliquez sur le bouton
3. **Observez la console du navigateur** pour voir :
   ```
   🔍 [CLIENTSIDE] Cancel button detection triggered
   n_clicks_list: [1, 0, 0, ...]
   Triggered: [{...}]
   prop_id: {"index":52,"type":"cancel-history"}.n_clicks
   ✅ Detected cancel for action_id: 52
   ```

### Étape 4 : Vérifier les Logs Serveur
```bash
tail -f /Users/diegoclaes/Code/Relation/app_output.log | grep -E "HISTORY|Cancel"
```

Vous devriez voir :
```
🔍 [HISTORY-CANCEL] Callback triggered!
   cancel_data: {'action_id': 52, 'timestamp': 1697836800}
✅ [HISTORY] Cancel action: action_id=52
   ✅ Action annulée: Personne supprimée: Test User Demo
   → Cache cleared, new version: 16
```

## 🐛 Problèmes Possibles

### Problème 1 : Rien dans la Console du Navigateur
**Cause** : Le clientside callback ne se déclenche pas
**Solution** :
- Vérifiez que les boutons existent dans le DOM (Inspect Element)
- Vérifiez que les IDs correspondent : `{'type': 'cancel-history', 'index': XX}`
- Essayez de rafraîchir la page (Ctrl+F5)

### Problème 2 : Console OK mais pas de logs serveur
**Cause** : Le Store ne déclenche pas le callback serveur
**Solution** :
- Vérifiez que `cancel-action-store` existe dans le layout
- Vérifiez les erreurs dans la console (onglet Console ET Network)

### Problème 3 : "Unauthorized cancel attempt"
**Cause** : Pas connecté en tant qu'admin
**Solution** :
- Reconnectez-vous
- Vérifiez `auth-data` dans le Store (DevTools → Application → Storage)

## 🔍 Debug Manuel

### Test du Clientside Callback
Ouvrez la console du navigateur et exécutez :
```javascript
// Trouver tous les boutons d'annulation
const buttons = document.querySelectorAll('[id*="cancel-history"]');
console.log('Boutons trouvés:', buttons.length);
buttons.forEach(btn => console.log('Button ID:', btn.id));

// Cliquer sur le premier
if (buttons.length > 0) {
    buttons[0].click();
}
```

### Test du Store
```javascript
// Voir la valeur du Store
const store = document.getElementById('cancel-action-store');
console.log('Store value:', store ? store.textContent : 'Not found');
```

### Test Direct du Service (Python)
```bash
cd /Users/diegoclaes/Code/Relation
python -c "
from services.history import history_service

# Lister les actions actives
recent = history_service.get_history(limit=5, status='active')
print(f'Actions actives: {len(recent)}')
if recent:
    first = recent[0]
    print(f'Première action: ID={first[\"id\"]}, type={first[\"action_type\"]}')
    
    # Tester l'annulation
    success, msg = history_service.cancel_action(first['id'], cancelled_by='test')
    print(f'Résultat: {msg}')
"
```

## 📊 Architecture Actuelle

```
[Bouton Annuler]
    ↓ n_clicks
[Clientside Callback] (JavaScript dans le navigateur)
    ↓ détecte le clic, extrait l'action_id
[cancel-action-store] (dcc.Store)
    ↓ data={'action_id': XX, 'timestamp': ...}
[Server Callback] (Python)
    ↓ history_service.cancel_action()
[Base de Données]
    ↓ UPDATE history SET status='cancelled'
    ↓ Revert les changements (DELETE/INSERT selon le type)
[Rafraîchissement UI]
    ↓ Re-render des listes
[Interface Mise à Jour]
```

## ✅ Checklist de Vérification

- [ ] Application démarrée (`curl http://localhost:8052` → 200)
- [ ] Connecté en tant qu'admin
- [ ] Sur l'onglet Historique
- [ ] Console du navigateur ouverte (F12)
- [ ] Logs serveur en cours (`tail -f app_output.log`)
- [ ] Cliqué sur un bouton "Annuler"
- [ ] Vu les logs clientside dans la console
- [ ] Vu les logs serveur dans le terminal
- [ ] L'action a été annulée (déplacée vers "Modifications Annulées")

## 🆘 Si Rien ne Fonctionne

Essayez cette commande Python pour annuler manuellement une action :
```bash
cd /Users/diegoclaes/Code/Relation
python demo_cancel.py
```

Cela créera une personne de test et l'annulera immédiatement pour vérifier que le service fonctionne.
