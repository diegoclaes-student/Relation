# 🎨 Guide Utilisateur - Modes de Visualisation

## Accéder aux Modes de Visualisation

### Étape 1: Ouvrir le Menu
Cliquez sur le **☰ menu hamburger** dans le coin **supérieur droit** de l'écran du graphe.

```
┌─────────────────────────────────┐
│  CENTRALE POTINS MAPS       ☰   │ ← Cliquez ici
├─────────────────────────────────┤
│                                 │
│     [Graphe interactif]         │
│     85 personnes, 93 relations  │
│                                 │
└─────────────────────────────────┘
```

### Étape 2: Sélectionner un Mode
Le menu déroulant s'affiche avec la liste des modes disponibles:

```
🎨 Mode de Visualisation
┌─────────────────────────────────┐
│ 🌐 Communautés       [DEFAULT]  │
│ ⭕ Circulaire                   │
│ 🌳 Hiérarchique                 │
│ 🎯 Radial                       │
│ 🔀 Force-Directed               │
│ 📊 Kamada-Kawai                 │
│ ✨ Spectral                     │
└─────────────────────────────────┘
```

### Étape 3: Le Graphe se Met à Jour
Le graphe se redessine automatiquement avec le nouveau mode choisi!

---

## Les 7 Modes Expliqués

### 🌐 Communautés (Défaut)

**Qu'est-ce que c'est?**
- Les personnes sont groupées par "communautés" (clusters naturels)
- Utilise un algorithme de détection de communautés (Greedy Modularity)

**À quoi ça ressemble?**
```
    [groupe1]              [groupe2]
    ●─●─●───             ●─●─●
    │ │ │                │ │
    ●─●─●───●──────────●─●─●
          │                │
        [groupe3]        [groupe4]
```

**Quand l'utiliser?**
- Pour comprendre les **groupes d'amis naturels**
- Pour voir quelles personnes forment des **cliques**
- Pour analyser les **divisions sociales**

---

### ⭕ Circulaire

**Qu'est-ce que c'est?**
- Toutes les personnes sont arrangées en **cercle**
- Les relations sont visibles comme des **lignes reliant le centre**

**À quoi ça ressemble?**
```
         ●
        / \
       /   \
      ●     ●
     / \   / \
    ●   ● ●   ●
    |   |/\   |
    ●   ●  ●  ●
     \ /    \ /
      ●      ●
       \    /
        ●──●
        
Tout le monde est sur le cercle,
les liens croisent le centre
```

**Quand l'utiliser?**
- ✅ **C'est ce que tu as demandé!** "toute les bulles en rond"
- Pour voir **toutes les connexions d'une personne** rapidement
- Pour les **présentations** ou **affichage public**
- Pour identifier les **personnes centrales** (beaucoup de lignes)

---

### 🌳 Hiérarchique

**Qu'est-ce que c'est?**
- Les personnes sont organisées par **niveau de connectivité**
- Centre = personnes très populaires (beaucoup d'amis)
- Extérieur = personnes moins connectées

**À quoi ça ressemble?**
```
                 ●           ← Super connectées
                /|\
               ● ● ●         ← Très connectées
              /|   |\
             ● ● ● ● ●       ← Moyennement connectées
            /  |   |  \
           ●   ●───●   ●    ← Peu connectées (périphérie)
```

**Quand l'utiliser?**
- Pour voir qui sont les **personnes clés** du réseau
- Pour comprendre la **structure hiérarchique**
- Pour identifier les **influenceurs** ou **connecteurs**

---

### 🎯 Radial

**Qu'est-ce que c'est?**
- **Une personne au centre** (celle avec le plus d'amis)
- **Ses amis directs** en première couronne
- **Les autres** en deuxième couronne

**À quoi ça ressemble?**
```
         ●───●
        /|   |\
       ● ●   ● ●
       | |   | |
    ●─●─●   ●─●─●
       | |   | |
       ● ●   ● ●
        \|   |/
         ●───●
         
    [Personne centrale]
    entourée de ses amis directs
```

**Quand l'utiliser?**
- Pour analyser le **réseau d'une personne spécifique**
- Pour voir ses **amis directs** vs **amis d'amis**
- Pour comprendre la **position de quelqu'un** dans le groupe

---

### 🔀 Force-Directed

**Qu'est-ce que c'est?**
- Simule des **forces physiques**: attraction et répulsion
- Les nodes connectés se rapprochent naturellement
- Les nodes non connectés se repoussent

**À quoi ça ressemble?**
```
    ●━━●
    ┃  ┃
    ●━━●    ← Groupes naturels qui se forment
    ┃
    ●    (espace)    ●─●
                     ┃ ┃
                     ●─●
```

**Quand l'utiliser?**
- Pour une **exploration intuitive** du réseau
- C'est le mode le plus **esthétique**
- Pour voir les **clusters naturels** sans intervention

---

### 📊 Kamada-Kawai

**Qu'est-ce que c'est?**
- Version améliorée du Force-Directed
- Minimise l'énergie globale du système
- Produit des layouts plus **lisses et réguliers**

**À quoi ça ressemble?**
```
Similaire à Force-Directed mais plus "équilibré"
```

**Quand l'utiliser?**
- Pour les **publications** ou **rapports professionnels**
- Quand tu veux un résultat **très esthétique**
- Pour des **présentations formelles**

---

### ✨ Spectral

**Qu'est-ce que c'est?**
- Utilise les **valeurs propres** (eigenvectors) de la matrice du graphe
- Approche **mathématique** et **déterministe**
- Toujours le même résultat (pas d'aléatoire)

**À quoi ça ressemble?**
```
Résultat très organisé et prévisible
```

**Quand l'utiliser?**
- Pour l'**analyse académique**
- Quand tu as besoin d'un résultat **reproductible**
- Pour les **comparaisons** entre différentes exécutions

---

## Conseils Pratiques

### 💡 Astuce 1: Explorer Tous les Modes
Ne reste pas sur un seul mode! Chaque mode révèle des aspects différents du réseau.

### 💡 Astuce 2: Combiner avec le Zoom
- Utilise le **zoom** (boutons +/-) ou **pinch-to-zoom** sur mobile
- Parfait pour explorer des zones spécifiques du graphe

### 💡 Astuce 3: Mode pour Chaque Question
- "Qui sont les gens importants?" → **Hiérarchique**
- "Quels sont les groupes?" → **Communautés**
- "Comment est connectée [personne]?" → **Radial** (+ zoom)
- "Belle visualisation?" → **Force-Directed** ou **Kamada-Kawai**
- "Voir tout clairement?" → **Circulaire**

### 💡 Astuce 4: Sur Mobile
Le menu fonctionne aussi sur mobile! Ouvre le menu, sélectionne le mode, et utilise tes deux doigts pour zoomer.

---

## Problèmes et Solutions

**Q: Le graphe ne change pas après avoir sélectionné un mode?**  
A: Attends quelques secondes (les grands réseaux prennent du temps à calculer). Si rien ne change, essaie de recharger la page.

**Q: Certain mode ne fonctionne pas?**  
A: Essaie un autre mode ou recharge la page. Si ça persiste, c'est peut-être un problème technique.

**Q: Comment revenir au mode par défaut?**  
A: Sélectionne "🌐 Communautés" dans le dropdown.

---

## Résumé Rapide

| Mode | Meilleur Pour | Emoji |
|------|---------------|-------|
| Communautés | Voir les groupes naturels | 🌐 |
| Circulaire | Vue circulaire (ta demande!) | ⭕ |
| Hiérarchique | Voir la hiérarchie/importance | 🌳 |
| Radial | Analyser une personne | 🎯 |
| Force-Directed | Beau et intuitif | 🔀 |
| Kamada-Kawai | Très esthétique | 📊 |
| Spectral | Analyse mathématique | ✨ |

---

**Bonne exploration! 🚀**
