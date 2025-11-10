# 🔍 DIAGNOSTIC COMPLET : Pinch-to-Zoom Mobile

## ❌ PROBLÈME RAPPORTÉ
"Le pitch to zoom ne fonctionne toujours pas sur mobile"

## 🔬 ANALYSE TECHNIQUE APPROFONDIE

### 1. Limitations Plotly.js

**DÉCOUVERTE MAJEURE** : Plotly.js **NE SUPPORTE PAS** le pinch-to-zoom natif sur les graphes cartésiens (scatter, line, bar, etc.)

**Documentation officielle** : [plotly.com/javascript/configuration-options](https://plotly.com/javascript/configuration-options/)
> **"mousewheel or two-finger scroll zooms the plot"** avec `scrollZoom: true`

**Ce qui est supporté** :
- ✅ **Desktop** : Mouse wheel / Trackpad scroll → zoom
- ✅ **Mobile** : Two-finger **SCROLL** (glisser 2 doigts haut/bas comme scroll) → zoom
- ❌ **Mobile** : Two-finger **PINCH** (écarter/rapprocher doigts) → **NON SUPPORTÉ**

**Pourquoi ?**
- Le pinch-to-zoom est un geste natif du browser (pour zoomer la page entière)
- Plotly capture les événements touch pour le **pan** (déplacer le graphe)
- Conflits entre gestures natives et Plotly = pas de pinch-to-zoom

### 2. Configuration Actuelle

**Dans `app_v2.py` (ligne 817)** :
```python
config={
    'displayModeBar': 'hover',  # ✅ Boutons natifs visibles
    'scrollZoom': True,         # ✅ Scroll/wheel zoom activé
    'modeBarButtonsToAdd': ['zoomIn2d', 'zoomOut2d', 'resetScale2d'],  # ✅
}
```

**Dans `graph.py` (ligne 688)** :
```python
fig.update_layout(
    dragmode='pan',  # ⚠️ Mode PAN = drag pour déplacer, pas zoomer
)
```

### 3. Comportements Actuels

| Plateforme | Geste | Config | Résultat |
|------------|-------|---------|----------|
| 🖥️ Desktop | Mouse wheel | `scrollZoom: True` | ✅ Zoom fonctionne |
| 🖥️ Desktop | Trackpad 2-doigts scroll | `scrollZoom: True` | ✅ Zoom fonctionne |
| 🖥️ Desktop | Click + drag | `dragmode='pan'` | ✅ Pan (déplace graphe) |
| 📱 Mobile | 2-doigts scroll (↕️) | `scrollZoom: True` | ✅ Zoom théorique |
| 📱 Mobile | 2-doigts pinch (↔️) | N/A | ❌ **NON SUPPORTÉ** par Plotly |
| 📱 Mobile | 1-doigt drag | `dragmode='pan'` | ✅ Pan fonctionne |
| 📱 Mobile | Bouton + natif | `modeBarButtonsToAdd` | ✅ Zoom fonctionne |
| 📱 Mobile | Bouton - natif | `modeBarButtonsToAdd` | ✅ Zoom fonctionne |

### 4. Tests Effectués (Session Précédente)

**❌ Approche 1** : JavaScript custom avec `waitForPlotlyRender()`
- **Problème** : `graphDiv.data` jamais disponible (timing Dash/React)
- **Résultat** : 50+ tentatives, échec total

**❌ Approche 2** : Event listener `plotly_afterplot`
- **Problème** : Event ne se déclenche jamais dans Dash
- **Résultat** : Aucun callback exécuté

**❌ Approche 3** : Polling `setInterval()` + `Plotly.relayout()`
- **Problème** : Même issue de timing
- **Résultat** : Échec

**✅ Approche 4** : Boutons custom → Boutons natifs Plotly
- **Solution** : JavaScript qui clique sur les boutons natifs `.modebar`
- **Résultat** : Fonctionne parfaitement ! ✅

**❌ Approche 5** : Implémentation pinch-to-zoom custom (400+ lignes)
- **Problème** : Impossible de détecter quand Plotly est prêt
- **Résultat** : Supprimé (inutile et non fonctionnel)

## 🎯 SOLUTIONS DISPONIBLES

### Option A : Boutons Zoom (ACTUELLE - FONCTIONNE)

**Avantages** :
- ✅ Déjà implémenté et fonctionnel
- ✅ Boutons natifs Plotly (zoomIn2d, zoomOut2d)
- ✅ Boutons custom HTML reliés aux natifs
- ✅ Marche sur tous les devices
- ✅ Simple et fiable

**Inconvénients** :
- ❌ Moins naturel que pinch sur mobile
- ❌ Nécessite cliquer sur un bouton

**Code** (déjà en place) :
```javascript
// JavaScript qui relie boutons custom → natifs
document.getElementById('btn-zoom-in').addEventListener('click', function() {
    var plotlyButton = document.querySelector('[data-title="Zoom in"]');
    plotlyButton.click();
});
```

### Option B : Two-Finger Scroll (TESTABLE)

**Principe** : Utiliser le scroll à 2 doigts (comme un trackpad)

**Avantages** :
- ✅ Supporté nativement par Plotly (`scrollZoom: True`)
- ✅ Pas de code custom nécessaire
- ✅ Geste connu sur mobile (scroll pages web)

**Inconvénients** :
- ❓ Moins intuitif que pinch
- ❓ Peut confondre avec scroll page
- ❓ Fonctionne-t-il vraiment sur tous les mobiles ?

**Implémentation** :
```python
# Déjà activé dans app_v2.py
config={'scrollZoom': True}
```

### Option C : Dragmode='zoom' (À TESTER)

**Principe** : Changer `dragmode='pan'` → `dragmode='zoom'`

**Comportement** :
- **Desktop** : Click-drag dessine un rectangle → zoom sur cette zone
- **Mobile** : Touch-drag dessine un rectangle → zoom sur cette zone

**Avantages** :
- ✅ Mode zoom natif Plotly
- ✅ Zoom précis sur une zone
- ✅ Fonctionne sur desktop et mobile

**Inconvénients** :
- ❌ Perd le mode pan (déplacement)
- ❌ Geste différent de pinch
- ❌ Peut être moins intuitif

**Implémentation** :
```python
# Dans graph.py, ligne 688
dragmode='zoom',  # Au lieu de 'pan'
```

### Option D : Hybrid Mode (COMPLEXE)

**Principe** : Détecter le device et adapter le dragmode

```python
import dash
from flask import request

def get_dragmode():
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(x in user_agent for x in ['android', 'iphone', 'ipad'])
    return 'zoom' if is_mobile else 'pan'
```

**Problème** : Le layout est généré côté serveur, pas dynamiquement

### Option E : Accepter la Limitation

**Réalité** :
- Plotly.js ne supporte pas le pinch-to-zoom sur cartesian plots
- Les boutons fonctionnent bien
- Le two-finger scroll théoriquement aussi

**Message aux utilisateurs** :
> "Sur mobile, utilisez les boutons + et - pour zoomer, ou faites glisser deux doigts verticalement"

## 🧪 RECOMMANDATION FINALE

### TEST À EFFECTUER (Avant toute modification)

1. **Tester scrollZoom sur mobile réel**
   - Ouvrir l'app sur iPhone/Android
   - Essayer de scroll avec 2 doigts (↕️ vertical)
   - Vérifier si le zoom fonctionne

2. **Si scrollZoom ne marche pas** :
   - Les boutons sont la SEULE solution viable
   - Améliorer UX des boutons (taille, position, feedback)

3. **Si scrollZoom marche** :
   - Ajouter un tooltip/guide : "Glissez 2 doigts pour zoomer"
   - Garder les boutons comme alternative

### MODIFICATION PROPOSÉE (Si test concluant)

**Option la plus simple** : Changer dragmode → 'zoom'

```python
# Dans graph.py, ligne 688
dragmode='zoom',  # Desktop: click-drag box, Mobile: touch-drag box
```

**Avantages** :
- Zoom par zone (desktop + mobile)
- Mode natif Plotly
- Pas de code custom

**Inconvénient** :
- Perd le pan (mais on peut l'ajouter au modebar)

## 📊 CONCLUSION

**VÉRITÉ TECHNIQUE** :
Le pinch-to-zoom (écarter 2 doigts) n'existe PAS dans Plotly.js pour les graphes cartésiens. C'est une **limitation du framework**, pas un bug.

**SOLUTIONS VIABLES** :
1. ✅ **Boutons +/-** (déjà implémenté, fonctionne)
2. ❓ **Two-finger scroll** (à tester sur mobile réel)
3. ❓ **Dragmode='zoom'** (zoom par zone, à tester)

**ACTIONS RECOMMANDÉES** :
1. Tester l'app actuelle sur mobile réel
2. Vérifier si scrollZoom (2-doigts ↕️) fonctionne
3. Si oui : Ajouter guide utilisateur
4. Si non : Optimiser les boutons (taille, position, animation)
5. Envisager `dragmode='zoom'` si besoin de zoom par zone

**NE PAS FAIRE** :
- ❌ Essayer d'implémenter un pinch-to-zoom custom (déjà tenté, échec)
- ❌ Créer 400 lignes de JavaScript complexe (maintenance cauchemar)
- ❌ Modifier le core de Plotly (pas possible)

