#!/usr/bin/env python3
"""
Social Network Analyzer - Version DEBUG
Pour identifier le bug du menu admin
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, ctx, no_update
import dash_bootstrap_components as dbc
from database import RelationDB, RELATION_TYPES
from graph import compute_layout, build_graph, make_figure
from admin_components import create_admin_dashboard
import datetime

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v6.1.1/css/all.css"],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True
)

db = RelationDB()
app.title = "Social Network Analyzer"

def log(message):
    """Helper pour logger avec timestamp"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

# CSS moderne (simplifié)
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
            display: flex;
            flex-direction: column;
        }
        .controls-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            max-height: calc(100vh - 30px);
            overflow-y: auto;
        }
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

# Layout
app.layout = html.Div([
    # Store pour la session
    dcc.Store(id='session-store', data={'logged_in': False, 'username': ''}, storage_type='memory'),
    
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(
                    id='network-graph',
                    config={'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False},
                    style={'height': '100%', 'width': '100%'}
                )
            ], className='graph-wrapper')
        ], className='graph-container'),
        
        html.Div([
            html.H3("📊 Controls"),
            
            # Boutons d'action
            html.Button("➕ Proposer une relation", id='btn-propose', n_clicks=0, className='action-btn', 
                       style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'color': 'white'}),
            html.Button("🎯 Admin", id='btn-admin', n_clicks=0, className='action-btn',
                       style={'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 'color': 'white'}),
            
            html.Hr(style={'margin': '20px 0'}),
            
            html.Div([
                html.Label("Layout Algorithm", className='control-label'),
                dcc.Dropdown(
                    id='layout-dropdown',
                    options=[
                        {'label': '🎯 Community', 'value': 'community'},
                        {'label': '🌸 Spring', 'value': 'spring'},
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

# CALLBACK: Graphique
@app.callback(
    Output('network-graph', 'figure'),
    [Input('layout-dropdown', 'value'),
     Input('refresh-interval', 'n_intervals')]
)
def update_graph(layout_type, n_intervals):
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
    fig = make_figure(G, pos)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        hovermode='closest',
    )
    return fig

# CALLBACK: Stats
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

# CALLBACK: Afficher modals - AVEC DEBUG
@app.callback(
    Output('modal-container', 'children'),
    [Input('btn-propose', 'n_clicks'),
     Input('btn-admin', 'n_clicks')],
    [State('session-store', 'data')],
    prevent_initial_call=True
)
def show_modal(propose_clicks, admin_clicks, session):
    """Affiche le modal approprié selon le bouton cliqué"""
    log(f"🔹 show_modal CALLED")
    log(f"   Triggered: {ctx.triggered}")
    log(f"   Session: {session}")
    log(f"   btn-propose n_clicks: {propose_clicks}")
    log(f"   btn-admin n_clicks: {admin_clicks}")
    
    if not ctx.triggered:
        log(f"   ❌ No trigger - returning no_update")
        return no_update
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    log(f"   ✅ Trigger: {trigger}")
    
    # S'assurer que session est valide
    if not isinstance(session, dict):
        log(f"   ⚠️  Session invalid, creating default")
        session = {'logged_in': False, 'username': ''}
    
    # PROPOSITION
    if trigger == 'btn-propose':
        log(f"   📝 Creating PROPOSE modal")
        persons = sorted([p['name'] for p in db.get_all_persons()])
        return dbc.Modal([
            dbc.ModalHeader("➕ Proposer une nouvelle relation"),
            dbc.ModalBody([
                html.P("✨ La relation sera automatiquement symétrisée après approbation"),
                dbc.Label("Personne 1"),
                dcc.Dropdown(id='propose-p1', options=[{'label': p, 'value': p} for p in persons]),
                html.Br(),
                dbc.Label("Personne 2"),
                dcc.Dropdown(id='propose-p2', options=[{'label': p, 'value': p} for p in persons]),
                html.Br(),
                dbc.Label("Type"),
                dcc.Dropdown(id='propose-type', 
                           options=[{'label': v, 'value': k} for k, v in RELATION_TYPES.items()],
                           value=0),
                html.Div(id='propose-result')
            ]),
            dbc.ModalFooter([
                dbc.Button("Envoyer", id='propose-submit', color="success", n_clicks=0),
                dbc.Button("Fermer", id='propose-close', color="secondary", n_clicks=0),
            ])
        ], id='propose-modal', is_open=True, size="lg")
    
    # ADMIN
    elif trigger == 'btn-admin':
        is_logged = session.get('logged_in', False)
        log(f"   🎯 Admin button - logged_in={is_logged}")
        
        if is_logged:
            log(f"   ✅ User IS logged in - showing ADMIN PANEL")
            return dbc.Modal([
                dbc.ModalHeader([
                    html.Span("🎯 Admin Dashboard", style={'flex': '1'}),
                    html.Small(f"👤 {session.get('username', '')}", 
                             style={'marginRight': '15px', 'color': '#64748b'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                dbc.ModalBody([
                    create_admin_dashboard(db)
                ], style={'maxHeight': '70vh', 'overflowY': 'auto'}),
                dbc.ModalFooter([
                    dbc.Button("🚪 Déconnexion", id='admin-logout', color="warning", n_clicks=0),
                    dbc.Button("Fermer", id='admin-close', color="secondary", n_clicks=0),
                ])
            ], id='admin-modal', is_open=True, size="xl")
        else:
            log(f"   ❌ User NOT logged in - showing LOGIN")
            return dbc.Modal([
                dbc.ModalHeader("🔐 Admin Login"),
                dbc.ModalBody([
                    dbc.Label("Username"),
                    dbc.Input(id='login-username', type='text', placeholder='admin', value=''),
                    html.Br(),
                    dbc.Label("Password"),
                    dbc.Input(id='login-password', type='password', placeholder='••••••', value=''),
                    html.Div(id='login-feedback')
                ]),
                dbc.ModalFooter([
                    dbc.Button("Login", id='login-submit', color="success", n_clicks=0),
                    dbc.Button("Annuler", id='login-cancel', color="secondary", n_clicks=0),
                ])
            ], id='login-modal', is_open=True)
    
    log(f"   ⚠️  No matching trigger - returning no_update")
    return no_update

# CALLBACK: Login - AVEC DEBUG
@app.callback(
    [Output('login-modal', 'is_open'),
     Output('login-feedback', 'children'),
     Output('session-store', 'data'),
     Output('modal-container', 'children', allow_duplicate=True)],
    [Input('login-submit', 'n_clicks'),
     Input('login-cancel', 'n_clicks')],
    [State('login-username', 'value'),
     State('login-password', 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_login(submit, cancel, username, password, current_session):
    log(f"🔑 handle_login CALLED")
    log(f"   Triggered: {ctx.triggered}")
    log(f"   Username: {username}")
    log(f"   Current session: {current_session}")
    
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    log(f"   Trigger: {trigger}")
    
    if trigger == 'login-cancel':
        log(f"   ❌ Cancel - closing modal")
        return False, "", {'logged_in': False, 'username': ''}, no_update
    
    if trigger == 'login-submit':
        if not username or not password:
            log(f"   ⚠️  Missing credentials")
            return True, dbc.Alert("Entrez vos identifiants", color="warning"), {'logged_in': False, 'username': ''}, no_update
        
        if db.verify_admin(username, password):
            log(f"   ✅ Login SUCCESS - creating session and opening admin panel")
            new_session = {'logged_in': True, 'username': username}
            
            # Créer directement le panel admin
            admin_panel = dbc.Modal([
                dbc.ModalHeader([
                    html.Span("🎯 Admin Dashboard", style={'flex': '1'}),
                    html.Small(f"👤 {username}", style={'marginRight': '15px', 'color': '#64748b'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                dbc.ModalBody([
                    create_admin_dashboard(db)
                ], style={'maxHeight': '70vh', 'overflowY': 'auto'}),
                dbc.ModalFooter([
                    dbc.Button("🚪 Déconnexion", id='admin-logout', color="warning", n_clicks=0),
                    dbc.Button("Fermer", id='admin-close', color="secondary", n_clicks=0),
                ])
            ], id='admin-modal', is_open=True, size="xl")
            
            log(f"   📦 Returning: login_modal=False, new_session={new_session}, admin_panel created")
            return False, None, new_session, admin_panel
        else:
            log(f"   ❌ Login FAILED - wrong credentials")
            return True, dbc.Alert("❌ Identifiants incorrects", color="danger"), {'logged_in': False, 'username': ''}, no_update
    
    return no_update, no_update, no_update, no_update

# CALLBACK: Logout - AVEC DEBUG
@app.callback(
    [Output('session-store', 'data', allow_duplicate=True),
     Output('admin-modal', 'is_open')],
    [Input('admin-logout', 'n_clicks')],
    prevent_initial_call=True
)
def handle_logout(n):
    log(f"🚪 handle_logout CALLED")
    log(f"   Clearing session and closing modal")
    return {'logged_in': False, 'username': ''}, False

# CALLBACK: Fermer admin - AVEC DEBUG
@app.callback(
    Output('admin-modal', 'is_open', allow_duplicate=True),
    [Input('admin-close', 'n_clicks')],
    [State('session-store', 'data')],
    prevent_initial_call=True
)
def close_admin_modal(n, session):
    log(f"❌ close_admin_modal CALLED")
    log(f"   Session at close: {session}")
    log(f"   Closing modal WITHOUT logout")
    return False

# CALLBACK: Actions admin - AVEC DEBUG
@app.callback(
    Output('modal-container', 'children', allow_duplicate=True),
    [Input({'type': 'btn-approve', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-reject', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-delete', 'index': ALL}, 'n_clicks')],
    [State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_admin_actions(approve, reject, delete, session):
    log(f"⚙️  handle_admin_actions CALLED")
    
    if not ctx.triggered:
        return no_update
    
    trigger = ctx.triggered_id
    if not trigger:
        return no_update
    
    action_type = trigger['type']
    index = trigger['index']
    
    log(f"   Action: {action_type} on {index}")
    
    # Exécuter l'action
    if action_type == 'btn-approve':
        db.approve_pending_relation(index, "admin")
    elif action_type == 'btn-reject':
        db.reject_pending_relation(index, "admin")
    elif action_type == 'btn-delete':
        parts = index.split('|')
        if len(parts) == 3:
            db.delete_relation(parts[0], parts[1], int(parts[2]), "admin")
    
    log(f"   Refreshing admin panel")
    
    # Rafraîchir le panel admin
    admin_panel = dbc.Modal([
        dbc.ModalHeader([
            html.Span("🎯 Admin Dashboard", style={'flex': '1'}),
            html.Small(f"👤 {session.get('username', '')}", 
                     style={'marginRight': '15px', 'color': '#64748b'})
        ], style={'display': 'flex', 'alignItems': 'center'}),
        dbc.ModalBody([
            create_admin_dashboard(db)
        ], style={'maxHeight': '70vh', 'overflowY': 'auto'}),
        dbc.ModalFooter([
            dbc.Button("🚪 Déconnexion", id='admin-logout', color="warning", n_clicks=0),
            dbc.Button("Fermer", id='admin-close', color="secondary", n_clicks=0),
        ])
    ], id='admin-modal', is_open=True, size="xl")
    
    return admin_panel

if __name__ == '__main__':
    persons = db.get_all_persons()
    relations = db.get_all_relations()
    
    print("\n" + "="*70)
    print("  🔍 SOCIAL NETWORK ANALYZER - DEBUG MODE")
    print("="*70)
    print(f"\n  📊 Données: {len(persons)} personnes, {len(relations)} relations")
    print(f"  🔐 Admin: admin / admin123")
    print(f"  🚀 URL: http://localhost:8051")
    print(f"\n  🐛 DEBUG MODE ACTIVÉ - Logs détaillés dans le terminal\n")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=8051, debug=True)
