#!/usr/bin/env python3
"""
Social Network Analyzer - Version Stable
Sans système "se souvenir" - Version qui fonctionnait avant
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
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

# CSS identique à app_old.py
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
        
        .action-btn {
            width: 100%;
            margin-bottom: 12px;
            padding: 12px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .graph-wrapper { flex: 1; min-height: 0; border-radius: 10px; overflow: hidden; }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
'''

# Layout simplifié
app.layout = html.Div([
    # Store simple pour la session - pas de persistance
    dcc.Store(id='session-store', data={'logged_in': False}),
    
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(
                    id='network-graph',
                    config={
                        'displayModeBar': True,
                        'scrollZoom': True,
                        'displaylogo': False,
                    },
                    style={'height': '100%', 'width': '100%'}
                )
            ], className='graph-wrapper')
        ], className='graph-container'),
        
        html.Div([
            html.H3("📊 Controls"),
            
            # Boutons d'action
            html.Button("➕ Proposer une relation", id='btn-propose', className='action-btn', 
                       style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'color': 'white'}),
            html.Button("🎯 Admin", id='btn-admin', className='action-btn',
                       style={'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 'color': 'white'}),
            
            html.Hr(style={'margin': '20px 0'}),
            
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
            
            html.Div([
                html.Label("Color By", className='control-label'),
                dcc.Dropdown(
                    id='color-dropdown',
                    options=[
                        {'label': '🎨 Community', 'value': 'community'},
                        {'label': '📈 Degree', 'value': 'degree'},
                    ],
                    value='community',
                    clearable=False,
                )
            ], className='control-group'),
            
            html.Div([
                html.H5("Network Stats"),
                html.Div(id='stats-content')
            ], className='stats-card'),
            
        ], className='controls-panel'),
        
    ], className='main-container'),
    
    # Container pour les modals
    html.Div(id='modal-container'),
    
    dcc.Interval(id='refresh-interval', interval=5000, n_intervals=0),
])

# Callback pour le graphique
@app.callback(
    Output('network-graph', 'figure'),
    [Input('layout-dropdown', 'value'),
     Input('color-dropdown', 'value'),
     Input('refresh-interval', 'n_intervals')]
)
def update_graph(layout_type, color_by, n_intervals):
    relations = db.get_all_relations()
    
    if not relations:
        import plotly.graph_objects as go
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
    fig = make_figure(G, pos, color_by=color_by)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        hovermode='closest',
    )
    
    return fig

# Callback pour les stats
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
        html.Div([html.Span("Pending"), html.Span(f"{len(pending)}", className='stat-value')], className='stat-item'),
    ])

# Callback pour afficher les modals
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
    
    if trigger == 'btn-propose':
        persons = sorted([p['name'] for p in db.get_all_persons()])
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
        # Vérifier si l'utilisateur est connecté
        if session and session.get('logged_in'):
            # Afficher le panel admin
            return dbc.Modal([
                dbc.ModalHeader("🎯 Admin Dashboard"),
                dbc.ModalBody([
                    create_admin_dashboard(db)
                ], style={'maxHeight': '70vh', 'overflowY': 'auto'}),
                dbc.ModalFooter([
                    dbc.Button("🚪 Déconnexion", id='btn-logout', color="warning"),
                    dbc.Button("Fermer", id='modal-close', color="secondary"),
                ])
            ], id='modal', is_open=True, size="xl")
        else:
            # Afficher le formulaire de connexion
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

# Callback pour gérer la proposition
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

# Callback pour gérer le login
@app.callback(
    [Output('modal', 'is_open', allow_duplicate=True),
     Output('login-result', 'children'),
     Output('session-store', 'data')],
    [Input('login-submit', 'n_clicks')],
    [State('login-user', 'value'),
     State('login-pass', 'value')],
    prevent_initial_call=True
)
def handle_login(n, username, password):
    if not username or not password:
        return True, dbc.Alert("Entrez vos identifiants", color="warning"), {'logged_in': False}
    
    if db.verify_admin(username, password):
        return False, None, {'logged_in': True, 'username': username}
    else:
        return True, dbc.Alert("❌ Identifiants incorrects", color="danger"), {'logged_in': False}

# Callback pour gérer la déconnexion
@app.callback(
    [Output('session-store', 'data', allow_duplicate=True),
     Output('modal', 'is_open', allow_duplicate=True)],
    [Input('btn-logout', 'n_clicks')],
    prevent_initial_call=True
)
def handle_logout(n):
    return {'logged_in': False}, False

# Callbacks pour les actions admin (approuver, rejeter, supprimer)
@app.callback(
    Output('modal-container', 'children', allow_duplicate=True),
    [Input({'type': 'btn-approve', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-reject', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-delete', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def handle_admin_actions(approve, reject, delete):
    if not ctx.triggered:
        return None
    
    trigger = ctx.triggered_id
    if not trigger:
        return None
    
    action_type = trigger['type']
    index = trigger['index']
    
    if action_type == 'btn-approve':
        db.approve_pending_relation(index, "admin")
    elif action_type == 'btn-reject':
        db.reject_pending_relation(index, "admin")
    elif action_type == 'btn-delete':
        # Format: "person1|person2|type"
        parts = index.split('|')
        if len(parts) == 3:
            db.delete_relation(parts[0], parts[1], int(parts[2]), "admin")
    
    # Retourner None pour ne pas changer le modal
    raise dash.exceptions.PreventUpdate

if __name__ == '__main__':
    persons = db.get_all_persons()
    relations = db.get_all_relations()
    
    print("\n" + "="*70)
    print("  🌐 SOCIAL NETWORK ANALYZER - Version Stable")
    print("="*70)
    print(f"\n  📊 Données: {len(persons)} personnes, {len(relations)} relations")
    print(f"  🔐 Admin: admin / admin123")
    print(f"  🚀 URL: http://localhost:8051\n")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=8051, debug=True)
