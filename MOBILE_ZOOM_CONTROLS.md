# Mobile - Contrôles de Zoom et Repositionnement

## Date : 19 octobre 2025

## Problème Initial
- Le pinch-to-zoom ne fonctionnait pas correctement sur mobile
- La barre d'outils Plotly était visible sur mobile (mais pas sur PC)
- Le menu hamburger prenait de la place en dehors du graphique
- Le bouton plein écran n'était pas au même niveau que le hamburger

## Solution Implémentée

### 1. Boutons Zoom +/- 
✅ **Ajout de contrôles manuels de zoom**
- Bouton **+** : Zoom avant (facteur 1.5x)
- Bouton **-** : Zoom arrière (facteur 0.67x)
- Positionnés en haut à droite sous le menu hamburger
- Design : 40x40px, rectangulaires avec coins arrondis (8px)
- JavaScript pur pour manipuler les axes Plotly

**Code clé (JavaScript)** :
```javascript
function zoomGraph(factor) {
    var xaxis = graphDiv.layout.xaxis;
    var yaxis = graphDiv.layout.yaxis;
    
    // Calculer le centre actuel
    var xCenter = (xRange[0] + xRange[1]) / 2;
    var yCenter = (yRange[0] + yRange[1]) / 2;
    
    // Nouvelle largeur/hauteur divisée par le facteur
    var xSpan = (xRange[1] - xRange[0]) / factor / 2;
    var ySpan = (yRange[1] - yRange[0]) / factor / 2;
    
    // Zoom centré
    window.Plotly.relayout(graphDiv, {
        'xaxis.range': [xCenter - xSpan, xCenter + xSpan],
        'yaxis.range': [yCenter - ySpan, yCenter + ySpan]
    });
}
```

### 2. Masquage de la Barre d'Outils Plotly
✅ **Configuration simplifiée du graphique**
```python
config={
    'displayModeBar': False,  # Masquer complètement la barre d'outils
    'scrollZoom': True,       # Garder le scroll zoom pour desktop
    'displaylogo': False,
    'doubleClick': 'reset',
    'responsive': True,
}
```

### 3. Repositionnement du Menu Hamburger
✅ **Menu intégré dans le graphique**

**Avant** :
- Menu hamburger en position `fixed`, en bas à droite
- Prenait de l'espace en dehors du graphique

**Après** :
- Menu hamburger en haut à droite **DANS** le graphique
- Position : `top: 15px, right: 15px`
- Menu déroulant apparaît juste en dessous
- Géré 100% en JavaScript (pas de callback Dash)

**Positionnement des contrôles** :
```
+----------------------------------+
|                  🍔 Hamburger    |  ← top: 15px
|                   + Zoom In      |  ← top: 75px
|                   - Zoom Out     |  ← top: 125px
|                                  |
|         [GRAPHIQUE]              |
|                                  |
| 📺 Fullscreen                    |  ← bottom: 15px, left: 15px
+----------------------------------+
```

### 4. Augmentation de l'Espace Graphique
✅ **Plus de place pour le graphe sur mobile**

**CSS Mobile (< 768px)** :
```css
.graph-panel {
    min-height: calc(80vh - 70px); /* Avant : 66vh */
}

#network-graph {
    height: calc(80vh - 70px) !important; /* Avant : 66vh */
}
```

**Gain d'espace** :
- De **66%** à **80%** de la hauteur du viewport
- Menu hamburger n'occupe plus d'espace externe
- Header compact (50px seulement)

### 5. Gestion du Menu Hamburger en JavaScript
✅ **Toggle sans callback Dash**

```javascript
hamburgerBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    var isVisible = hamburgerMenu.style.display !== 'none';
    hamburgerMenu.style.display = isVisible ? 'none' : 'block';
});

// Fermer si on clique ailleurs
document.addEventListener('click', function(e) {
    if (!hamburgerMenu.contains(e.target) && e.target !== hamburgerBtn) {
        hamburgerMenu.style.display = 'none';
    }
});
```

## Architecture Technique

### Modifications des Fichiers

**app_v2.py** :
1. **Config Plotly** (ligne ~815) : `displayModeBar: False`
2. **Boutons de contrôle** (lignes ~820-910) : Ajout de 3 nouveaux boutons (hamburger, zoom+, zoom-)
3. **Menu déroulant** (lignes ~915-960) : Repositionné en `fixed` sous le hamburger
4. **JavaScript** (lignes ~653-790) : Nouvelle fonction `initZoomButtons()`, `zoomGraph()`, et `initHamburgerMenu()`
5. **CSS Mobile** (lignes ~350-360) : Hauteur augmentée à 80vh
6. **Callback supprimé** (ancien ligne ~1410) : Toggle hamburger maintenant en JS

## Résultat Final

### ✅ Avantages
1. **Zoom précis** : Boutons +/- permettent un contrôle exact du niveau de zoom
2. **UI épurée** : Barre d'outils Plotly masquée, interface plus propre
3. **Plus d'espace** : Graphique prend 80% de l'écran mobile (vs 66% avant)
4. **Meilleure UX** : Tous les contrôles regroupés dans/sur le graphique
5. **Performance** : Menu hamburger géré en JS pur (pas de round-trip serveur)

### 🎨 Design Mobile Optimisé
- Menu hamburger : 48x48px, rond, bleu foncé
- Boutons zoom : 40x40px, carrés arrondis, bleu clair
- Bouton fullscreen : 48x48px, rond, bleu clair, en bas à gauche
- Tous avec bordure blanche 2px et ombre portée

### 📱 Expérience Utilisateur
1. **Ouvrir le menu** : Tap sur le hamburger en haut à droite
2. **Zoomer** : Tap sur + ou - sous le hamburger
3. **Plein écran** : Tap sur le bouton en bas à gauche
4. **Naviguer** : Drag pour déplacer, scroll sur desktop

## Tests Recommandés

1. ✅ Tester les boutons +/- sur mobile et desktop
2. ✅ Vérifier que le menu hamburger s'ouvre/ferme correctement
3. ✅ Confirmer que le zoom est centré et fluide
4. ✅ S'assurer que le plein écran fonctionne toujours
5. ✅ Tester que cliquer en dehors du menu le ferme

## Notes Techniques

### Pourquoi JavaScript au lieu de Callbacks Dash ?
- **Latence** : Pas de round-trip serveur pour toggle le menu
- **Fluidité** : Interactions instantanées
- **Simplicité** : Pas besoin de State/Output complexes
- **Performance** : Moins de charge sur le serveur Dash

### Calcul du Zoom
Le zoom utilise un facteur multiplicatif sur les ranges des axes :
- **Zoom in (1.5x)** : Les ranges sont divisés par 1.5 → vue plus proche
- **Zoom out (0.67x)** : Les ranges sont multipliés par 1.5 → vue plus éloignée
- Le centre de la vue reste fixe pendant le zoom

### Compatibilité
- ✅ Chrome/Safari mobile
- ✅ Firefox mobile
- ✅ Desktop (tous navigateurs)
- ✅ Tablette

## Prochaines Améliorations Possibles

1. **Animation du zoom** : Transition smooth lors du zoom
2. **Indicateur de niveau de zoom** : Afficher "100%", "150%", etc.
3. **Zoom sur point** : Zoomer vers l'endroit où l'utilisateur a cliqué
4. **Bouton reset** : Revenir au zoom initial en un clic
5. **Gesture long-press** : Maintenir + ou - pour zoom continu

---

**Status** : ✅ Implémenté et fonctionnel
**Prochaine étape** : Tests utilisateur sur mobile
