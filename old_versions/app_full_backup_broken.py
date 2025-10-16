#!/usr/bin/env python3
"""
Social Network Analyzer - Version Complète
Avec système de propositions et panel admin
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from database import RelationDB, RELATION_TYPES
from graph import compute_layout, build_graph, make_figure
from admin_components import create_admin_dashboard

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v6.1.1/css/all.css"],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True
)

db = RelationDB()
app.title = "Social Network Analyzer"

# CSS (utiliser le même que app_old.py pour la cohérence)
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-attachment: fixed;
            min-height: 100vh;
        }
        
        .main-container {
            min-height: 100vh;
            display: grid;
            grid-template-columns: 1fr 300px;
            padding: 15px;
            gap: 15px;
        }
        
        .graph-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 15px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
        }
        
        .controls-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            max-height: calc(100vh - 30px);
            overflow-y: auto;
        }
        
        .controls-panel::-webkit-scrollbar { width: 6px; }
        .controls-panel::-webkit-scrollbar-track { background: rgba(0,0,0,0.05); border-radius: 10px; }
        .controls-panel::-webkit-scrollbar-thumb { background: rgba(102, 126, 234, 0.5); border-radius: 10px; }
        
        h3 { color: #1d1d1f; font-size: 24px; font-weight: 700; margin-bottom: 20px; }
        .control-group { margin-bottom: 20px; }
        .control-label { display: block; color: #1d1d1f; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
        
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 18px;
            margin-top: 20px;
            color: white;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        }
        
        .stats-card h5 { font-size: 16px; margin-bottom: 12px; font-weight: 700; }
        .stat-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; }
        .stat-value { font-weight: 700; font-size: 15px; }
        
        .graph-wrapper { flex: 1; min-height: 0; border-radius: 10px; overflow: hidden; }
        
        .btn-custom {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 10px;
            transition: all 0.2s;
        }
        
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-success { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
        
        .btn-admin-discrete {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            font-size: 12px;
            padding: 8px;
        }
        
        .btn-admin-discrete:hover {
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
        }
        
        .pending-badge {
            background: #ff6b6b;
            color: white;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: 700;
            margin-left: 5px;
        }
        
        @media (max-width: 1024px) {
            .main-container { grid-template-columns: 1fr; }
            .controls-panel { order: -1; max-height: none; }
            .graph-container { min-height: 500px; }
        }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
'''

# Layout
app.layout = html.Div([
    # Session et modal - utiliser 'memory' pour éviter les bugs de sessionStorage
    dcc.Store(id='session-store', data={'logged_in': False, 'username': ''}, storage_type='memory'),
    dcc.Store(id='edit-action-store', data={}),  # Store pour les actions de modification
    dcc.Interval(id='refresh-interval', interval=5000, n_intervals=0),
    
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(
                    id='network-graph',
                    config={
                        'displayModeBar': True,
                        'scrollZoom': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                    },
                    style={'height': '100%', 'width': '100%'}
                )
            ], className='graph-wrapper')
        ], className='graph-container'),
        
        html.Div([
            html.H3("📊 Controls"),
            
            html.Div([
                html.Label("Layout Algorithm", className='control-label'),
                dcc.Dropdown(
                    id='layout-dropdown',
                    options=[
                        {'label': '🎯 Community', 'value': 'community'},
                        {'label': '🌸 Spring', 'value': 'spring'},
                        {'label': '🔷 Kamada-Kawai', 'value': 'kk'},
                        {'label': '⭐ Spectral', 'value': 'spectral'},
                    ],
                    value='community',
                    clearable=False,
                )
            ], className='control-group'),
            
            html.Button("➕ Proposer une relation", id='btn-propose', className='btn-custom btn-primary'),
            html.Button("⚙️ Admin", id='btn-admin', className='btn-custom btn-admin-discrete'),
            
            html.Div([
                html.H5("Network Stats"),
                html.Div(id='stats-content')
            ], className='stats-card'),
            
        ], className='controls-panel'),
    ], className='main-container'),
    
    html.Div(id='modal-container'),
])

@app.callback(
    Output('network-graph', 'figure'),
    [Input('layout-dropdown', 'value'),
     Input('refresh-interval', 'n_intervals')]
)
def update_graph(layout_type, n_intervals):
    relations = db.get_all_relations()
    persons = db.get_all_persons()
    
    if not persons:
        fig = go.Figure()
        fig.add_annotation(text="No data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    relations_dict = {}
    for p1, p2, rel_type in relations:
        if p1 not in relations_dict:
            relations_dict[p1] = []
        relations_dict[p1].append((p2, rel_type))
    
    G = build_graph(relations_dict)
    pos = compute_layout(G, mode=layout_type)
    fig = make_figure(G, pos)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        hovermode='closest',
        dragmode='pan',
        uirevision='constant',
    )
    
    return fig

@app.callback(
    Output('stats-content', 'children'),
    Input('refresh-interval', 'n_intervals')
)
def update_stats(n_intervals):
    persons = db.get_all_persons()
    relations = db.get_all_relations()
    pending = db.get_pending_relations()
    
    return html.Div([
        html.Div([html.Span("Persons"), html.Span(f"{len(persons)}", className='stat-value')], className='stat-item'),
        html.Div([html.Span("Relations"), html.Span(f"{len(relations)}", className='stat-value')], className='stat-item'),
        html.Div([
            html.Span("Pending"), 
            html.Span([
                f"{len(pending)}",
                html.Span(f" {len(pending)}", className='pending-badge') if len(pending) > 0 else None
            ], className='stat-value')
        ], className='stat-item'),
    ])

@app.callback(
    Output('modal-container', 'children'),
    [Input('btn-propose', 'n_clicks'),
     Input('btn-admin', 'n_clicks')],
    [State('session-store', 'data')],
    prevent_initial_call=True
)
def show_modal(propose_clicks, admin_clicks, session):
    if not ctx.triggered:
        return None
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # S'assurer que session est un dict valide
    if session is None:
        session = {'logged_in': False, 'username': '', 'remember_me': False}
    
    if trigger == 'btn-propose':
        # Modal de proposition simplifiée
        persons = sorted(db.get_all_persons())
        return dbc.Modal([
            dbc.ModalHeader("➕ Proposer une nouvelle relation"),
            dbc.ModalBody([
                html.P("✨ La relation sera automatiquement symétrisée après approbation", 
                      style={'fontSize': '13px', 'color': '#666'}),
                dbc.Label("Personne 1"),
                dcc.Dropdown(id='modal-p1', options=[{'label': p, 'value': p} for p in persons]),
                html.Br(),
                dbc.Label("Personne 2"),
                dcc.Dropdown(id='modal-p2', options=[{'label': p, 'value': p} for p in persons]),
                html.Br(),
                dbc.Label("Type"),
                dcc.Dropdown(id='modal-type', 
                           options=[{'label': v, 'value': k} for k, v in RELATION_TYPES.items()],
                           value=0),
                html.Div(id='modal-result', style={'marginTop': '15px'})
            ]),
            dbc.ModalFooter([
                dbc.Button("Envoyer", id='modal-submit', color="success"),
                dbc.Button("Fermer", id='modal-close', color="secondary"),
            ])
        ], id='modal', is_open=True, size="lg")
    
    elif trigger == 'btn-admin':
        # Panel admin - vérifier que la session est valide et logged_in est True
        is_logged_in = session.get('logged_in', False) if isinstance(session, dict) else False
        
        if is_logged_in:
            return dbc.Modal([
                dbc.ModalHeader([
                    html.Span("🎯 Admin Dashboard", style={'flex': '1'}),
                    html.Small(f"👤 {session.get('username', '')}", style={'marginRight': '15px', 'color': '#64748b'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                dbc.ModalBody([
                    html.Div(id='admin-dashboard-content', children=create_admin_dashboard(db)),
                ], style={'maxHeight': '70vh', 'overflowY': 'auto'}),
                dbc.ModalFooter([
                    dbc.Button("🚪 Déconnexion", id='logout-btn', color="warning", className='me-2'),
                    dbc.Button("Fermer", id='admin-modal-close', color="secondary"),
                ])
            ], id='admin-modal', is_open=True, size="xl")
        else:
            return dbc.Modal([
                dbc.ModalHeader("🔐 Admin Login"),
                dbc.ModalBody([
                    dbc.Label("Username"),
                    dbc.Input(id='login-user', type='text', placeholder='admin'),
                    html.Br(),
                    dbc.Label("Password"),
                    dbc.Input(id='login-pass', type='password', placeholder='••••••'),
                    html.Div(id='login-result', style={'marginTop': '15px'})
                ]),
                dbc.ModalFooter([
                    dbc.Button("Login", id='login-submit', color="success"),
                    dbc.Button("Annuler", id='modal-close', color="secondary"),
                ])
            ], id='modal', is_open=True)
    
    return None

@app.callback(
    [Output('modal', 'is_open', allow_duplicate=True),
     Output('modal-result', 'children')],
    [Input('modal-submit', 'n_clicks'),
     Input('modal-close', 'n_clicks')],
    [State('modal-p1', 'value'),
     State('modal-p2', 'value'),
     State('modal-type', 'value')],
    prevent_initial_call=True
)
def handle_propose(submit, close, p1, p2, rel_type):
    if not ctx.triggered:
        return False, ""
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger == 'modal-close':
        return False, ""
    
    if trigger == 'modal-submit':
        if not p1 or not p2:
            return True, dbc.Alert("Sélectionnez les deux personnes", color="warning")
        if p1 == p2:
            return True, dbc.Alert("Les personnes doivent être différentes", color="warning")
        
        success = db.submit_pending_relation(p1, p2, rel_type, "user", "")
        if success:
            return False, dbc.Alert("✅ Proposition envoyée !", color="success")
        else:
            return True, dbc.Alert("Cette relation est déjà en attente", color="info")
    
    return False, ""

@app.callback(
    [Output('modal', 'is_open', allow_duplicate=True),
     Output('login-result', 'children'),
     Output('session-store', 'data', allow_duplicate=True)],
    [Input('login-submit', 'n_clicks')],
    [State('login-user', 'value'),
     State('login-pass', 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_login(n, username, password, session):
    if not username or not password:
        return True, dbc.Alert("Entrez vos identifiants", color="warning"), session
    
    if db.verify_admin(username, password):
        session['logged_in'] = True
        session['username'] = username
        
        return False, dbc.Alert("✅ Connecté !", color="success"), session
    else:
        return True, dbc.Alert("❌ Identifiants incorrects", color="danger"), session

# Callback pour gérer la déconnexion
@app.callback(
    [Output('session-store', 'data', allow_duplicate=True),
     Output('modal-container', 'children', allow_duplicate=True)],
    [Input('logout-btn', 'n_clicks')],
    [State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_logout(n_clicks, session):
    # Effacer la session complètement
    session_cleared = {'logged_in': False, 'username': ''}
    
    # Afficher un message de confirmation
    modal = dbc.Modal([
        dbc.ModalHeader("✅ Déconnexion réussie"),
        dbc.ModalBody([
            html.P("Vous avez été déconnecté avec succès."),
            html.P("La session reste active pendant que le navigateur est ouvert.", 
                   style={'fontSize': '13px', 'color': '#666'})
        ]),
        dbc.ModalFooter([
            dbc.Button("OK", id='logout-confirm-close', color="primary"),
        ])
    ], id='logout-modal', is_open=True)
    
    return session_cleared, modal

# Callback pour fermer le modal de confirmation de déconnexion
@app.callback(
    Output('modal-container', 'children', allow_duplicate=True),
    [Input('logout-confirm-close', 'n_clicks')],
    prevent_initial_call=True
)
def close_logout_modal(n_clicks):
    return None

# Callbacks pour l'admin panel - Relations uniquement
@app.callback(
    Output('modal-container', 'children', allow_duplicate=True),
    [Input({'type': 'btn-approve', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-reject', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-delete', 'index': ALL}, 'n_clicks'),
     Input('admin-modal-close', 'n_clicks'),
     Input('logout-btn', 'n_clicks'),
     Input('admin-tabs', 'active_tab')],
    [State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_admin_relations(approve, reject, delete, close_clicks, logout_clicks, active_tab, session):
    if not ctx.triggered:
        return None
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Fermer le panel admin
    if trigger_id == 'admin-modal-close':
        return None
    
    # Déconnexion - géré par un autre callback
    if trigger_id == 'logout-btn':
        raise dash.exceptions.PreventUpdate
    
    # Changement d'onglet - ne rien faire
    if trigger_id == 'admin-tabs':
        raise dash.exceptions.PreventUpdate
    
    # Actions admin
    if not session.get('logged_in'):
        return None
    
    import json
    trigger = json.loads(trigger_id) if trigger_id.startswith('{') else None
    
    if trigger:
        action_type = trigger['type']
        index = trigger['index']
        username = session.get('username', 'admin')
        
        if action_type == 'btn-approve':
            db.approve_relation(index, username, auto_symmetrize=True)
        elif action_type == 'btn-reject':
            db.reject_relation(index, username)
        elif action_type == 'btn-delete':
            parts = index.split('|')
            if len(parts) == 3:
                db.delete_relation(parts[0], parts[1], int(parts[2]), username, auto_symmetrize=True)
        
        # Rouvrir le panel admin avec les données mises à jour
        return dbc.Modal([
            dbc.ModalHeader("🎯 Admin Dashboard", style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'color': 'white'}),
            dbc.ModalBody([
                html.Div(id='admin-dashboard-content', children=create_admin_dashboard(db)),
            ], style={'maxHeight': '70vh', 'overflowY': 'auto', 'background': '#f8f9fa'}),
            dbc.ModalFooter([
                dbc.Button("Fermer", id='admin-modal-close', color="secondary", className='px-4'),
            ], style={'background': '#f8f9fa'})
        ], id='admin-modal', is_open=True, size="xl")
    
    return None

# Callback séparé pour les actions sur les personnes
@app.callback(
    Output('modal-container', 'children', allow_duplicate=True),
    [Input({'type': 'btn-edit-person', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-merge-person', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-delete-person', 'index': ALL}, 'n_clicks')],
    [State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_person_actions(edit_clicks, merge_clicks, delete_clicks, session):
    if not ctx.triggered or not session.get('logged_in'):
        raise dash.exceptions.PreventUpdate
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    import json
    trigger = json.loads(trigger_id) if trigger_id.startswith('{') else None
    
    if not trigger:
        raise dash.exceptions.PreventUpdate
    
    # Vérifier qu'un bouton a vraiment été cliqué (n_clicks > 0)
    action_type = trigger['type']
    person_name = trigger['index']
    
    # Trouver l'index du bouton cliqué et vérifier n_clicks
    clicked = False
    if action_type == 'btn-edit-person':
        for idx, clicks in enumerate(edit_clicks):
            if clicks and clicks > 0:
                clicked = True
                break
    elif action_type == 'btn-merge-person':
        for idx, clicks in enumerate(merge_clicks):
            if clicks and clicks > 0:
                clicked = True
                break
    elif action_type == 'btn-delete-person':
        for idx, clicks in enumerate(delete_clicks):
            if clicks and clicks > 0:
                clicked = True
                break
    
    if not clicked:
        raise dash.exceptions.PreventUpdate
    
    username = session.get('username', 'admin')
    
    if action_type == 'btn-edit-person':
        return create_edit_person_modal(person_name)
    elif action_type == 'btn-merge-person':
        return create_merge_person_modal(person_name)
    elif action_type == 'btn-delete-person':
        if db.delete_person(person_name, username):
            return dbc.Modal([
                dbc.ModalHeader("🎯 Admin Dashboard", style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'color': 'white'}),
                dbc.ModalBody([
                    dbc.Alert(f"✅ {person_name} a été supprimé(e) avec toutes ses relations", color="success", className='mb-3'),
                    html.Div(id='admin-dashboard-content', children=create_admin_dashboard(db)),
                ], style={'maxHeight': '70vh', 'overflowY': 'auto', 'background': '#f8f9fa'}),
                dbc.ModalFooter([
                    dbc.Button("Fermer", id='admin-modal-close', color="secondary", className='px-4'),
                ], style={'background': '#f8f9fa'})
            ], id='admin-modal', is_open=True, size="xl")
    
    raise dash.exceptions.PreventUpdate

def create_edit_person_modal(person_name):
    """Crée une modale moderne pour modifier une personne."""
    # Récupérer les infos actuelles
    persons_detailed = db.get_all_persons_detailed()
    person_info = next((p for p in persons_detailed if p['name'] == person_name), None)
    
    current_gender = person_info['gender'] if person_info else None
    current_orientation = person_info['sexual_orientation'] if person_info else None
    
    # Utiliser un ID unique basé sur le nom pour éviter les conflits
    modal_id = f'edit-person-modal-{hash(person_name)}'
    
    return dbc.Modal([
        dbc.ModalHeader([
            html.I(className="fas fa-user-edit", style={'marginRight': '10px'}),
            f"Modifier {person_name}"
        ], style={
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'color': 'white',
            'fontWeight': '600'
        }),
        dbc.ModalBody([
            html.Div([
                html.Label([
                    html.I(className="fas fa-signature", style={'marginRight': '8px', 'color': '#667eea'}),
                    "Nouveau nom"
                ], style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dbc.Input(
                    id={'type': 'edit-person-newname', 'index': person_name},
                    type='text',
                    value=person_name,
                    style={
                        'borderRadius': '8px',
                        'border': '2px solid #e2e8f0',
                        'padding': '10px 12px',
                        'fontSize': '14px'
                    }
                ),
            ], className='mb-3'),
            
            html.Div([
                html.Label([
                    html.I(className="fas fa-venus-mars", style={'marginRight': '8px', 'color': '#667eea'}),
                    "Genre"
                ], style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Dropdown(
                    id={'type': 'edit-person-gender', 'index': person_name},
                    options=[
                        {'label': '👨 Homme', 'value': 'M'},
                        {'label': '👩 Femme', 'value': 'F'},
                        {'label': '❓ Non spécifié', 'value': '?'}
                    ],
                    value=current_gender,
                    clearable=True,
                    style={'borderRadius': '8px'}
                ),
            ], className='mb-3'),
            
            html.Div([
                html.Label([
                    html.I(className="fas fa-heart", style={'marginRight': '8px', 'color': '#667eea'}),
                    "Orientation sexuelle"
                ], style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Dropdown(
                    id={'type': 'edit-person-orientation', 'index': person_name},
                    options=[
                        {'label': '💑 Hétéro', 'value': 'straight'},
                        {'label': '🌈 Gay', 'value': 'gay'},
                        {'label': '🌈 Lesbienne', 'value': 'lesbian'},
                        {'label': '💜 Bisexuel(le)', 'value': 'bi'},
                        {'label': '❓ Non spécifié', 'value': '?'}
                    ],
                    value=current_orientation,
                    clearable=True,
                    style={'borderRadius': '8px'}
                ),
            ], className='mb-3'),
            
            html.Div(id={'type': 'edit-person-result', 'index': person_name}),
        ], style={'padding': '20px', 'background': '#f8fafc'}),
        dbc.ModalFooter([
            dbc.Button([
                html.I(className="fas fa-save", style={'marginRight': '8px'}),
                "Enregistrer"
            ], id={'type': 'edit-person-submit', 'index': person_name}, n_clicks=0, style={
                'background': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                'border': 'none',
                'borderRadius': '8px',
                'padding': '10px 20px',
                'fontWeight': '600'
            }),
            dbc.Button([
                html.I(className="fas fa-times", style={'marginRight': '8px'}),
                "Annuler"
            ], id={'type': 'edit-person-cancel', 'index': person_name}, n_clicks=0, style={
                'background': '#64748b',
                'border': 'none',
                'borderRadius': '8px',
                'padding': '10px 20px',
                'fontWeight': '600'
            }),
        ], style={'background': '#f8fafc', 'borderTop': '1px solid #e2e8f0'})
    ], id=modal_id, is_open=True, size="md", centered=True)

def create_merge_person_modal(person_name):
    """Crée une modale moderne pour fusionner une personne avec une autre."""
    all_persons = sorted(db.get_all_persons())
    # Retirer la personne actuelle de la liste
    other_persons = [p for p in all_persons if p != person_name]
    
    # Utiliser un ID unique basé sur le nom
    modal_id = f'merge-person-modal-{hash(person_name)}'
    
    return dbc.Modal([
        dbc.ModalHeader([
            html.I(className="fas fa-code-branch", style={'marginRight': '10px'}),
            f"Fusionner {person_name}"
        ], style={
            'background': 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
            'color': 'white',
            'fontWeight': '600'
        }),
        dbc.ModalBody([
            html.Div([
                html.I(className="fas fa-exclamation-triangle", style={
                    'fontSize': '48px',
                    'color': '#f59e0b',
                    'marginBottom': '15px'
                }),
                html.P([
                    "Cette action va transférer toutes les relations de ",
                    html.Strong(person_name, style={'color': '#f59e0b'}),
                    " vers la personne sélectionnée, puis supprimer ",
                    html.Strong(person_name, style={'color': '#ef4444'}),
                    "."
                ], style={
                    'fontSize': '14px',
                    'color': '#475569',
                    'marginBottom': '20px',
                    'lineHeight': '1.6'
                })
            ], style={'textAlign': 'center'}),
            
            html.Div([
                html.Label([
                    html.I(className="fas fa-user-check", style={'marginRight': '8px', 'color': '#f59e0b'}),
                    f"Fusionner {person_name} dans :"
                ], style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Dropdown(
                    id={'type': 'merge-person-target', 'index': person_name},
                    options=[{'label': p, 'value': p} for p in other_persons],
                    placeholder="Sélectionner la personne principale...",
                    style={'borderRadius': '8px'}
                ),
            ], className='mb-3'),
            
            html.Div(id={'type': 'merge-person-result', 'index': person_name}),
        ], style={'padding': '20px', 'background': '#fffbeb'}),
        dbc.ModalFooter([
            dbc.Button([
                html.I(className="fas fa-code-branch", style={'marginRight': '8px'}),
                "Fusionner"
            ], id={'type': 'merge-person-submit', 'index': person_name}, n_clicks=0, style={
                'background': 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                'border': 'none',
                'borderRadius': '8px',
                'padding': '10px 20px',
                'fontWeight': '600'
            }),
            dbc.Button([
                html.I(className="fas fa-times", style={'marginRight': '8px'}),
                "Annuler"
            ], id={'type': 'merge-person-cancel', 'index': person_name}, n_clicks=0, style={
                'background': '#64748b',
                'border': 'none',
                'borderRadius': '8px',
                'padding': '10px 20px',
                'fontWeight': '600'
            }),
        ], style={'background': '#fffbeb', 'borderTop': '1px solid #fde68a'})
    ], id=modal_id, is_open=True, size="md", centered=True)

# Callback pour modifier une personne avec pattern matching
@app.callback(
    Output('modal-container', 'children', allow_duplicate=True),
    [Input({'type': 'edit-person-submit', 'index': ALL}, 'n_clicks'),
     Input({'type': 'edit-person-cancel', 'index': ALL}, 'n_clicks')],
    [State({'type': 'edit-person-newname', 'index': ALL}, 'value'),
     State({'type': 'edit-person-gender', 'index': ALL}, 'value'),
     State({'type': 'edit-person-orientation', 'index': ALL}, 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_edit_person(submit_clicks, cancel_clicks, new_names, genders, orientations, session):
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    import json
    trigger = json.loads(trigger_id) if trigger_id.startswith('{') else None
    
    if not trigger:
        raise dash.exceptions.PreventUpdate
    
    action_type = trigger['type']
    old_name = trigger['index']
    
    # Trouver l'index correspondant au nom
    # Les inputs sont créés avec index=person_name, donc on cherche cet index
    try:
        # Pour submit
        if action_type == 'edit-person-submit':
            idx = None
            for i, clicks in enumerate(submit_clicks):
                if clicks and clicks > 0:
                    # Vérifier que c'est bien le bon bouton qui a été cliqué
                    if i < len(new_names):
                        idx = i
                        break
            
            if idx is None:
                raise dash.exceptions.PreventUpdate
            
            new_name = new_names[idx] if idx < len(new_names) else old_name
            gender = genders[idx] if idx < len(genders) else None
            orientation = orientations[idx] if idx < len(orientations) else None
            
        # Pour cancel
        elif action_type == 'edit-person-cancel':
            # Juste retourner au panel admin
            return dbc.Modal([
                dbc.ModalHeader("🎯 Admin Dashboard", style={
                    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'color': 'white'
                }),
                dbc.ModalBody([
                    html.Div(id='admin-dashboard-content', children=create_admin_dashboard(db)),
                ], style={'maxHeight': '70vh', 'overflowY': 'auto', 'background': '#f8f9fa'}),
                dbc.ModalFooter([
                    dbc.Button("Fermer", id='admin-modal-close', color="secondary", className='px-4'),
                ], style={'background': '#f8f9fa'})
            ], id='admin-modal', is_open=True, size="xl")
        else:
            raise dash.exceptions.PreventUpdate
            
    except Exception as e:
        print(f"Erreur dans handle_edit_person: {e}")
        raise dash.exceptions.PreventUpdate
    
    # Enregistrer les modifications
    if not session.get('logged_in'):
        raise dash.exceptions.PreventUpdate
    
    username = session.get('username', 'admin')
    success = True
    final_name = old_name
    
    # Renommer si le nom a changé
    if new_name and new_name != old_name:
        success = db.rename_person(old_name, new_name, username)
        if not success:
            # Nom déjà existant - réafficher la modale avec erreur
            return create_edit_person_modal(old_name)
        final_name = new_name
    
    # Mettre à jour genre et orientation (même si le nom n'a pas changé)
    db.update_person_info(final_name, gender, orientation, username)
    
    # Rouvrir le panel admin avec message de succès
    return dbc.Modal([
        dbc.ModalHeader("🎯 Admin Dashboard", style={
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'color': 'white'
        }),
        dbc.ModalBody([
            dbc.Alert([
                html.I(className="fas fa-check-circle", style={'marginRight': '10px'}),
                f"✅ {final_name} mis(e) à jour avec succès!"
            ], color="success", className='mb-3'),
            html.Div(id='admin-dashboard-content', children=create_admin_dashboard(db)),
        ], style={'maxHeight': '70vh', 'overflowY': 'auto', 'background': '#f8f9fa'}),
        dbc.ModalFooter([
            dbc.Button("Fermer", id='admin-modal-close', color="secondary", className='px-4'),
        ], style={'background': '#f8f9fa'})
    ], id='admin-modal', is_open=True, size="xl")

# Callback pour fusionner des personnes
@app.callback(
    Output('modal-container', 'children', allow_duplicate=True),
    [Input({'type': 'merge-person-submit', 'index': ALL}, 'n_clicks'),
     Input({'type': 'merge-person-cancel', 'index': ALL}, 'n_clicks')],
    [State({'type': 'merge-person-target', 'index': ALL}, 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_merge_person(submit_clicks_list, cancel_clicks_list, target_names, session):
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    trigger_info = ctx.triggered[0]['prop_id']
    
    # Vérifier si c'est un bouton annuler qui a été cliqué
    if 'merge-person-cancel' in trigger_info:
        # Retour au panel admin
        return dbc.Modal([
            dbc.ModalHeader("🎯 Admin Dashboard", style={
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'color': 'white'
            }),
            dbc.ModalBody([
                html.Div(id='admin-dashboard-content', children=create_admin_dashboard(db)),
            ], style={'maxHeight': '70vh', 'overflowY': 'auto', 'background': '#f8f9fa'}),
            dbc.ModalFooter([
                dbc.Button("Fermer", id='admin-modal-close', color="secondary", className='px-4'),
            ], style={'background': '#f8f9fa'})
        ], id='admin-modal', is_open=True, size="xl")
    
    # Fusionner les personnes
    if 'merge-person-submit' in trigger_info:
        if not session.get('logged_in'):
            raise dash.exceptions.PreventUpdate
        
        # Trouver quel bouton a été cliqué
        clicked_idx = None
        for idx, clicks in enumerate(submit_clicks_list):
            if clicks and clicks > 0:
                clicked_idx = idx
                break
        
        if clicked_idx is None:
            raise dash.exceptions.PreventUpdate
        
        # Extraire le nom de la personne depuis l'ID du bouton cliqué
        import json
        trigger_dict = json.loads(trigger_info.split('.')[0])
        source_name = trigger_dict['index']
        
        # Récupérer la cible sélectionnée
        target_name = target_names[clicked_idx] if clicked_idx < len(target_names) else None
        
        if not target_name:
            # Pas de cible sélectionnée - réafficher la modale avec un message
            return create_merge_person_modal(source_name)
        
        username = session.get('username', 'admin')
        success = db.merge_persons(target_name, source_name, username)
        
        if success:
            # Rouvrir le panel admin avec message de succès
            return dbc.Modal([
                dbc.ModalHeader("🎯 Admin Dashboard", style={
                    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'color': 'white'
                }),
                dbc.ModalBody([
                    dbc.Alert([
                        html.I(className="fas fa-check-circle", style={'marginRight': '10px'}),
                        f"✅ {source_name} a été fusionné(e) dans {target_name}!"
                    ], color="success", className='mb-3'),
                    html.Div(id='admin-dashboard-content', children=create_admin_dashboard(db)),
                ], style={'maxHeight': '70vh', 'overflowY': 'auto', 'background': '#f8f9fa'}),
                dbc.ModalFooter([
                    dbc.Button("Fermer", id='admin-modal-close', color="secondary", className='px-4'),
                ], style={'background': '#f8f9fa'})
            ], id='admin-modal', is_open=True, size="xl")
        else:
            # Erreur de fusion - réafficher la modale
            return create_merge_person_modal(source_name)
    
    raise dash.exceptions.PreventUpdate

if __name__ == '__main__':
    db.add_admin("admin", "admin123")
    
    persons = db.get_all_persons()
    relations = db.get_all_relations()
    
    print("\n" + "="*70)
    print("  🌐 SOCIAL NETWORK ANALYZER - Full Version")
    print("="*70)
    print(f"\n  📊 Données: {len(persons)} personnes, {len(relations)} relations")
    print(f"  🔐 Admin: admin / admin123")
    print(f"  🚀 URL: http://localhost:8051")
    print(f"\n  ⚡ Fonctionnalités:")
    print(f"     • Propositions utilisateurs")
    print(f"     • Panel admin complet")
    print(f"     • Symétrie automatique\n")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=8051, debug=True)
