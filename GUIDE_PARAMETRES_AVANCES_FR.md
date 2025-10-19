# ⚙️ Menu Hamburger - Paramètres Avancés

## Nouvelle Section: ⚙️ Paramètres

Dans le menu hamburger, vous trouverez maintenant une nouvelle section "⚙️ Paramètres" avec 4 contrôles avancés pour customiser la visualisation du graphe.

---

## 1️⃣ 🔍 Chercher une Personne

### Qu'est-ce que c'est?
Un champ de recherche pour trouver rapidement une personne dans le réseau et centr le graphe sur elle.

### Comment l'utiliser?
1. **Cliquez sur le dropdown** "🔍 Chercher une personne"
2. **Tapez le nom** de la personne que vous cherchez
3. **Sélectionnez-la** dans la liste
4. **Le graphe se centrera et zoomera** automatiquement sur cette personne!

### Exemple
```
Vous tapez "Alice"
↓
Le dropdown affiche:
  - Alice H
  - Alice L
↓
Vous cliquez sur "Alice H"
↓
Le graphe se recentre et zoom sur Alice H
et affiche ses connexions clairement
```

### Cas d'usage
- **Chercher une personne spécifique** et voir son réseau
- **Comprendre la position** d'une personne dans le groupe
- **Analyser les connexions** directes et indirectes

### Conseil
- ✅ Parfait avec le mode **🎯 Radial** pour voir son réseau personnel
- ✅ Parfait avec le mode **⭕ Circulaire** pour voir sa place dans le groupe

---

## 2️⃣ 📊 Taille des Bulles

### Qu'est-ce que c'est?
Un slider pour contrôler la taille des nœuds (bulles représentant les personnes).

### Plage
- **Min:** 5 (très petites)
- **Max:** 30 (très grandes)
- **Défaut:** 15 (normal)

### Comment l'utiliser?
1. **Déplacez le slider** vers la gauche (plus petit) ou la droite (plus grand)
2. **Les bulles changent de taille instantanément**
3. **La lisibilité s'adapte** selon votre préférence

### Cas d'usage

**Diminuer la taille (< 15):**
- ✅ Graphes avec beaucoup de personnes (80+ personnes)
- ✅ Voir le graphe complet en une fois
- ✅ Vue globale du réseau

**Augmenter la taille (> 15):**
- ✅ Graphes plus petits (< 30 personnes)
- ✅ Mieux lire les noms
- ✅ Voir les détails clairement

### Exemple
```
Taille 5:  ●●●●● (Très dense, complet)
Taille 15: ●  ●  ●  (Normal, équilibré)
Taille 30: ●     ●     ● (Spacieux, lisible)
```

---

## 3️⃣ 📏 Distance / Répulsion

### Qu'est-ce que c'est?
Contrôle la distance entre les nœuds. Plus la répulsion est forte, plus les nœuds s'écartent.

### Plage
- **Min:** 0.5 (très proche)
- **Max:** 3.0 (très écartés)
- **Défaut:** 1.0 (normal)

### Comment l'utiliser?
1. **Déplacez le slider** vers la gauche (rapprocher) ou la droite (écarter)
2. **Les nœuds se réarrangent** immédiatement
3. **L'espacement change** selon votre préférence

### Cas d'usage

**Diminuer la répulsion (< 1.0):**
- ✅ Graphes grands avec peu de nœuds
- ✅ Voir les connexions lointaines
- ✅ Vue compacte

**Augmenter la répulsion (> 1.0):**
- ✅ Mieux voir chaque nœud séparément
- ✅ Moins de chevauchements
- ✅ Plus claire sur le rôle de chaque personne

### Lien avec les Modes
- **Force-Directed:** La répulsion a un grand effet
- **Circulaire:** La répulsion a peu d'effet (déjà organisé)
- **Hiérarchique:** La répulsion maintient les niveaux

### Conseil
```
Si le graphe est:
  - Trop dense → Augmentez la répulsion (>1.5)
  - Trop éclaté → Diminuez la répulsion (<0.7)
```

---

## 4️⃣ ⚡ Force Anti-Croisement

### Qu'est-ce que c'est?
Contrôle la force qui essaie d'éviter les croisements des liens. Les liens sont les arêtes reliant les nœuds.

### Plage
- **Faible (0.0):** Les liens peuvent se croiser (plus rapide)
- **Moyen (0.5):** Équilibre entre clarté et performance
- **Fort (1.0):** Minimise les croisements (peut être lent)

### Comment l'utiliser?
1. **Déplacez le slider** entre "Faible", "Moyen", et "Fort"
2. **Les liens se réarrangent** pour minimiser les croisements
3. **La clarté s'améliore** (mais peut prendre plus de temps)

### Cas d'usage

**Faible (0.0):**
- ✅ Graphes très grands (>200 nœuds)
- ✅ Performance prioritaire
- ✅ Croisements acceptables

**Moyen (0.5):**
- ✅ Graphe standard (80-100 nœuds)
- ✅ Bon équilibre
- ✅ Recommandé par défaut

**Fort (1.0):**
- ✅ Petits graphes (< 50 nœuds)
- ✅ Clarté maximale
- ✅ Pas besoin de performance

### Exemple Visuel
```
Faible (0.0):        Moyen (0.5):         Fort (1.0):
  ●─────●               ●                    ●
  │   ╱ │               │╲                   │ ╲
  │ ╱   │               │ ╲                  │  ╲
  ●─────●               ●  ●                ●   ●
  │╲    │               │  │                 │   │
  │ ╲   │               │  │                 │   │
  ●─────●               ●  ●                 ●   ●

Beaucoup de           Équilibre            Très clair
croisements           bon
```

---

## 📋 Comment Combiner les Paramètres

### Scénario 1: Vue Globale d'un Grand Réseau
```
Mode:                ⭕ Circulaire
Taille bulles:       10 (petites)
Distance:            2.0 (très écartées)
Anti-croisement:     Faible (performance)
```

### Scénario 2: Étude Détaillée d'un Petit Groupe
```
Mode:                🌳 Hiérarchique
Taille bulles:       25 (grandes)
Distance:            1.0 (normal)
Anti-croisement:     Fort (très clair)
```

### Scénario 3: Analyse d'une Personne
```
Mode:                🎯 Radial
Taille bulles:       18 (moyen)
Distance:            1.5 (modéré)
Anti-croisement:     Moyen (bon équilibre)
Chercher:            [La personne cible]
```

### Scénario 4: Présentation/Partage
```
Mode:                🔀 Force-Directed
Taille bulles:       20 (lisible)
Distance:            1.2 (harmonieux)
Anti-croisement:     Moyen (esthétique)
```

---

## 🎯 Conseils Pratiques

### Conseil 1: Testez!
- N'hésitez pas à bouger les sliders
- Chaque combinaison revèle quelque chose de nouveau
- Pas d'effet permanent (vous pouvez revenir en arrière)

### Conseil 2: Combinaison Mode + Paramètres
- Le **Mode** change la structure du graphe
- Les **Paramètres** affinent la visualisation du mode choisi
- Toujours tester ensemble pour meilleur résultat

### Conseil 3: Performance
- Petit graphe (< 50 nodes) → Anti-croisement Fort
- Graphe moyen (50-100 nodes) → Anti-croisement Moyen
- Grand graphe (> 100 nodes) → Anti-croisement Faible

### Conseil 4: Lecture
- Augmentez taille bulles + augmentez distance = Plus lisible
- Diminuez taille bulles + diminuez distance = Plus compact

---

## ⌨️ Raccourcis/Astuces

### Conseil 5: Réinitialisation
- Diminuez tous les sliders au minimum → Vue compacte
- Augmentez tous les sliders au maximum → Vue expansive
- Réinitialiser le navigateur → Valeurs par défaut

### Conseil 6: Recherche Rapide
- Cliquez le dropdown de recherche
- Commencez à taper (ex: "Al" pour Alice)
- Sélectionnez et le graphe se centre!

### Conseil 7: Export/Screenshot
- Réglez les paramètres pour la meilleure vue
- Prenez un screenshot avec Print Screen
- Parfait pour documents/présentations

---

## 🔧 Valeurs Recommandées par Défaut

| Paramètre | Valeur | Raison |
|-----------|--------|--------|
| Taille bulles | 15 | Lisible pour 80 personnes |
| Distance | 1.0 | Équilibre naturel |
| Anti-croisement | 0.5 | Bon compromis |
| Recherche | Vide | Vue complète |

---

## 📱 Sur Mobile

Tous les paramètres fonctionnent sur mobile:
- ✅ Sliders tactiles (défilement)
- ✅ Dropdown de recherche (scroll)
- ✅ Mise à jour en temps réel
- ✅ Zoom pinch-to-zoom compatible

---

## ⚠️ Problèmes et Solutions

**Q: Les changements ne s'appliquent pas?**  
A: Attendez 1-2 secondes. Le graphe se recalcule. Vérifiez la console navigateur.

**Q: Le graphe devient lent?**  
A: Diminuez "Anti-croisement" à "Faible" et réduisez la taille des bulles.

**Q: Je ne vois pas les noms dans la recherche?**  
A: Cliquez d'abord sur le dropdown, puis tapez pour filtrer.

**Q: Comment revenir aux paramètres par défaut?**  
A: Rechargez la page avec F5, ou réinitialisez chaque slider à sa valeur de base.

---

## ✨ Résumé Rapide

| Paramètre | Utilité | Min | Max | Défaut |
|-----------|---------|-----|-----|--------|
| 🔍 Recherche | Centrer sur une personne | N/A | N/A | - |
| 📊 Taille | Taille des nœuds | 5 | 30 | 15 |
| 📏 Distance | Écartement des nœuds | 0.5 | 3.0 | 1.0 |
| ⚡ Anti-croisement | Clarté des liens | Faible | Fort | Moyen |

---

**Ces paramètres vous donnent un contrôle total sur la visualisation de votre réseau social! 🚀**
