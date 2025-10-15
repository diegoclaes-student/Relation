# 🔄 Scripts de Symétrisation des Relations

## 📋 Vue d'ensemble

Deux scripts sont disponibles pour gérer les relations asymétriques dans la base de données :

1. **`check_asymmetric_relations.py`** : Détecte et affiche les relations asymétriques
2. **`symmetrize_all_relations.py`** : Corrige automatiquement les relations asymétriques

---

## 🔍 1. Vérifier les relations asymétriques

### Utilisation :
```bash
python check_asymmetric_relations.py
```

### Résultat :
- Affiche toutes les paires de relations asymétriques
- Statistiques détaillées (nombre de personnes, relations, taux de symétrie)
- Recommandations pour corriger

### Exemple de sortie :
```
🔍 DÉTECTION DES RELATIONS ASYMÉTRIQUES
========================================

⚠️  94 relation(s) asymétrique(s) détectée(s):

1. 👨 Diego → 👩 Lola T
   └─ Manque: 👩 Lola T → 👨 Diego

2. 👩 Isaline D → 👨 Guillaume G
   └─ Manque: 👨 Guillaume G → 👩 Isaline D

📊 STATISTIQUES:
   • Total personnes: 85
   • Total relations: 95
   • Relations asymétriques: 94
   • Taux de symétrie: 1.1%
```

---

## 🔧 2. Symétriser automatiquement

### Mode simulation (recommandé en premier) :
```bash
python symmetrize_all_relations.py
```

Cette commande **n'applique AUCUNE modification** mais affiche ce qui serait fait.

### Mode application (modifie la base de données) :
```bash
python symmetrize_all_relations.py --apply
```

⚠️ **ATTENTION** : Cette commande modifie réellement la base de données !

---

## 📊 Que fait le script de symétrisation ?

### Principe :
Pour chaque relation `A → B` qui existe, si `B → A` n'existe pas, le script ajoute automatiquement `B → A` avec le même type de relation.

### Exemple :
**AVANT** :
- Diego → Lola T (type: 0)

**APRÈS** :
- Diego → Lola T (type: 0)
- Lola T → Diego (type: 0)  ← **Ajouté automatiquement**

---

## 🔒 Sécurité

### Mode simulation (dry run) :
- ✅ Aucune modification de la base de données
- ✅ Affiche ce qui serait modifié
- ✅ Recommandé pour vérifier avant d'appliquer

### Mode application :
- ⚠️ Modifie la base de données
- ⚠️ Ajoute les relations inverses
- ⚠️ **Créez une sauvegarde avant !**

---

## 📝 Workflow recommandé

### Étape 1 : Vérification
```bash
# Voir les relations asymétriques
python check_asymmetric_relations.py
```

### Étape 2 : Sauvegarde (important !)
```bash
# Sauvegarder la base de données
cp relations.db relations.db.backup
```

### Étape 3 : Simulation
```bash
# Voir ce qui serait modifié
python symmetrize_all_relations.py
```

### Étape 4 : Application
```bash
# Appliquer les modifications
python symmetrize_all_relations.py --apply
```

### Étape 5 : Vérification finale
```bash
# Vérifier que tout est symétrique
python check_asymmetric_relations.py
```

---

## 📈 Statistiques attendues

### Avant symétrisation :
- Relations : 95
- Relations asymétriques : 94
- Taux de symétrie : 1.1%

### Après symétrisation :
- Relations : 189 (95 + 94)
- Relations asymétriques : 0
- Taux de symétrie : 100%

---

## ❓ FAQ

### Q: Puis-je annuler les modifications ?
**R:** Oui, si vous avez fait une sauvegarde :
```bash
cp relations.db.backup relations.db
```

### Q: Que se passe-t-il si je relance le script ?
**R:** Le script détecte les relations déjà existantes et ne les ajoute pas en double.

### Q: Le type de relation est-il préservé ?
**R:** Oui, la relation inverse aura exactement le même type que la relation originale.

### Q: Puis-je voir toutes les relations qui seront ajoutées ?
**R:** Oui, exécutez le script sans `--apply`. Il affiche les 10 premières + un compteur du reste.

---

## 🐛 Dépannage

### Erreur "ModuleNotFoundError: No module named 'networkx'"
```bash
# Installer les dépendances
pip install -r requirements.txt
```

### Le script ne trouve pas la base de données
```bash
# Vérifier le chemin
ls -la relations.db

# Le script cherche dans le répertoire courant
cd /Users/diegoclaes/Code/Relation
python symmetrize_all_relations.py
```

---

## 📊 Exemple complet

```bash
# 1. Vérification initiale
$ python check_asymmetric_relations.py
⚠️  94 relation(s) asymétrique(s) détectée(s)
Taux de symétrie: 1.1%

# 2. Sauvegarde
$ cp relations.db relations.db.backup

# 3. Simulation
$ python symmetrize_all_relations.py
📋 94 relation(s) inverse(s) à ajouter
💡 Pour appliquer: python symmetrize_all_relations.py --apply

# 4. Application
$ python symmetrize_all_relations.py --apply
⏳ Application des modifications...
✅ 94 relation(s) inverse(s) ajoutée(s) avec succès !
Taux de symétrie: 100%

# 5. Vérification
$ python check_asymmetric_relations.py
✅ Aucune relation asymétrique détectée !
```

---

## 🎯 Recommandation finale

Pour un réseau social où "A a pécho B" signifie généralement une relation mutuelle, **il est fortement recommandé de symétriser toutes les relations** pour avoir un graphe cohérent et des prédictions plus précises.

Exécutez :
```bash
python symmetrize_all_relations.py --apply
```

Une fois les relations symétriques, les prédictions de genre et les suggestions de nouvelles relations seront beaucoup plus précises ! 🎉
