"""
User Management Component
Gestion des utilisateurs: permissions admin, suppression de compte
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from database.users import UserRepository


def create_user_management_tab():
    """Crée l'onglet Gestion des utilisateurs"""
    return html.Div([
        html.Div("👥 Gestion des utilisateurs", className='section-title', style={'marginBottom': '20px'}),
        
        # Filters
        html.Div([
            html.Div([
                html.Label("Filtrer par:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                dbc.ButtonGroup([
                    dbc.Button(
                        "Tous",
                        id='filter-all-users',
                        active=True,
                        outline=False,
                        color='primary'
                    ),
                    dbc.Button(
                        "👑 Admins",
                        id='filter-admins',
                        active=False,
                        outline=True,
                        color='primary'
                    ),
                    dbc.Button(
                        "👤 Utilisateurs",
                        id='filter-users',
                        active=False,
                        outline=True,
                        color='primary'
                    ),
                    dbc.Button(
                        "⏳ En attente",
                        id='filter-pending',
                        active=False,
                        outline=True,
                        color='primary'
                    ),
                ], className='w-100'),
            ], style={'marginBottom': '20px'}),
        ]),
        
        # Active Users List
        html.Div([
            html.H5("👥 Utilisateurs actifs", style={'marginBottom': '15px'}),
            html.Div(id='active-users-list', children=[
                html.P("Chargement...", className='text-muted')
            ]),
        ], style={'marginBottom': '30px'}),
        
        # Pending Users List
        html.Div([
            html.H5("⏳ En attente d'approbation", style={'marginBottom': '15px'}),
            html.Div(id='pending-users-list', children=[
                html.P("Aucun utilisateur en attente", className='text-muted')
            ]),
        ], style={'marginBottom': '30px'}),
        
        # Refresh button
        html.Div([
            dbc.Button([
                html.I(className="fas fa-sync", style={'marginRight': '8px'}),
                "Actualiser"
            ], id='btn-refresh-users', color='secondary', className='w-100'),
        ]),
        
        # Store for filter state
        dcc.Store(id='user-filter-state', data='all'),
    ])


def render_active_user_item(user: dict) -> html.Div:
    """Rend un item d'utilisateur actif"""
    admin_badge = html.Span(
        "👑 Admin",
        style={
            'backgroundColor': '#FFC107',
            'color': '#000',
            'padding': '4px 8px',
            'borderRadius': '4px',
            'fontSize': '12px',
            'fontWeight': 'bold',
            'marginRight': '8px'
        }
    ) if user.get('is_admin') else html.Span("")
    
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    admin_badge,
                    html.Strong(user['username']),
                ], style={'marginBottom': '5px'}),
                html.Small(f"Email: {user.get('email', 'N/A')}", className='text-muted', style={'display': 'block'}),
                html.Small(f"Créé le: {str(user.get('created_at', 'N/A'))[:10]}", className='text-muted'),
            ], style={'flex': '1'}),
            html.Div([
                dbc.Button([
                    html.I(className="fas fa-crown", style={'marginRight': '4px'}),
                    ("Retirer admin" if user.get('is_admin') else "Promouvoir admin")
                ], id={'type': 'toggle-admin', 'index': user['id']}, 
                   color='warning' if user.get('is_admin') else 'success',
                   size='sm', className='me-2'),
                dbc.Button([
                    html.I(className="fas fa-trash")
                ], id={'type': 'delete-user', 'index': user['id']}, 
                   color='danger', size='sm'),
            ], style={'display': 'flex'}),
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'padding': '12px',
            'border': '1px solid #e0e0e0',
            'borderRadius': '8px',
            'marginBottom': '10px',
            'backgroundColor': '#f8f9fa'
        }),
    ])


def render_pending_user_item(user: dict) -> html.Div:
    """Rend un item d'utilisateur en attente"""
    return html.Div([
        html.Div([
            html.Div([
                html.Strong(user['username']),
                html.Br(),
                html.Small(f"Email: {user.get('email', 'N/A')}", className='text-muted', style={'display': 'block'}),
                html.Small(f"Demandé le: {str(user.get('submitted_at', 'N/A'))[:10]}", className='text-muted'),
            ], style={'flex': '1'}),
            html.Div([
                dbc.Button([
                    html.I(className="fas fa-check")
                ], id={'type': 'approve-pending-user', 'index': user['id']}, 
                   color='success', size='sm', className='me-1', 
                   title="Approuver sans admin"),
                dbc.Button([
                    html.I(className="fas fa-crown")
                ], id={'type': 'approve-pending-admin', 'index': user['id']}, 
                   color='warning', size='sm', className='me-1',
                   title="Approuver comme admin"),
                dbc.Button([
                    html.I(className="fas fa-times")
                ], id={'type': 'reject-pending-user', 'index': user['id']}, 
                   color='danger', size='sm'),
            ], style={'display': 'flex'}),
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'padding': '12px',
            'border': '1px solid #FFC107',
            'borderRadius': '8px',
            'marginBottom': '10px',
            'backgroundColor': '#FFFBEA'
        }),
    ])


def render_active_users_list(users: list, filter_type: str = 'all') -> html.Div:
    """Rend la liste des utilisateurs actifs avec filtrage"""
    if not users:
        return html.P("Aucun utilisateur", className='text-muted')
    
    # Apply filter
    if filter_type == 'admins':
        users = [u for u in users if u.get('is_admin')]
    elif filter_type == 'users':
        users = [u for u in users if not u.get('is_admin')]
    
    if not users:
        return html.P(f"Aucun utilisateur correspondant au filtre", className='text-muted')
    
    return html.Div([render_active_user_item(u) for u in users])


def render_pending_users_list(users: list) -> html.Div:
    """Rend la liste des utilisateurs en attente"""
    if not users:
        return html.P("Aucun utilisateur en attente", className='text-muted')
    
    return html.Div([render_pending_user_item(u) for u in users])
