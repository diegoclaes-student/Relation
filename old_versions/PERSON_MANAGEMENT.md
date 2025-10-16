# 👥 Gestion des Personnes - Documentation

## Vue d'ensemble

Le système de gestion des personnes permet d'enrichir les données du graphe social avec des métadonnées sur chaque personne et de maintenir la qualité des données.

## Nouvelles fonctionnalités

### 1. 📊 Table Persons dans la base de données

**Structure de la table :**
- `id` : Identifiant unique
- `name` : Nom de la personne (UNIQUE)
- `gender` : Genre (M/F/?)
- `sexual_orientation` : Orientation sexuelle (straight/gay/lesbian/bi/?)
- `created_at` : Date de création
- `updated_at` : Date de dernière modification

**Migration automatique :**
- Script `migrate_persons.py` pour peupler la table avec toutes les personnes existantes
- Toutes les 84 personnes du graphe ont été migrées

### 2. ✏️ Modifier une personne

**Fonctionnalités :**
- ✏️ **Renommer** : Change le nom avec mise à jour CASCADE sur toutes les relations
- 👤 **Genre** : Homme (M) / Femme (F) / Non spécifié (?)
- 💜 **Orientation** : Hétéro / Gay / Lesbienne / Bisexuel(le) / Non spécifié

**Comment faire :**
1. Ouvrir le panel Admin
2. Aller dans l'onglet "👥 Gérer Personnes"
3. Cliquer sur "✏️ Modifier" à côté de la personne
4. Modifier les informations
5. Cliquer sur "💾 Enregistrer"

**Sécurité :**
- Le renommage met à jour automatiquement `person1` et `person2` dans toutes les tables (relations, pending_relations)
- Impossible de renommer vers un nom déjà existant (protection contre les doublons)

### 3. 🔀 Fusionner des personnes

**Usage :**
Utilisé pour corriger les doublons créés par erreur (ex: "Diego" et "Diego C" sont la même personne)

**Processus :**
1. Sélectionner la personne à fusionner (doublon)
2. Choisir la personne principale (celle à conserver)
3. Le système :
   - Transfère toutes les relations du doublon vers la personne principale
   - Évite les doublons de relations (grâce à la contrainte UNIQUE)
   - Supprime le doublon de pending_relations
   - Supprime le doublon de la table persons

**Comment faire :**
1. Panel Admin → "👥 Gérer Personnes"
2. Cliquer sur "🔀 Fusionner" à côté du doublon
3. Sélectionner la personne principale
4. Confirmer avec "🔀 Fusionner"

**Exemple :**
```
Avant :
- Diego : 5 relations
- Diego C : 3 relations

Après fusion (Diego C → Diego) :
- Diego : 8 relations (doublons automatiquement évités)
- Diego C : supprimé
```

### 4. 🗑️ Supprimer une personne

**Action :**
Supprime complètement une personne du système avec toutes ses relations.

**Impact :**
- Supprime toutes les relations où la personne apparaît (person1 ou person2)
- Supprime de pending_relations
- Supprime de la table persons
- **ATTENTION : Action irréversible**

### 5. 👥 Nouvel onglet "Gérer Personnes"

**Interface :**
- Liste de toutes les personnes avec :
  - Icône genre (👨/👩/❓)
  - Nom de la personne
  - Genre et orientation sexuelle
  - 3 boutons d'action : Modifier / Fusionner / Supprimer

**Affichage :**
- 30 premières personnes par défaut (pour performance)
- Scrollable pour voir tout le contenu

## Méthodes de database.py

### `add_person(name, gender, sexual_orientation)`
Ajoute une nouvelle personne dans la table.

### `get_all_persons_detailed()`
Récupère toutes les personnes avec leurs informations complètes.

### `update_person_info(name, gender, sexual_orientation, updated_by)`
Met à jour les informations d'une personne (crée la personne si elle n'existe pas).

### `rename_person(old_name, new_name, updated_by)`
Renomme une personne avec CASCADE sur toutes les relations.
- Met à jour `persons.name`
- Met à jour `relations.person1` et `relations.person2`
- Met à jour `pending_relations.person1` et `pending_relations.person2`

### `merge_persons(primary_name, duplicate_name, updated_by)`
Fusionne deux personnes :
1. Transfère toutes les relations du doublon vers le principal
2. Supprime les anciennes relations du doublon
3. Supprime le doublon de pending_relations
4. Supprime le doublon de persons

### `delete_person(name, deleted_by)`
Supprime une personne et toutes ses relations.

## Historique

Toutes les actions sont enregistrées dans la table `history` :
- `ADD_PERSON` : Ajout d'une personne
- `UPDATE_PERSON` : Modification des informations
- `RENAME_PERSON` : Renommage (avec old_name → new_name)
- `MERGE_PERSONS` : Fusion (duplicate → primary)
- `DELETE_PERSON` : Suppression

## Utilisation recommandée

### Workflow de nettoyage des données :

1. **Audit des doublons :**
   - Chercher visuellement dans "Gérer Personnes" les noms similaires
   - Ex: "Léa B" et "Lea B", "Diego" et "Diego C"

2. **Fusion des doublons :**
   - Utiliser "🔀 Fusionner" pour consolider
   - Choisir le nom le plus complet comme principal

3. **Enrichissement des données :**
   - Ajouter le genre pour chaque personne
   - Ajouter l'orientation si connue
   - Permet de meilleures prédictions futures

4. **Corrections de noms :**
   - Utiliser "✏️ Modifier" pour corriger les fautes de frappe
   - Uniformiser les formats (ex: "Alexandre" vs "Alex")

## Sécurité et contraintes

✅ **Protections en place :**
- Noms uniques (impossible d'avoir deux personnes avec le même nom)
- Transactions SQL (rollback en cas d'erreur)
- Logging de toutes les actions
- Validation des paramètres

⚠️ **Limitations :**
- Affichage limité à 30 personnes (performance)
- Pas de fonction "undo" (utiliser l'historique pour retrouver les infos)

## Exemples d'usage

### Corriger une faute de frappe :
```
1. Modifier "Mathhis" → "Matthis"
2. Le système met à jour toutes les 15 relations automatiquement
```

### Fusionner un doublon :
```
1. Identifier : "Alice L" et "Alice" sont la même personne
2. Fusionner "Alice" dans "Alice L" 
3. Toutes les relations d'"Alice" sont transférées à "Alice L"
4. "Alice" est supprimé
```

### Enrichir les données :
```
1. Modifier "Diego"
2. Genre: M
3. Orientation: straight
4. Enregistrer
```

## Fichiers modifiés

- ✅ `database.py` : Ajout table persons + 6 nouvelles méthodes
- ✅ `admin_components.py` : Nouvel onglet "Gérer Personnes"
- ✅ `app_full.py` : 2 nouveaux callbacks (edit/merge) + 2 modales
- ✅ `migrate_persons.py` : Script de migration initiale

## État actuel

- 📊 **84 personnes** migrées dans la table persons
- 🔗 **183 relations** (100% symétriques)
- ✨ **5 onglets** dans le panel admin (Propositions, Gérer Relations, Gérer Personnes, Ajouter, Historique)
