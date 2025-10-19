# 👥 Guide Gestion des Utilisateurs

## Vue d'ensemble
Nouvel onglet admin complet pour gérer les utilisateurs de la plateforme:
- ✅ Promouvoir/rétrograder des admins
- ✅ Supprimer des comptes
- ✅ Approuver/rejeter les demandes de compte
- ✅ Filtrer les utilisateurs

---

## Accès au menu

**URL:** `http://localhost:8052`

**Login:** 
- Username: `admin`
- Password: `admin123`

Puis aller à l'onglet **"👥 Utilisateurs"** (5ème onglet du panel admin)

---

## Fonctionnalités principales

### 1. 👥 Utilisateurs Actifs

#### Affichage
Liste de tous les utilisateurs avec:
- Badge 👑 Admin (si administrateur)
- Email de l'utilisateur
- Date de création

#### Actions disponibles

**Bouton "Promouvoir admin" / "Retirer admin"** (jaune)
- Promeut un utilisateur régulier en administrateur
- Rétrograde un administrateur à utilisateur régulier
- Enregistre l'action dans l'historique

**Bouton "Supprimer" (Trash)** (rouge)
- Désactive le compte (soft delete)
- L'utilisateur ne peut plus se connecter
- Les données sont conservées dans l'audit

### 2. ⏳ En Attente d'Approbation

#### Affichage
Liste des utilisateurs en attente avec:
- Username demandé
- Email (si fourni)
- Date de la demande

#### Actions disponibles

**Bouton ✅ (vert)**
- Approuve l'utilisateur SANS admin
- Crée un compte régulier

**Bouton 👑 (jaune)**
- Approuve l'utilisateur ET le promeut admin
- Crée un compte administrateur direct

**Bouton ❌ (rouge)**
- Rejette la demande
- Le compte n'est pas créé

### 3. 🔍 Filtres

Filtrer les utilisateurs actifs par:
- **Tous** - Affiche tous les utilisateurs
- **👑 Admins** - Affiche uniquement les administrateurs
- **👤 Utilisateurs** - Affiche uniquement les utilisateurs réguliers
- **⏳ En attente** - Affiche seulement les demandes en attente

### 4. 🔄 Actualiser

Bouton pour rafraîchir les listes manuellement

---

## Audit & Historique

Toutes les actions sont enregistrées:

| Action | Enregistrement |
|--------|---|
| Promotion admin | ✅ Audit log: demote → admin |
| Rétrogradation | ✅ Audit log: admin → user |
| Approbation | ✅ Audit log: pending → approved |
| Rejet | ✅ Audit log: pending → rejected |
| Suppression | ✅ Audit log: user → deleted |

**Voir dans l'onglet "📋 Historique"** pour voir toutes les actions

---

## Base de données

### Table: `users`
```
id             INTEGER PRIMARY KEY
username       TEXT UNIQUE NOT NULL
password_hash  TEXT NOT NULL
is_admin       INTEGER (0 ou 1)
created_at     TEXT
last_login     TEXT
is_active      INTEGER (0 ou 1, soft delete)
```

### Table: `pending_accounts`
```
id              INTEGER PRIMARY KEY
username        TEXT UNIQUE NOT NULL
password_hash   TEXT NOT NULL
requested_at    TEXT
status          TEXT (pending/approved/rejected)
```

### Table: `audit_log`
```
action_type     TEXT (approve/promote/demote/reject/delete)
entity_type     TEXT (user)
entity_id       INTEGER
entity_name     TEXT (username)
performed_by    TEXT (admin)
old_value       TEXT
new_value       TEXT
status          TEXT (completed/cancelled)
created_at      TEXT
```

---

## Méthodes API

### UserRepository

```python
# Récupérer utilisateurs
UserRepository.get_all_users()              # Liste tous les utilisateurs actifs
UserRepository.get_user_by_id(user_id)     # Récupère un utilisateur par ID
UserRepository.get_user_by_username(name)  # Récupère un utilisateur par username
UserRepository.get_pending_users()          # Liste les demandes en attente

# Gestion des utilisateurs
UserRepository.promote_to_admin(user_id)    # Promouvoir en admin
UserRepository.demote_from_admin(user_id)   # Rétrograder d'admin
UserRepository.delete_user(user_id)         # Supprimer (soft delete)

# Gestion des demandes
UserRepository.approve_pending_user(pending_id, make_admin=False)
UserRepository.get_pending_user_by_id(pending_id)
UserRepository.reject_pending_user(pending_id)

# Authentification
UserRepository.authenticate(username, password)
UserRepository.create_user(username, password, is_admin=False)
UserRepository.verify_password(password, password_hash)
```

---

## Exemple d'utilisation

```python
from database.users import UserRepository
from database.audit import AuditRepository

# Promouvoir Diego en admin
UserRepository.promote_to_admin(1)

# Log l'action
AuditRepository.log_action(
    action_type='promote',
    entity_type='user',
    entity_id=1,
    entity_name='Diego',
    performed_by='admin',
    old_value='user',
    new_value='admin'
)

# Approuver une demande en tant qu'admin
UserRepository.approve_pending_user(5, make_admin=True)

# Obtenir tous les admins
all_users = UserRepository.get_all_users()
admins = [u for u in all_users if u['is_admin']]
print(f"Admins: {[a['username'] for a in admins]}")
```

---

## Sécurité

- ✅ Seuls les admins peuvent accéder au menu "👥 Utilisateurs"
- ✅ Les mots de passe sont hashés avec SHA-256 + salt
- ✅ Les actions sont auditées et enregistrées
- ✅ Soft delete: les comptes supprimés restent en base avec `is_active=0`
- ✅ Les tokens de session vérifient l'admin status

---

## Troubleshooting

**❌ Onglet grisé / désactivé?**
→ Vous n'êtes pas admin. Demandez à un admin de vous promouvoir.

**❌ Changement ne s'applique pas?**
→ Cliquez sur "🔄 Actualiser" pour rafraîchir les listes.

**❌ L'utilisateur peut se reconnecter après suppression?**
→ C'est normal, le compte est juste marqué `is_active=0`. Pour sécurité totale, changez son mot de passe ou supprimez directement en SQL.

---

## Logs d'app

Voir `/tmp/app.log` pour les erreurs de connexion

```bash
tail -f /tmp/app.log | grep "user management"
```

---

## Statistiques actuelles

- 👥 **8 utilisateurs** (7 réguliers + 1 admin)
- ⏳ **0 en attente**
- 📋 **Audit complet** de toutes les modifications
