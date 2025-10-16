"""
Authentication UI Components
Modals pour login, register, et composants d'authentification
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_login_modal():
    """Modal de connexion"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("🔐 Connexion")),
        dbc.ModalBody([
            html.Div([
                dbc.Label("Nom d'utilisateur", className='control-label'),
                dbc.Input(
                    id='login-username',
                    type='text',
                    placeholder='Entrez votre username',
                    className='mb-3'
                ),
            ]),
            html.Div([
                dbc.Label("Mot de passe", className='control-label'),
                dbc.Input(
                    id='login-password',
                    type='password',
                    placeholder='Entrez votre mot de passe',
                    className='mb-3'
                ),
            ]),
            html.Div(id='login-error', className='text-danger mb-2'),
        ]),
        dbc.ModalFooter([
            dbc.Button("Annuler", id='btn-cancel-login', color='secondary', className='me-2'),
            dbc.Button("Se connecter", id='btn-submit-login', color='primary'),
        ]),
    ], id='modal-login', is_open=False, backdrop='static')


def create_register_modal():
    """Modal d'inscription"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("📝 Créer un compte")),
        dbc.ModalBody([
            html.Div([
                dbc.Label("Nom d'utilisateur", className='control-label'),
                dbc.Input(
                    id='register-username',
                    type='text',
                    placeholder='Choisissez un username',
                    className='mb-3'
                ),
            ]),
            html.Div([
                dbc.Label("Mot de passe", className='control-label'),
                dbc.Input(
                    id='register-password',
                    type='password',
                    placeholder='Choisissez un mot de passe',
                    className='mb-3'
                ),
            ]),
            html.Div([
                dbc.Label("Confirmer mot de passe", className='control-label'),
                dbc.Input(
                    id='register-password-confirm',
                    type='password',
                    placeholder='Confirmez votre mot de passe',
                    className='mb-3'
                ),
            ]),
            html.Div(id='register-error', className='text-danger mb-2'),
            html.Div(id='register-success', className='text-success mb-2'),
        ]),
        dbc.ModalFooter([
            dbc.Button("Annuler", id='btn-cancel-register', color='secondary', className='me-2'),
            dbc.Button("S'inscrire", id='btn-submit-register', color='primary'),
        ]),
    ], id='modal-register', is_open=False, backdrop='static')


def create_propose_person_modal():
    """Modal pour proposer une personne"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("➕ Proposer une personne")),
        dbc.ModalBody([
            html.P("Proposez une nouvelle personne à ajouter au réseau. Un admin devra approuver votre proposition.", 
                   className='text-muted mb-3'),
            html.Div([
                dbc.Label("Nom de la personne", className='control-label'),
                dbc.Input(
                    id='propose-person-name',
                    type='text',
                    placeholder='Entrez le nom',
                    className='mb-3'
                ),
            ]),
            html.Div(id='propose-person-error', className='text-danger mb-2'),
            html.Div(id='propose-person-success', className='text-success mb-2'),
        ]),
        dbc.ModalFooter([
            dbc.Button("Annuler", id='btn-cancel-propose-person', color='secondary', className='me-2'),
            dbc.Button("Proposer", id='btn-submit-propose-person', color='primary'),
        ]),
    ], id='modal-propose-person', is_open=False, backdrop='static')


def create_propose_relation_modal():
    """Modal pour proposer une relation"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("🔗 Proposer une relation")),
        dbc.ModalBody([
            html.P("Proposez une nouvelle relation. Un admin devra l'approuver.", 
                   className='text-muted mb-3'),
            html.Div([
                dbc.Label("Première personne", className='control-label'),
                dcc.Dropdown(
                    id='propose-relation-person1',
                    placeholder='Sélectionnez...',
                    className='mb-3'
                ),
            ]),
            html.Div([
                dbc.Label("Deuxième personne", className='control-label'),
                dcc.Dropdown(
                    id='propose-relation-person2',
                    placeholder='Sélectionnez...',
                    className='mb-3'
                ),
            ]),
            html.Div([
                dbc.Label("Type de relation", className='control-label'),
                dcc.Dropdown(
                    id='propose-relation-type',
                    options=[
                        {'label': '💋 Bisou', 'value': 0},
                        {'label': '😴 Dodo', 'value': 1},
                        {'label': '🛏️ Couché ensemble', 'value': 2},
                        {'label': '💑 Couple', 'value': 3},
                        {'label': '💔 Ex', 'value': 4},
                    ],
                    placeholder='Sélectionnez le type',
                    className='mb-3'
                ),
            ]),
            html.Div(id='propose-relation-error', className='text-danger mb-2'),
            html.Div(id='propose-relation-success', className='text-success mb-2'),
        ]),
        dbc.ModalFooter([
            dbc.Button("Annuler", id='btn-cancel-propose-relation', color='secondary', className='me-2'),
            dbc.Button("Proposer", id='btn-submit-propose-relation', color='primary'),
        ]),
    ], id='modal-propose-relation', is_open=False, backdrop='static')


def create_user_badge(username: str, is_admin: bool):
    """Badge utilisateur avec logout"""
    role = "👑 Admin" if is_admin else "👤 User"
    return html.Div([
        html.Span(f"{role} {username}", className='me-2', style={'fontWeight': '600'}),
        dbc.Button("Déconnexion", id='btn-logout', color='danger', size='sm'),
    ], style={'display': 'flex', 'alignItems': 'center'})


def create_public_header():
    """Header pour vue publique (non-authentifié)"""
    return html.Div([
        html.H1([
            html.I(className="fas fa-project-diagram", style={'marginRight': '10px'}),
            "Social Network Analyzer"
        ]),
        html.Div([
            dbc.Button([
                html.I(className="fas fa-user-plus", style={'marginRight': '5px'}),
                "S'inscrire"
            ], id='btn-open-register', color='info', className='me-2'),
            dbc.Button([
                html.I(className="fas fa-sign-in-alt", style={'marginRight': '5px'}),
                "Connexion"
            ], id='btn-open-login', color='primary'),
        ], style={'display': 'flex', 'gap': '10px'}),
    ], className='header-bar')


def create_admin_header(username: str, is_admin: bool):
    """Header pour vue admin (authentifié)"""
    return html.Div([
        html.H1([
            html.I(className="fas fa-project-diagram", style={'marginRight': '10px'}),
            "Social Network Analyzer"
        ]),
        html.Div(id='user-badge-container', children=[
            create_user_badge(username, is_admin)
        ]),
    ], className='header-bar')
