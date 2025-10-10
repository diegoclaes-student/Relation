# Graphe social interactif (NetworkX + Plotly)

Ce projet affiche un **graphe social orienté** à partir d'une liste de relations du type « A a pécho B ».

- Un **nœud** = une personne
- Une **flèche A → B** = "A a pécho B"
- La **taille** et la **couleur** des nœuds dépendent du **degré total** (entrants + sortants)
- Rendu **interactif** (zoom, pan, hover)
- Génère un fichier **graph.html** autonome

## Prérequis

- Python 3.9+
- Dépendances Python:

```
pip install -r requirements.txt
```

## Exécution

### Avec un fichier texte (recommandé)

Format attendu par ligne: `A: B, C, D` qui signifie « A a pécho B, C, D ».

Exemple (`relations.txt`):

```
A: B, C, D
B: A, X, Y
C: D
D: B
X: A
Y: C
```

Lancer le script:

```
python3 graph.py --input relations.txt --output graph.html
```

- Le script écrit un fichier `graph.html` autonome, et tente d'ouvrir une fenêtre d'affichage.
- Si l'ouverture ne fonctionne pas (environnement sans GUI), ouvrez `graph.html` dans votre navigateur.

Règles de parsing:
- Lignes vides ou commençant par `#` ignorées
- Espaces tolérés autour des virgules et des `:`
- Dédoublonnage des cibles par source
- Auto-boucles ignorées (ex: `A: A`)

Si `--input` est omis, le script essaie `relations.txt` à la racine. En cas d'absence ou de fichier vide/invalide, il bascule sur des relations par défaut.

### Sans fichier (défaut intégré)

```
python3 graph.py
```

Dans ce cas, les relations par défaut codées dans `graph.py` (fonction `default_relations`) sont utilisées.
