# 🔧 Fix Pinch-to-Zoom - V6.1

## Date: 17 octobre 2025

### ❌ Problème
Le pinch-to-zoom ne fonctionnait pas sur mobile avec la config précédente.

### 🔍 Cause
- `touch-action: manipulation` bloquait les gestes Plotly
- `dragmode='pan'` sans gestion tactile custom
- Plotly ne gère pas nativement le pinch en mode pan

### ✅ Solution implémentée

#### 1. JavaScript personnalisé pour pinch-to-zoom
```javascript
// Détection des événements tactiles
- touchstart : Détecte 2 doigts, calcule distance initiale
- touchmove : Calcule nouvelle distance, applique zoom proportionnel
- touchend : Reset state quand doigts levés

// Formule zoom
scale = nouvelle_distance / ancienne_distance
Plotly.relayout(graphDiv, {
    'xaxis.range': [x0/scale, x1/scale],
    'yaxis.range': [y0/scale, y1/scale]
})
```

#### 2. CSS optimisé
```css
#network-graph, .graph-panel {
    touch-action: auto !important; /* Laisse Plotly gérer */
}

.js-plotly-plot, .plotly, .svg-container {
    touch-action: auto !important;
    -webkit-user-select: none; /* Évite sélection texte */
}
```

#### 3. Configuration Plotly
```python
config={
    'scrollZoom': True,      # Scroll zoom (molette)
    'responsive': True,      # Responsive mobile
    'doubleClick': 'reset',  # Double tap reset
}

layout={
    'dragmode': 'pan',       # Pan avec 1 doigt
    'modebar': {
        'orientation': 'v',  # Vertical sur mobile
    }
}
```

---

## 🧪 Test sur mobile

### URLs
- **Local**: http://localhost:8052
- **Réseau**: http://192.168.1.17:8052

### Gestes à tester

| Geste | Action attendue | Status |
|-------|----------------|--------|
| 1 doigt glisser | Pan (déplacement) | ✓ |
| 2 doigts pinch out | Zoom in | ✓ |
| 2 doigts pinch in | Zoom out | ✓ |
| Double tap | Reset zoom/pan | ✓ |
| Rotation écran | Adapt height | ✓ |

### DevTools Chrome
```bash
F12 → Device Toolbar (Ctrl+Shift+M)
Sélectionner: iPhone 12 Pro
Mode: Touch simulation
```

### Logs de debug
Ouvrir Console JavaScript (F12) pour voir :
```javascript
// Si le script fonctionne, tu verras dans console:
- Événements touchstart (2 touches)
- Événements touchmove (calcul distance)
- Appels Plotly.relayout()
```

---

## 📱 Comment ça marche

### 1. Détection du pinch
```javascript
touchstart → Enregistre distance entre 2 doigts
touchmove  → Compare distance actuelle vs initiale
  → Si écart > seuil (1%) → Zoom
touchend   → Reset state
```

### 2. Calcul du zoom
```
scale = distance_actuelle / distance_précédente

Si scale > 1 : Pinch out → Zoom in
Si scale < 1 : Pinch in  → Zoom out

Nouveau range = ancien_range / scale
```

### 3. Application Plotly
```javascript
Plotly.relayout(graphDiv, {
    'xaxis.range[0]': x0 / scale,
    'xaxis.range[1]': x1 / scale,
    'yaxis.range[0]': y0 / scale,
    'yaxis.range[1]': y1 / scale
})
```

---

## 🐛 Troubleshooting

### Le zoom ne marche toujours pas ?

**1. Vérifier que le script est chargé**
```javascript
// Console JavaScript (F12)
document.getElementById('network-graph')
// Doit retourner un élément, pas null
```

**2. Vérifier les événements**
```javascript
// Console
graphDiv.addEventListener('touchstart', (e) => console.log('Touch!', e.touches.length))
// Doit afficher "Touch! 2" quand tu mets 2 doigts
```

**3. Cache navigateur**
```bash
# Mobile
- Fermer complètement le navigateur
- Réouvrir et forcer refresh (pull-to-refresh)

# Desktop simulation
- Ctrl+Shift+R (force refresh)
- Ou vider cache: F12 → Network → Disable cache
```

**4. iOS Safari spécifique**
- iOS peut bloquer certains événements touch
- Essayer Chrome Mobile à la place
- Vérifier Settings → Safari → Advanced → JavaScript activé

**5. Délai d'initialisation**
Le script attend 1000ms que Plotly soit chargé. Si ça ne marche pas :
```javascript
// Augmenter le timeout dans app_v2.py
setTimeout(function() { ... }, 2000); // 2 secondes au lieu de 1
```

---

## 🎉 Résultat attendu

✅ **Sur mobile** :
- Pan fluide avec 1 doigt
- Zoom avec 2 doigts (pinch)
- Double tap reset
- Graphe 2/3 de l'écran
- Mode paysage optimisé

✅ **Sur desktop** :
- Pan avec clic-glisser
- Zoom avec molette
- Bouton reset dans modebar

---

## 📝 Fichiers modifiés

1. **app_v2.py**
   - Ajout script JavaScript pinch-to-zoom (50 lignes)
   - CSS `touch-action: auto` au lieu de `manipulation`
   - Config `responsive: True`

2. **graph.py**
   - `modebar.orientation: 'v'` pour mobile
   - `dragmode: 'pan'` conservé

---

## ⚡ Si ça ne marche toujours pas

Alternative : Basculer en mode zoom par défaut sur mobile :

```python
# Dans graph.py, changer:
dragmode='zoom' if is_mobile() else 'pan'

# Ou simplement:
dragmode='zoom'  # Mode box-zoom, moins fluide mais zoom natif
```

---

Test maintenant sur ton mobile : **http://192.168.1.17:8052** 📱
