# 📱 Guide de Test Mobile - Social Network Analyzer

## ✅ Améliorations V6 - Responsive Mobile

### 🎯 Changements effectués :

1. **Graphe agrandi sur mobile** : Occupe maintenant **2/3 de l'écran** (66vh)
2. **Zoom tactile activé** : Pinch-to-zoom avec **deux doigts** 
3. **Double tap** : Reset du zoom
4. **Bouton reset zoom** : Disponible dans la barre d'outils
5. **Mode paysage** : Graphe prend 85% de l'écran en landscape

### 📲 URLs de test :

- **Local** : http://localhost:8052
- **Réseau local** : http://192.168.1.17:8052

### 🧪 Tests à effectuer sur mobile :

#### Portrait Mode (📱)
- [ ] Le graphe occupe environ 2/3 de l'écran (hauteur minimum 450px)
- [ ] Zoom avec deux doigts fonctionne (pinch-to-zoom)
- [ ] Pan avec un doigt pour déplacer le graphe
- [ ] Double tap pour reset le zoom
- [ ] Les contrôles sont accessibles en scrollant vers le bas
- [ ] Les boutons ont une taille tactile correcte (minimum 44px)

#### Landscape Mode (📱 horizontal)
- [ ] Le graphe prend presque tout l'écran (85vh)
- [ ] Header compact pour maximiser l'espace graphe
- [ ] Zoom tactile fonctionne toujours

#### Tablette (📱 grande)
- [ ] Layout en une colonne
- [ ] Graphe à hauteur adaptative
- [ ] Tous les contrôles visibles

### 🔍 Breakpoints configurés :

| Taille écran | Hauteur graphe | Mode |
|--------------|----------------|------|
| > 1200px | 600px | Desktop - 2 colonnes |
| < 1200px | 66vh - 100px | Tablette - 1 colonne |
| < 768px | 66vh - 100px | Mobile Large |
| < 480px | 66vh - 80px | Mobile Small |
| Landscape | 85vh - 60px | Mobile Paysage |

### ⚙️ Fonctionnalités tactiles :

- **Touch-action: manipulation** → Permet pinch-to-zoom natif
- **ScrollZoom: true** → Zoom avec gestes
- **DoubleClick: reset** → Double tap reset
- **Drag mode: pan** → Déplacement fluide

### 🎨 Optimisations UX :

- Inputs font-size: 16px (évite zoom auto sur iOS)
- Touch targets: 44px minimum
- Modals fullscreen sur mobile
- Scrollbars tactiles (10px de largeur)

### 🐛 Troubleshooting :

**Le zoom ne fonctionne pas ?**
- Vérifier que le navigateur mobile supporte touch-action
- Essayer de rafraîchir la page (F5 ou pull-to-refresh)

**Le graphe est trop petit ?**
- Vérifier l'orientation (portrait vs landscape)
- Calculer : Hauteur = 66% viewport - header

**Les boutons sont difficiles à toucher ?**
- Tous les boutons font minimum 44px (recommandation Apple)

---

## 🎉 Bonne navigation !
