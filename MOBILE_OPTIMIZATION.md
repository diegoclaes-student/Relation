# 📱 Optimisations Mobile

## ✅ Corrections apportées (Commit à venir)

### 1. **Viewport Configuration**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
```
- `maximum-scale=5.0` : Permet de zoomer jusqu'à 500%
- `user-scalable=yes` : Autorise le zoom natif du navigateur

### 2. **Graphique Plotly - Configuration**
```python
config={
    'displayModeBar': False,  # Cache la barre d'outils sur mobile
    'scrollZoom': True,       # Active le zoom via scroll/pinch
    'responsive': True,        # Redimensionnement automatique
    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],  # Simplifie l'interface
}
```

### 3. **Pinch-to-Zoom Custom**
Un système JavaScript custom gère le pinch zoom à 2 doigts :
- Détection de 2 doigts simultanés
- Calcul de la distance entre les doigts
- Mise à jour du zoom Plotly en temps réel
- Throttling à 60fps pour la performance

```javascript
// Activation automatique au chargement
document.addEventListener('DOMContentLoaded', function() {
    attachPinchZoomListeners();
});
```

### 4. **CSS Touch-Action**
```css
#network-graph {
    touch-action: auto !important; /* Permet tous les gestes natifs */
}

.graph-panel {
    touch-action: auto !important; /* Laisse Plotly gérer */
    overflow: hidden; /* Empêche le scroll du container */
}

/* Force Plotly à accepter les gestes tactiles */
.js-plotly-plot, .plotly, .svg-container {
    touch-action: auto !important;
}
```

### 5. **Menu Hamburger**
- Position: `absolute` en haut à droite
- Z-index: `999` pour rester au-dessus du graphique
- Taille: `48x48px` pour une cible de touch accessible (recommandation : >44px)
- **Scrollable** : `max-height: calc(100vh - 100px)` + `overflow-y: auto`
- **Mobile** : `max-height: calc(100vh - 120px)` pour plus d'espace
- **Landscape** : `max-height: calc(100vh - 80px)` pour écrans courts
- **Portrait** : `max-height: calc(100vh - 140px)` pour tenir compte du header
- Smooth scrolling sur iOS : `-webkit-overflow-scrolling: touch`
- Hover effect: `scale(1.1)` pour feedback visuel

```css
#hamburger-menu {
    max-height: calc(100vh - 100px);
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
}

@media (max-width: 480px) {
    #hamburger-menu {
        max-height: calc(100vh - 120px) !important;
        max-width: calc(100vw - 30px);
    }
}
```

### 6. **Responsive Breakpoints**
- **Tablette (< 1200px)** : Layout 1 colonne
- **Mobile (< 768px)** : Padding réduit, graphique plein écran
- **Petit mobile (< 480px)** : Header compact, controls optimisés
- **Très petit (< 360px)** : Ajustements supplémentaires

### 7. **Boutons de Zoom**
- Position: `fixed` en bas à droite
- Empêchent la propagation des événements touch
- Taille minimale: `40x40px`
- `touchAction: 'manipulation'` pour réponse immédiate

## 🔍 Tests à effectuer

### Sur mobile (iOS/Android) :
1. ✅ Pinch zoom à 2 doigts fonctionne
2. ✅ Menu hamburger accessible et responsive
3. ✅ Boutons zoom + / - fonctionnent
4. ✅ Drag/pan avec 1 doigt fonctionne
5. ✅ Double tap pour reset fonctionne
6. ✅ Interface s'adapte à la taille d'écran
7. ✅ Pas de scroll indésirable de la page
8. ✅ Header reste visible

### Landscape vs Portrait :
- **Portrait** : Menu complet visible
- **Landscape** : Header compact, plus d'espace pour le graphique

## 🐛 Problèmes connus et solutions

### Problème : Menu hamburger dépasse de l'écran
**Solution** : Le menu a maintenant `max-height: calc(100vh - 100px)` et `overflow-y: auto`. Sur mobile (< 480px), il utilise `max-height: calc(100vh - 120px)` pour laisser plus d'espace au header. Le menu est scrollable verticalement avec smooth scrolling sur iOS (`-webkit-overflow-scrolling: touch`).

### Problème : Pinch zoom ne fonctionne pas
**Solution** : Vérifier dans la console navigateur :
```javascript
console.log('✅ Attaching pinch-zoom listeners');
```
Si ce message n'apparaît pas, le JavaScript n'est pas chargé.

### Problème : Menu hamburger trop petit
**Solution** : La taille est déjà `48x48px` (recommandation Apple/Google : >44px)

### Problème : Graphique ne remplit pas l'écran
**Solution** : CSS media query force `height: calc(100vh - 60px)`

## 📚 Références

- [Apple Human Interface Guidelines - Touch Targets](https://developer.apple.com/design/human-interface-guidelines/inputs/touchscreen-gestures)
- [Google Material Design - Touch Targets](https://material.io/design/usability/accessibility.html#layout-and-typography)
- [Plotly.js Touch Interaction](https://plotly.com/javascript/configuration-options/)
- [MDN touch-action](https://developer.mozilla.org/en-US/docs/Web/CSS/touch-action)

## 🚀 Prochaines améliorations possibles

1. **Geste 3 doigts** : Reset du zoom
2. **Vibration feedback** : Confirmation tactile des actions
3. **Mode sombre** : Économie batterie sur OLED
4. **PWA** : Installation comme app native
5. **Offline mode** : Cache des données localement
6. **Lazy loading** : Charger le graphique progressivement
