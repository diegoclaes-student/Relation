# 🔐 Système d'Authentification V7 - Architecture

## Date: 17 octobre 2025

## 🎯 Objectif
Créer deux vues distinctes :
1. **Vue Publique** : Graph + Search + Propose + Login
2. **Vue Admin** : Vue actuelle complète + Admin Panel

---

## 📊 Architecture Base de Données

### Tables créées

#### `users`
```sql
- id: INTEGER PRIMARY KEY
- username: TEXT UNIQUE
- password_hash: TEXT (SHA-256 + salt)
- is_admin: INTEGER (0 ou 1)
- created_at: TEXT (ISO datetime)
- last_login: TEXT
- is_active: INTEGER (soft delete)
```

#### `pending_accounts`
```sql
- id: INTEGER PRIMARY KEY
- username: TEXT UNIQUE
- password_hash: TEXT
- requested_at: TEXT
- status: TEXT ('pending', 'approved', 'rejected')
```

#### `pending_persons`
```sql
- id: INTEGER PRIMARY KEY
- name: TEXT
- submitted_by: TEXT (username)
- submitted_at: TEXT
- status: TEXT
```

#### `pending_relations`
```sql
- id: INTEGER PRIMARY KEY
- person1: TEXT
- person2: TEXT
- relation_type: INTEGER
- submitted_by: TEXT (username)
- submitted_at: TEXT
- status: TEXT
```

---

## 🏗️ Repositories Créés

### `/database/users.py`
- `UserRepository`
  - `create_user(username, password, is_admin)`
  - `authenticate(username, password)`
  - `get_user_by_username(username)`
  - `hash_password(password)` → SHA-256 + salt
  - `verify_password(password, hash)`
  
- `PendingAccountRepository`
  - `create_request(username, password)`
  - `get_pending_requests()`
  - `approve_request(request_id)` → Crée user
  - `reject_request(request_id)`

### `/database/pending_submissions.py`
- `PendingSubmissionRepository`
  - `submit_person(name, submitted_by)`
  - `submit_relation(p1, p2, type, submitted_by)`
  - `get_pending_persons()`
  - `get_pending_relations()`
  - `approve_person(id)` → Ajoute à persons
  - `approve_relation(id)` → Ajoute à relations
  - `reject_person(id)`
  - `reject_relation(id)`

---

## 🔧 Services Créés

### `/services/auth.py`
- `AuthService`
  - `login(username, password)` → User dict ou None
  - `register_request(username, password)` → (success, message)
  - `is_admin(user)` → bool
  - `is_authenticated(user)` → bool

---

## 🎨 À implémenter (Suite)

### 4. Composants UI (`/components/auth/`)
- [x] Login modal
- [x] Register modal
- [x] User badge (affiche username + logout)
- [x] Admin panel

### 5. Vue Publique (non-authentifié)
```python
- Graph interactif (read-only)
- Search bar (chercher personne)
- Button "Proposer Relation"
- Button "Proposer Personne"
- Button "Se connecter"
- Button "Créer un compte"
```

### 6. Vue Admin (authentifié)
```python
- Tout l'actuel (manage relations, manage persons, etc.)
+ Admin Panel:
  - Pending Accounts (approve/reject)
  - Pending Persons (approve/reject)
  - Pending Relations (approve/reject)
  - User Management (list, delete)
```

### 7. Session Management
```python
- Flask secret_key configuration
- dcc.Store('user-session') → JSON user data
- Server-side session Flask-Session
- Callbacks protected by @auth_required
```

### 8. Callbacks
```python
- login_callback(username, password)
- logout_callback()
- register_callback(username, password)
- propose_person_callback(name)
- propose_relation_callback(p1, p2, type)
- approve_account_callback(request_id)
- approve_person_callback(submission_id)
- approve_relation_callback(submission_id)
- reject_*_callback()
```

---

## 🔐 Sécurité

### Password Hashing
```python
salt = secrets.token_hex(16)  # 32 chars hex
hash = SHA-256(password + salt)
stored = f"{salt}${hash}"
```

### Session
```python
Flask session (server-side)
+ dcc.Store (client-side, non-sensitive data only)
```

### Authorization
```python
def require_admin(callback_func):
    def wrapper(*args, **kwargs):
        if not is_admin(current_user):
            return no_update
        return callback_func(*args, **kwargs)
    return wrapper
```

---

## 📱 Workflow Utilisateur

### Nouveau compte
1. User clique "Créer un compte"
2. Modal : username + password
3. → `pending_accounts` table
4. Admin voit dans Admin Panel
5. Admin approve → User créé dans `users`
6. User peut login

### Proposer une relation (non-admin)
1. User login
2. Clique "Proposer Relation"
3. Modal : Person1 + Person2 + Type
4. → `pending_relations` table
5. Admin voit et approve
6. → Ajouté à `relations` table
7. Graph mis à jour

---

## 🎨 UI/UX

### Vue Publique
```
┌─────────────────────────────────────┐
│  🌐 Social Network [Connexion] [S'inscrire]
├─────────────────────────────────────┤
│                                     │
│          GRAPHE INTERACTIF          │
│         (Read-only + Zoom)          │
│                                     │
├─────────────────────────────────────┤
│  🔍 Rechercher une personne         │
│  ➕ Proposer une personne           │
│  🔗 Proposer une relation           │
└─────────────────────────────────────┘
```

### Vue Admin
```
┌─────────────────────────────────────┐
│  🌐 Social Network    👤 Admin [Déconnexion]
├─────────────────────────────────────┤
│  [Graph] [Manage] [Admin Panel]    │
├─────────────────────────────────────┤
│  ... Vue actuelle complète ...     │
│  + Onglet Admin Panel:             │
│    - 3 pending accounts             │
│    - 5 pending persons              │
│    - 2 pending relations            │
│    - User management                │
└─────────────────────────────────────┘
```

---

## ✅ Fait
- [x] Tables DB (users, pending_*)
- [x] UserRepository
- [x] PendingAccountRepository
- [x] PendingSubmissionRepository
- [x] AuthService
- [x] Admin par défaut (admin/admin123)

## 🔧 En cours
- [ ] Modals UI (login, register, propose)
- [ ] Layout avec conditional rendering
- [ ] Callbacks authentification
- [ ] Admin Panel UI
- [ ] Session management

## 📝 Reste à faire
- [ ] Tests complets
- [ ] Documentation utilisateur
- [ ] Notifications (toasts)
- [ ] Export/Import CSV admins

---

## 🚀 Démarrage

```bash
python3 app_v2.py

# Credentials admin par défaut:
Username: admin
Password: admin123
```

---

**État:** Repositories et Services créés ✅  
**Prochaine étape:** Créer les composants UI et intégrer dans app_v2.py
