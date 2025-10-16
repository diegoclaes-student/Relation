# 🎯 Guide Rapide - Interface V4

## Lancer l'Application
```bash
python3 app_v2.py
```
Puis ouvrir: http://localhost:8052

---

## ✨ Nouveautés V4

### 1. **Ajouter une Relation** (Bouton vert "Add Relation")

**Super simple maintenant!**
1. Tape un nom dans "First Person" → Sélectionne (personne existante OU "➕ Create new: NomTapé")
2. Tape un nom dans "Second Person" → Sélectionne
3. Choisis le type de relation (💋 Bisou, 😴 Dodo, etc.)
4. Click "Add Relation" → C'est fait!

**Indicateurs visuels:**
- ✅ Existing person selected (personne existe déjà)
- ➕ Will create new person: X (personne sera créée automatiquement)

**Plus besoin de:**
- ❌ Cliquer sur "Create New Person"
- ❌ Remplir des formulaires cachés
- ❌ Se demander si la personne existe ou pas

---

### 2. **Gérer les Relations** (Bouton bleu "Update Relation")

**Nouvelle interface liste complète!**
- Voir TOUTES tes relations en un coup d'œil
- Chaque relation a 2 boutons:
  - **[Edit]** → Change le type de relation
  - **[Delete]** → Supprime la relation

**Fonctionnalités:**
- ✅ Une seule entrée par paire (pas de doublons Alice↔Bob et Bob↔Alice)
- ✅ Auto-refresh après chaque modification
- ✅ Suppression prend en compte les symétries (les 2 directions supprimées)

---

## 🎨 Interface

### Modal "Add Relation"
```
┌───────────────────────────────┐
│ 🔗 Add New Relation          │
├───────────────────────────────┤
│                               │
│ 👤 First Person (fond bleu)   │
│ 🔍 Type a name...          ▼ │
│ ✅ Existing person selected   │
│                               │
│ 👤 Second Person (fond bleu)  │
│ 🔍 Type a name...          ▼ │
│ ➕ Will create new: TestName  │
│                               │
│ ❤️ Relation Type (fond rose)  │
│ Select type...             ▼ │
│                               │
│        [Cancel] [Add Relation]│
└───────────────────────────────┘
```

### Modal "Manage Relations"
```
┌───────────────────────────────┐
│ 📝 Manage Relations          │
├───────────────────────────────┤
│                               │
│ 👥 Alice ↔ Bob                │
│ ❤️ Type: 💋 Bisou              │
│         [Edit] [Delete]       │
│                               │
│ 👥 Diego ↔ Tom                │
│ ❤️ Type: 💑 Couple             │
│         [Edit] [Delete]       │
│                               │
│                      [Close]  │
└───────────────────────────────┘
```

---

## 🔥 Tips

### Créer une relation rapidement:
1. Click "Add Relation"
2. Tape "Jean" → Sélectionne "➕ Create new: Jean"
3. Tape "Marie" → Sélectionne "➕ Create new: Marie"
4. Sélectionne "💑 Couple"
5. Submit → Jean et Marie créés + Relation créée!

**Temps total: ~10 secondes!**

### Modifier un type de relation:
1. Click "Update Relation"
2. Click "Edit" sur la relation à modifier
3. Choisis nouveau type
4. Click "Save Changes"

**Temps total: ~5 secondes!**

### Supprimer une relation:
1. Click "Update Relation"
2. Click "Delete" sur la relation
3. C'est fait!

**Temps total: ~2 secondes!**

---

## 📊 Types de Relations Disponibles

| Emoji | Type | Description |
|-------|------|-------------|
| 💋 | Bisou | |
| 😴 | Dodo | |
| 🛏️ | Couché ensemble | |
| 💑 | Couple | |
| 💔 | Ex | |

---

## ❓ FAQ

**Q: Que se passe-t-il si je tape un nom qui existe déjà?**
A: Le dropdown montre la personne existante, et l'indicator affiche "✅ Existing person selected".

**Q: Puis-je créer deux personnes en même temps?**
A: Oui! Tape deux noms inexistants, sélectionne "Create new" pour chacun, et submit.

**Q: Si je supprime une relation, est-ce que les personnes sont supprimées?**
A: Non, seule la relation est supprimée. Les personnes restent dans la base.

**Q: Comment savoir si une relation existe déjà?**
A: Dans le graphe, les personnes connectées ont un lien visible. Tu peux aussi vérifier dans "Update Relation".

**Q: Puis-je avoir plusieurs types de relations entre les mêmes personnes?**
A: Non, une seule relation par paire. Pour changer le type, utilise "Update Relation" → "Edit".

---

## 🐛 Bugs Connus

Aucun pour le moment! 🎉

---

## 📝 Documentation Complète

Voir `UX_REFONTE_V4.md` pour tous les détails techniques.
