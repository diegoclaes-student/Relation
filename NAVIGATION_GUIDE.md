# 🎯 Guide de Navigation du Graphe

## Améliorations de Navigation Implémentées

### ✨ Nouvelles Fonctionnalités

#### 🖱️ **Zoom avec molette/trackpad** (ACTIVÉ)
- **Molette de souris** : Scroll pour zoomer/dézoomer
- **Trackpad** : Pincer pour zoomer (deux doigts)
- **Fluide et précis** : Le zoom suit le curseur

#### 🤚 **Déplacement panoramique**
- **Cliquer-glisser** : Déplace la vue du graphe
- **Mode par défaut** : Pas besoin de sélectionner un outil
- **Navigation intuitive** : Comme Google Maps

#### 🔒 **Conservation du zoom** (uirevision)
- **Zoom persistant** : Le graphe conserve votre niveau de zoom lors des mises à jour auto
- **Position sauvegardée** : Votre vue reste stable même avec le refresh toutes les 5 secondes
- **Pas de reset automatique** : Plus de retour à la vue par défaut

#### 🎨 **Interface optimisée**
- **Légende retirée** : Plus d'espace pour le graphe (pas de liste de communautés)
- **Marges réduites** : Utilisation maximale de l'écran
- **Barre d'outils épurée** : Toujours visible avec contrôles essentiels
- **Pas de logo Plotly** : Interface propre et professionnelle

#### 🖥️ **Mode plein écran natif**
- **Bouton dans la barre d'outils** : Cliquez pour passer en plein écran
- **Compatible tous navigateurs** : Fonctionne sur Chrome, Firefox, Safari, Edge
- **Raccourci clavier** : Échap pour quitter le plein écran

### 🎮 Contrôles Disponibles

| Action | Comment faire |
|--------|---------------|
| **Zoomer** | Molette souris / Pincer trackpad |
| **Dézoomer** | Molette inverse / Écarter trackpad |
| **Se déplacer** | Cliquer-glisser avec souris/trackpad |
| **Plein écran** | Cliquer sur l'icône en haut à droite de la barre d'outils |
| **Réinitialiser la vue** | Cliquer sur le bouton "🏠 Home" dans la barre d'outils |
| **Export image** | Cliquer sur l'icône 📷 dans la barre d'outils |
| **Hover info** | Passer la souris sur un nœud pour voir les détails |

### ⚙️ Configuration Technique

```python
# Dans dashboard.py et app.py
config={
    'scrollZoom': True,              # Zoom avec molette activé
    'doubleClick': False,            # Double-clic désactivé (pas de reset)
    'displayModeBar': True,          # Barre d'outils visible
    'displaylogo': False,            # Logo Plotly masqué
    'modeBarButtonsToAdd': ['toggleSpikelines'],  # Boutons supplémentaires
}

# Dans fig.update_layout()
dragmode="pan",                      # Mode déplacement par défaut
uirevision="constant",               # Conservation du zoom/position
fixedrange=False,                    # Zoom/pan autorisé sur X et Y
showlegend=False,                    # Légende désactivée
margin=dict(b=20, l=20, r=20, t=60), # Marges réduites
```

### 🚀 Utilisation Optimale

1. **Exploration initiale** : Utilisez la molette pour avoir une vue d'ensemble
2. **Mode plein écran** : Cliquez sur l'icône plein écran pour une immersion totale
3. **Analyse détaillée** : Zoomez sur une communauté spécifique
4. **Navigation fluide** : Déplacez-vous en cliquant-glissant
5. **Stabilité** : Votre vue reste fixe pendant les mises à jour automatiques

### 💡 Astuces

- **Zoom rapide** : Utilisez Ctrl + Molette (Windows) ou Cmd + Trackpad (Mac) pour zoomer plus vite
- **Centrer sur une personne** : Utilisez le dropdown "Centrer sur" dans la sidebar
- **Export** : Pour sauvegarder votre vue actuelle, utilisez le bouton d'export en haute résolution
- **Reset complet** : Cliquez sur "🏠" dans la barre d'outils pour revenir à la vue initiale
- **Plein écran** : Parfait pour les présentations ou l'analyse approfondie
- **Échap** : Pour quitter le mode plein écran rapidement

## 🎯 Comparaison Avant/Après

| Fonctionnalité | Avant ❌ | Après ✅ |
|----------------|---------|---------|
| Zoom avec molette | Non | **Oui** |
| Conservation du zoom | Reset auto | **Persistant** |
| Mode déplacement | Sélection manuelle | **Par défaut** |
| Double-clic | Reset vue | **Désactivé** |
| Barre d'outils | Cachée | **Visible** |
| Légende communautés | Visible | **Masquée (+ d'espace)** |
| Plein écran | Non | **Oui** |
| Marges | Larges | **Optimisées** |
| Navigation fluide | Basique | **Professionnelle** |

## 📐 Gain d'espace

- **Avant** : Marge droite de 200px pour la légende
- **Après** : Marge droite de 20px
- **Gain** : **~180px de largeur supplémentaire** pour afficher le graphe !

---

**Dernière mise à jour** : 10 octobre 2025
**Version** : 2.1

