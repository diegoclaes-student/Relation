# 🔐 V7 - Système d'Authentification - Plan d'Intégration

## ✅ Fait jusqu'ici

### 1. Base de données & Repositories ✅
- `/database/users.py` : UserRepository, PendingAccountRepository
- `/database/pending_submissions.py` : PendingSubmissionRepository
- Admin par défaut créé : **admin / admin123**

### 2. Services ✅
- `/services/auth.py` : AuthService (login, register, is_admin, is_authenticated)

### 3. Composants UI ✅
- `/components/auth_components.py` : 
  - Modal login
  - Modal register
  - Modal propose person
  - Modal propose relation
  - User badge
  - Headers (public/admin)
  
- `/components/admin_panel.py` :
  - Admin panel tab
  - Render pending accounts/persons/relations
  - Approve/reject buttons

---

## 🔧 Prochaines étapes

### Étape 1 : Modifier app_v2.py pour ajouter session et vues conditionnelles

**A. Ajouter imports**
```python
from flask import Flask, session
from components.auth_components import *
from components.admin_panel import *
from database.users import user_repository, pending_account_repository
from database.pending_submissions import pending_submission_repository
from services.auth import auth_service
```

**B. Configurer Flask session**
```python
server = app.server
server.secret_key = 'votre_secret_key_ici_CHANGEZ_MOI'  # À changer en prod!
```

**C. Ajouter Store session dans layout**
```python
dcc.Store(id='user-session', data=None, storage_type='session'),
```

**D. Créer fonction pour layout conditionnel**
```python
def get_layout(user_session):
    if user_session and user_session.get('username'):
        # Vue admin (authentifié)
        return create_admin_layout(user_session)
    else:
        # Vue publique
        return create_public_layout()
```

**E. Vue publique (non-authentifié)**
```python
def create_public_layout():
    return html.Div([
        dcc.Store(id='user-session', data=None, storage_type='session'),
        
        # Modals
        create_login_modal(),
        create_register_modal(),
        create_propose_person_modal(),
        create_propose_relation_modal(),
        
        # Header public
        create_public_header(),
        
        # Graph (read-only)
        html.Div([
            html.Div([
                dcc.Graph(id='network-graph', ...),
            ], className='graph-panel'),
        ]),
        
        # Actions publiques
        html.Div([
            html.Div("🔍 Navigation", className='section-title'),
            dbc.Input(
                id='public-search-person',
                placeholder='Rechercher une personne...',
                className='mb-3'
            ),
            dbc.Button("➕ Proposer une personne", id='btn-open-propose-person', ...),
            dbc.Button("🔗 Proposer une relation", id='btn-open-propose-relation', ...),
        ], className='public-actions'),
    ])
```

**F. Vue admin (authentifié)**
```python
def create_admin_layout(user_session):
    return html.Div([
        dcc.Store(id='user-session', data=user_session, storage_type='session'),
        
        # Modals (toutes)
        ... tous les modals actuels + auth modals ...
        
        # Header admin
        create_admin_header(user_session['username'], user_session['is_admin']),
        
        # Tabs
        dbc.Tabs([
            dbc.Tab(label="📊 Graph", tab_id='tab-graph'),
            dbc.Tab(label="🔧 Manage", tab_id='tab-manage'),
            dbc.Tab(label="👑 Admin" if is_admin else "👤 Profil", tab_id='tab-admin'),
        ], id='main-tabs', active_tab='tab-graph'),
        
        # Content basé sur tab
        html.Div(id='tab-content'),
    ])
```

---

### Étape 2 : Créer callbacks authentification

**A. Login callback**
```python
@app.callback(
    [Output('user-session', 'data'),
     Output('modal-login', 'is_open'),
     Output('login-error', 'children'),
     Output('url', 'pathname')],  # Pour refresh page
    [Input('btn-submit-login', 'n_clicks')],
    [State('login-username', 'value'),
     State('login-password', 'value')],
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    if not username or not password:
        return no_update, True, "Veuillez remplir tous les champs", no_update
    
    user = auth_service.login(username, password)
    if user:
        # Store in Flask session
        session['user'] = user
        return user, False, "", "/"  # Refresh page
    else:
        return no_update, True, "Identifiants incorrects", no_update
```

**B. Register callback**
```python
@app.callback(
    [Output('modal-register', 'is_open'),
     Output('register-error', 'children'),
     Output('register-success', 'children')],
    [Input('btn-submit-register', 'n_clicks')],
    [State('register-username', 'value'),
     State('register-password', 'value'),
     State('register-password-confirm', 'value')],
    prevent_initial_call=True
)
def register(n_clicks, username, password, password_confirm):
    if not username or not password:
        return True, "Veuillez remplir tous les champs", ""
    
    if password != password_confirm:
        return True, "Les mots de passe ne correspondent pas", ""
    
    success, message = auth_service.register_request(username, password)
    if success:
        return False, "", message  # Ferme modal, affiche succès
    else:
        return True, message, ""
```

**C. Logout callback**
```python
@app.callback(
    [Output('user-session', 'data'),
     Output('url', 'pathname')],
    [Input('btn-logout', 'n_clicks')],
    prevent_initial_call=True
)
def logout(n_clicks):
    session.pop('user', None)
    return None, "/"
```

**D. Propose person callback**
```python
@app.callback(
    [Output('modal-propose-person', 'is_open'),
     Output('propose-person-error', 'children'),
     Output('propose-person-success', 'children')],
    [Input('btn-submit-propose-person', 'n_clicks')],
    [State('propose-person-name', 'value'),
     State('user-session', 'data')],
    prevent_initial_call=True
)
def propose_person(n_clicks, name, user_session):
    if not user_session:
        return True, "Vous devez être connecté", ""
    
    if not name:
        return True, "Veuillez entrer un nom", ""
    
    submission_id = pending_submission_repository.submit_person(
        name, user_session['username']
    )
    
    if submission_id:
        return False, "", "Proposition envoyée !"
    else:
        return True, "Erreur lors de la soumission", ""
```

**E. Admin approve/reject callbacks**
```python
@app.callback(
    Output('pending-accounts-list', 'children'),
    [Input({'type': 'approve-account', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-account', 'index': ALL}, 'n_clicks'),
     Input('btn-refresh-admin', 'n_clicks')],
    [State('user-session', 'data')],
    prevent_initial_call=True
)
def handle_pending_accounts(approve_clicks, reject_clicks, refresh, user_session):
    if not user_session or not user_session.get('is_admin'):
        return no_update
    
    ctx_triggered = ctx.triggered_id
    if ctx_triggered:
        if isinstance(ctx_triggered, dict):
            action_type = ctx_triggered['type']
            item_id = ctx_triggered['index']
            
            if action_type == 'approve-account':
                pending_account_repository.approve_request(item_id)
            elif action_type == 'reject-account':
                pending_account_repository.reject_request(item_id)
    
    # Refresh list
    accounts = pending_account_repository.get_pending_requests()
    return render_pending_accounts_list(accounts)
```

---

### Étape 3 : Layout conditionnel principal

**Modifier app.layout**
```python
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content'),
])

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
)
def display_page(pathname):
    # Récupérer session
    user = session.get('user', None)
    
    if user:
        return create_admin_layout(user)
    else:
        return create_public_layout()
```

---

## 🎯 Résumé des modifs app_v2.py

1. ✅ Ajouter imports auth/admin components
2. ✅ Configurer Flask session (secret_key)
3. ✅ Créer create_public_layout()
4. ✅ Créer create_admin_layout()
5. ✅ Modifier app.layout pour routing
6. ✅ Callbacks auth (login, logout, register)
7. ✅ Callbacks propose (person, relation)
8. ✅ Callbacks admin (approve, reject)
9. ✅ Callback populate dropdowns propose-relation

---

## 🚀 Ordre d'implémentation

1. Modifier structure app_v2.py (session + routing)
2. Créer layouts (public + admin)
3. Implémenter callbacks auth basiques (login/logout)
4. Implémenter callbacks propose
5. Implémenter callbacks admin panel
6. Tests complets du workflow

---

## 📝 À ne pas oublier

- [ ] Changer secret_key en production
- [ ] Ajouter timeout session (30 min)
- [ ] Ajouter CSRF protection
- [ ] Logger les actions admin
- [ ] Rate limiting sur login
- [ ] Validation côté serveur (longueur password, etc.)
- [ ] Notifications toast pour feedback
- [ ] Tests unitaires auth service

---

**Prêt pour intégration dans app_v2.py !**
