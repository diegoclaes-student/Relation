# 🌐 Social Network Analyzer - Guide Complet

## 📋 Table des Matières
- [Vue d'ensemble](#vue-densemble)
- [Nouvelles Fonctionnalités](#nouvelles-fonctionnalités)
- [Utilisation](#utilisation)
- [Panel Admin](#panel-admin)
- [Symétrie Automatique](#symétrie-automatique)

---

## 🎯 Vue d'ensemble

Application web interactive pour visualiser et gérer un réseau social de relations avec :
- **Visualisation graphique** du réseau avec différents layouts
- **Propositions de relations** par les utilisateurs
- **Panel administrateur** pour gérer toutes les relations
- **Symétrie automatique** de toutes les relations

---

## ✨ Nouvelles Fonctionnalités

### 1. **Bouton "Proposer une relation"**
- ➕ Accessible à tous les utilisateurs
- Permet de suggérer de nouvelles relations
- Les propositions sont envoyées en attente d'approbation
- **Symétrie automatique** : Quand une relation est approuvée, la relation inverse est créée automatiquement

### 2. **Panel Admin Complet**
Accessible via le bouton "🔐 Admin Panel" avec les identifiants :
- **Username**: `admin`
- **Password**: `admin123`

#### Fonctionnalités du panel admin :

**📬 Onglet Propositions**
- Liste de toutes les propositions en attente
- Affiche : personnes, type de relation, auteur, date, notes
- Actions :
  - ✅ **Approuver** : Ajoute la relation ET sa relation inverse automatiquement
  - ❌ **Rejeter** : Supprime la proposition

**📝 Onglet Gérer Relations**
- Vue de toutes les relations existantes groupées par personne
- 🗑️ **Supprimer** : Supprime la relation ET sa relation inverse automatiquement
- Affiche jusqu'à 20 personnes pour la performance

**➕ Onglet Ajouter**
- Ajouter directement une relation sans passer par les propositions
- Options :
  - Sélectionner Personne 1 et Personne 2
  - Choisir le type de relation
  - ✅ **Option "Créer aussi la relation inverse"** (cochée par défaut)
- Permet d'ajouter des relations unidirectionnelles si nécessaire

**📜 Onglet Historique**
- Journal de toutes les actions effectuées
- Affiche : type d'action, personnes concernées, auteur, date, détails
- Actions tracées : ADD, DELETE, APPROVE, REJECT, UPDATE

---

## 🚀 Utilisation

### Démarrage de l'application

```bash
python app_full.py
```

L'application sera disponible sur : **http://localhost:8051**

### Pour les utilisateurs

1. **Visualiser le réseau**
   - Utilisez le dropdown "Layout Algorithm" pour changer la disposition
   - Zoomez et naviguez dans le graphe
   - Survolez les nœuds pour voir les informations détaillées

2. **Proposer une nouvelle relation**
   - Cliquez sur "➕ Proposer une relation"
   - Sélectionnez les deux personnes
   - Choisissez le type de relation
   - Ajoutez des notes optionnelles
   - Cliquez sur "Envoyer"
   - ✨ **La relation sera automatiquement bidirectionnelle après approbation**

### Pour les administrateurs

1. **Se connecter**
   - Cliquez sur "🔐 Admin Panel"
   - Entrez : `admin` / `admin123`

2. **Approuver des propositions**
   - Onglet "📬 Propositions"
   - Cliquez sur ✅ pour approuver (crée automatiquement les deux directions)
   - Cliquez sur ❌ pour rejeter

3. **Gérer les relations existantes**
   - Onglet "📝 Gérer Relations"
   - Cliquez sur 🗑️ pour supprimer (supprime automatiquement les deux directions)

4. **Ajouter directement**
   - Onglet "➕ Ajouter"
   - Remplissez le formulaire
   - Cochez/décochez "Créer aussi la relation inverse"
   - Cliquez sur "Ajouter la relation"

5. **Consulter l'historique**
   - Onglet "📜 Historique"
   - Voir toutes les modifications avec horodatage

---

## 🔄 Symétrie Automatique

### Principe

Toutes les relations sont **bidirectionnelles** par défaut :
- Si A → B, alors B → A est créé automatiquement
- Garantit la cohérence du réseau
- Reflète la nature réciproque des relations sociales

### Comment ça fonctionne

1. **Lors des propositions**
   - L'utilisateur propose : Diego → Lola
   - Après approbation, le système crée :
     - Diego → Lola
     - Lola → Diego

2. **Lors de l'ajout direct (admin)**
   - Option cochée par défaut
   - Peut être décochée si besoin d'une relation unidirectionnelle

3. **Lors de la suppression**
   - Supprimer Diego → Lola supprime aussi Lola → Diego
   - Évite les relations orphelines

### Vérification

Utilisez le script de vérification :

```bash
python check_asymmetric_relations.py
```

Doit afficher : **"Taux de symétrie : 100%"**

---

## 📊 Types de Relations

| Code | Type | Description |
|------|------|-------------|
| 0 | Bisous | Relation simple |
| 1 | Dodo ensemble | Relation intermédiaire |
| 2 | Baise | Relation intime |
| 3 | Couple | Relation officielle |

---

## 🗃️ Structure de la Base de Données

### Tables principales

**`relations`** : Relations approuvées
- `person1`, `person2` : Nom des personnes
- `relation_type` : Type de relation (0-3)
- `approved_by` : Administrateur qui a approuvé
- `approved_at` : Date d'approbation

**`pending_relations`** : Propositions en attente
- `person1`, `person2` : Nom des personnes
- `relation_type` : Type proposé
- `submitted_by` : Auteur de la proposition
- `submitted_at` : Date de soumission
- `notes` : Notes optionnelles

**`history`** : Historique des actions
- `action_type` : ADD, DELETE, APPROVE, REJECT, UPDATE
- `person1`, `person2` : Personnes concernées
- `performed_by` : Auteur de l'action
- `created_at` : Date de l'action
- `details` : Informations supplémentaires

**`admins`** : Comptes administrateurs
- `username` : Nom d'utilisateur
- `password_hash` : Hash SHA256 du mot de passe

---

## 🔧 Maintenance

### Créer un nouvel administrateur

```python
from database import RelationDB
db = RelationDB()
db.add_admin("nouveau_admin", "mot_de_passe")
```

### Backup de la base de données

```bash
cp relations.db relations.db.backup_$(date +%Y%m%d_%H%M%S)
```

### Symétriser manuellement toutes les relations

```bash
python symmetrize_all_relations.py --apply
```

---

## 📈 Statistiques

Visibles en temps réel dans le panneau de droite :
- **Persons** : Nombre total de personnes
- **Relations** : Nombre total de relations (doit être pair si symétrique)
- **Pending** : Nombre de propositions en attente (badge rouge si > 0)

---

## 🎨 Personnalisation

### Modifier les types de relations

Éditez `database.py` :

```python
RELATION_TYPES = {
    0: "Bisous",
    1: "Dodo ensemble",
    2: "Baise",
    3: "Couple",
    4: "Nouveau Type"  # Ajoutez vos types
}
```

### Changer les couleurs du thème

Modifiez le CSS dans `app_full.py`, section `app.index_string`

---

## 🐛 Dépannage

### Les propositions ne s'affichent pas
- Vérifiez que vous êtes connecté en tant qu'admin
- Rechargez la page

### La symétrie ne fonctionne pas
- Vérifiez les logs dans le terminal
- Utilisez `check_asymmetric_relations.py` pour diagnostiquer

### Erreur de connexion admin
- Vérifiez les identifiants : `admin` / `admin123`
- Le mot de passe est sensible à la casse

---

## 📝 Changelog

### Version 2.0 (Actuelle)
- ➕ Système de propositions utilisateurs
- 🔐 Panel administrateur complet
- 🔄 Symétrie automatique des relations
- 📜 Historique des actions
- ✅ Approbation/Rejet des propositions
- 🗑️ Suppression symétrique

### Version 1.0
- Visualisation du graphe
- Layouts multiples
- Détection de genre
- Prédictions de relations

---

## 🤝 Contribution

Pour ajouter des fonctionnalités :
1. Modifiez `database.py` pour les opérations DB
2. Ajoutez les composants UI dans `admin_components.py`
3. Créez les callbacks dans `app_full.py`
4. Testez avec `python app_full.py`

---

## 📄 Licence

Usage interne - Projet éducatif

---

**Enjoy managing your social network! 🎉**
