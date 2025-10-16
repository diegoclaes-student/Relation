# 📱 V6 - Amélioration Mobile & Responsive

## Date: 17 octobre 2025

### 🎯 Objectif
Rendre l'application **100% utilisable sur mobile** avec zoom tactile et graphe agrandi.

---

## ✅ Modifications effectuées

### 1. **Graphe agrandi (2/3 de l'écran)**
```css
@media (max-width: 768px) {
    #network-graph {
        height: calc(66vh - 100px) !important;
    }
}
```
- Mobile portrait : 66% de la hauteur du viewport
- Mobile landscape : 85% de la hauteur du viewport

### 2. **Zoom tactile avec deux doigts**
```css
#network-graph {
    touch-action: manipulation; /* Permet pinch-to-zoom */
}
```
```javascript
config={
    'scrollZoom': True,
    'doubleClick': 'reset',
    'modeBarButtonsToAdd': ['resetScale2d'],
}
```

### 3. **Breakpoints responsive**
| Breakpoint | Hauteur | Usage |
|------------|---------|-------|
| > 1200px | 600px | Desktop (2 colonnes) |
| < 1200px | 66vh | Tablette (1 colonne) |
| < 768px | 66vh - 100px | Mobile Large |
| < 480px | 66vh - 80px | Mobile Small |
| Landscape | 85vh - 60px | Paysage mobile |

### 4. **Optimisations tactiles**
- Touch targets : **44px minimum** (Apple Guidelines)
- Inputs : **font-size: 16px** (évite zoom auto iOS)
- Touch-action : **manipulation** (pinch-to-zoom natif)
- Modals : **full-width sur mobile**

### 5. **Gestes supportés**
- ✅ **Pinch-to-zoom** : Deux doigts pour zoomer/dézoomer
- ✅ **Pan** : Un doigt pour déplacer le graphe
- ✅ **Double tap** : Reset du zoom
- ✅ **Scroll** : Contrôles et liste accessible

---

## 📱 Testing

### URLs
- Local : http://localhost:8052
- Réseau : http://192.168.1.17:8052

### DevTools Chrome
1. F12 → Toggle Device Toolbar (Ctrl+Shift+M)
2. Sélectionner iPhone/iPad
3. Tester portrait + landscape

### Tests manuels
```bash
# Sur mobile, ouvrir :
http://192.168.1.17:8052

# Tester :
- Zoom avec 2 doigts ✓
- Pan avec 1 doigt ✓
- Double tap reset ✓
- Rotation portrait/paysage ✓
```

---

## 🎨 Fichiers modifiés

1. **app_v2.py**
   - Ajout config `doubleClick`, `modeBarButtonsToAdd`
   - CSS responsive étendu avec breakpoints mobile
   - Touch-action: manipulation
   - Hauteurs adaptatives (66vh, 85vh)

2. **graph.py**
   - Pas de modification (déjà optimisé)

---

## 🚀 Résultat

- ✅ Graphe occupe 2/3 de l'écran mobile
- ✅ Zoom tactile fonctionnel (pinch-to-zoom)
- ✅ Pan fluide avec un doigt
- ✅ Double tap reset opérationnel
- ✅ Mode paysage optimisé (85vh)
- ✅ Tous les boutons tactiles (44px)
- ✅ Inputs sans zoom auto iOS (16px)

---

## 📝 Notes techniques

**Touch-action: manipulation**
- Permet les gestes natifs (pinch, pan)
- Désactive les comportements par défaut du navigateur
- Compatible iOS Safari, Chrome Android

**calc(66vh - 100px)**
- 66% du viewport height
- Soustraction de 100px pour header + padding
- S'adapte dynamiquement à toutes les tailles

**orientation: landscape**
- Media query spécifique pour mode paysage
- Maximise l'espace graphe (85vh)
- Header ultra-compact

---

## 🎉 Prêt pour production !
