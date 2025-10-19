"""
Authentication UI Components
Modals pour login, register, et composants d'authentification
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_login_modal():
    """Modal de connexion"""
    return dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle("🔐 Connexion"),
            style={'background': '#1a2332', 'color': 'white', 'borderBottom': '1px solid #e0e4e8'}
        ),
        dbc.ModalBody([
            html.Div([
                dbc.Label("Nom d'utilisateur", style={'color': '#1a2332', 'fontSize': '13px', 'fontWeight': '500'}),
                dbc.Input(
                    id='input-login-username',
                    type='text',
                    placeholder='Entrez votre username',
                    className='mb-3',
                    style={'borderRadius': '6px', 'border': '1px solid #e0e4e8'}
                ),
            ]),
            html.Div([
                dbc.Label("Mot de passe", style={'color': '#1a2332', 'fontSize': '13px', 'fontWeight': '500'}),
                dbc.Input(
                    id='input-login-password',
                    type='password',
                    placeholder='Entrez votre mot de passe',
                    className='mb-3',
                    style={'borderRadius': '6px', 'border': '1px solid #e0e4e8'}
                ),
            ]),
            html.Div(id='login-error', className='text-danger mb-2'),
        ]),
        dbc.ModalFooter([
            dbc.Button("Annuler", id='btn-cancel-login', color='secondary', className='me-2', style={'borderRadius': '6px'}),
            dbc.Button("Se connecter", id='btn-submit-login', style={
                'background': '#1a2332',
                'border': 'none',
                'color': 'white',
                'borderRadius': '6px'
            }),
        ]),
    ], id='modal-login', is_open=False, backdrop='static')


def create_register_modal():
    """Modal d'inscription"""
    return dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle("📝 Créer un compte"),
            style={'background': '#1a2332', 'color': 'white', 'borderBottom': '1px solid #e0e4e8'}
        ),
        dbc.ModalBody([
            html.Div([
                dbc.Label("Nom d'utilisateur", style={'color': '#1a2332', 'fontSize': '13px', 'fontWeight': '500'}),
                dbc.Input(
                    id='input-register-username',
                    type='text',
                    placeholder='Choisissez un username',
                    className='mb-3',
                    style={'borderRadius': '6px', 'border': '1px solid #e0e4e8'}
                ),
            ]),
            html.Div([
                dbc.Label("Mot de passe", style={'color': '#1a2332', 'fontSize': '13px', 'fontWeight': '500'}),
                dbc.Input(
                    id='input-register-password',
                    type='password',
                    placeholder='Choisissez un mot de passe (min 6 caractères)',
                    className='mb-3',
                    style={'borderRadius': '6px', 'border': '1px solid #e0e4e8'}
                ),
            ]),
            html.Div([
                dbc.Label("Confirmer mot de passe", style={'color': '#1a2332', 'fontSize': '13px', 'fontWeight': '500'}),
                dbc.Input(
                    id='input-register-confirm',
                    type='password',
                    placeholder='Confirmez votre mot de passe',
                    className='mb-3',
                    style={'borderRadius': '6px', 'border': '1px solid #e0e4e8'}
                ),
            ]),
            html.Div(id='register-error', className='text-danger mb-2'),
            html.Div(id='register-success', className='text-success mb-2'),
        ]),
        dbc.ModalFooter([
            dbc.Button("Annuler", id='btn-cancel-register', color='secondary', className='me-2', style={'borderRadius': '6px'}),
            dbc.Button("S'inscrire", id='btn-submit-register', style={
                'background': '#1a2332',
                'border': 'none',
                'color': 'white',
                'borderRadius': '6px'
            }),
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
                    id='input-propose-person-name',
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
                    id='dropdown-propose-rel-p1',
                    placeholder='🔍 Tapez un nom... (existant ou nouveau)',
                    searchable=True,
                    className='mb-3'
                ),
            ]),
            html.Div([
                dbc.Label("Deuxième personne", className='control-label'),
                dcc.Dropdown(
                    id='dropdown-propose-rel-p2',
                    placeholder='🔍 Tapez un nom... (existant ou nouveau)',
                    searchable=True,
                    className='mb-3'
                ),
            ]),
            html.Div([
                dbc.Label("Type de relation", className='control-label'),
                dcc.Dropdown(
                    id='dropdown-propose-rel-type',
                    options=[
                        {'label': '💋 Bisou', 'value': 0},
                        {'label': '😴 Dodo', 'value': 1},
                        {'label': '🛏️ Couché ensemble', 'value': 2},
                        {'label': '💑 Couple', 'value': 3},
                        {'label': '💔 Ex', 'value': 4},
                    ],
                    placeholder='Sélectionnez le type',
                    searchable=True,
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
    """Header pour vue publique (non-authentifié) - Compact sur mobile"""
    return html.Div([
        html.H1([
            html.I(className="fas fa-map-marked-alt", style={'marginRight': '10px'}),
            "Centrale Potins Maps"
        ]),
        html.Div([
            # Boutons plus compacts sur mobile
            dbc.Button([
                html.I(className="fas fa-user-plus", style={'marginRight': '5px'}),
                html.Span("S'inscrire", className='auth-btn-text')
            ], id='btn-open-register', color='info', size='sm', className='me-2 auth-header-btn'),
            dbc.Button([
                html.I(className="fas fa-sign-in-alt", style={'marginRight': '5px'}),
                html.Span("Connexion", className='auth-btn-text')
            ], id='btn-open-login', color='primary', size='sm', className='auth-header-btn'),
        ], style={'display': 'flex', 'gap': '8px'}),
    ], className='header-bar')


def create_admin_header(username: str, is_admin: bool):
    """Header pour vue admin (authentifié)"""
    return html.Div([
        html.H1([
            html.I(className="fas fa-map-marked-alt", style={'marginRight': '10px'}),
            "Centrale Potins Maps"
        ]),
        html.Div(id='user-badge-container', children=[
            create_user_badge(username, is_admin)
        ]),
    ], className='header-bar')
