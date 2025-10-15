#!/usr/bin/env python3"""

"""Social Network Analyzer - Version Complète avec Admin"""Application Dash - Graphe Social

Version propre et fonctionnelle

import dash"""

from dash import dcc, html, Input, Output, State, ALL, ctxfrom __future__ import annotations

import dash_bootstrap_components as dbcimport networkx as nx

import plotly.graph_objects as goimport dash

from database import RelationDB, RELATION_TYPESfrom dash import dcc, html, Input, Output, State, ctx

from graph import compute_layout, build_graph, make_figurefrom dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc

app = dash.Dash(

    __name__,from database import RelationDB, RELATION_TYPES

    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v6.1.1/css/all.css"],from dashboard import make_graph_figure

    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],

    suppress_callback_exceptions=True# Initialiser la base de données

)db = RelationDB()



db = RelationDB()# Configuration de l'app

app.title = "Social Network Analyzer"app = dash.Dash(

    __name__,

# État de session (simplifié pour démo, utiliser dcc.Store en production)    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],

session_state = {'logged_in': False, 'username': None}    suppress_callback_exceptions=True,

)

# CSS moderne

app.index_string = '''app.title = "Social Network Analyzer"

<!DOCTYPE html>

<html>print("✓ App initialisée")

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
            grid-template-columns: 1fr 320px;
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
        
        h3 { color: #1d1d1f; font-size: 22px; font-weight: 700; margin-bottom: 20px; }
        h5 { color: #1d1d1f; font-size: 16px; font-weight: 600; margin: 15px 0 10px 0; }
        
        .control-group { margin-bottom: 15px; }
        .control-label { display: block; color: #1d1d1f; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
        
        .btn-custom {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            padding: 10px;
            margin-bottom: 10px;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-primary-custom {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .btn-success-custom {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        
        .btn-danger-custom {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
            color: white;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        }
        
        .stats-card h5 { font-size: 14px; margin-bottom: 10px; color: white; }
        .stat-item { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px; }
        .stat-value { font-weight: 700; font-size: 14px; }
        
        .graph-wrapper { flex: 1; min-height: 0; border-radius: 10px; overflow: hidden; }
        
        .pending-badge {
            background: #ff6b6b;
            color: white;
            border-radius: 12px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: 700;
            margin-left: 8px;
        }
        
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        }
        
        .modal-content {
            background: white;
            border-radius: 16px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .relation-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .relation-info { flex: 1; }
        .relation-actions { display: flex; gap: 5px; }
        
        .btn-sm {
            padding: 5px 10px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
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

# Layout principal
app.layout = html.Div([
    # Store pour l'état de session
    dcc.Store(id='session-store', data={'logged_in': False, 'username': ''}),
    dcc.Interval(id='refresh-interval', interval=5000, n_intervals=0),
    
    html.Div([
        # Graphe
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
        
        # Panneau de contrôle
        html.Div([
            html.H3("📊 Controls"),
            
            # Layout
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
            
            # Bouton proposer une relation
            html.Div([
                html.Button(
                    "➕ Proposer une relation",
                    id='btn-propose',
                    className='btn-custom btn-primary-custom'
                )
            ]),
            
            # Bouton Admin
            html.Div([
                html.Button(
                    [html.I(className="fas fa-lock"), " Admin Panel"],
                    id='btn-admin',
                    className='btn-custom btn-success-custom'
                )
            ]),
            
            # Stats
            html.Div([
                html.H5("Network Stats"),
                html.Div(id='stats-content')
            ], className='stats-card'),
            
        ], className='controls-panel'),
        
    ], className='main-container'),
    
    # Modals
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
        fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig
    
    # Convert relations to graph format
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
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=False),
        hovermode='closest',
        dragmode='pan',
        uirevision='constant',
        transition={'duration': 0},
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
                html.Span(f"{len(pending)}", className='pending-badge') if len(pending) > 0 else None
            ], className='stat-value')
        ], className='stat-item'),
    ])

@app.callback(
    Output('modal-container', 'children'),
    [Input('btn-propose', 'n_clicks'),
     Input('btn-admin', 'n_clicks')],
    prevent_initial_call=True
)
def open_modal(propose_clicks, admin_clicks):
    if not ctx.triggered:
        return None
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-propose':
        return create_propose_modal()
    elif button_id == 'btn-admin':
        return create_admin_modal()
    
    return None

def create_propose_modal():
    """Modal pour proposer une nouvelle relation"""
    persons = db.get_all_persons()
    
    return html.Div([
        html.Div([
            html.H3("➕ Proposer une nouvelle relation"),
            
            html.Div([
                html.Label("Personne 1", className='control-label'),
                dcc.Dropdown(
                    id='propose-person1',
                    options=[{'label': p, 'value': p} for p in sorted(persons)],
                    placeholder="Sélectionner...",
                    style={'marginBottom': '15px'}
                ),
                
                html.Label("Personne 2", className='control-label'),
                dcc.Dropdown(
                    id='propose-person2',
                    options=[{'label': p, 'value': p} for p in sorted(persons)],
                    placeholder="Sélectionner...",
                    style={'marginBottom': '15px'}
                ),
                
                html.Label("Type de relation", className='control-label'),
                dcc.Dropdown(
                    id='propose-type',
                    options=[{'label': v, 'value': k} for k, v in RELATION_TYPES.items()],
                    value=0,
                    clearable=False,
                    style={'marginBottom': '15px'}
                ),
                
                html.Label("Notes (optionnel)", className='control-label'),
                dcc.Textarea(
                    id='propose-notes',
                    placeholder="Ajouter des détails...",
                    style={'width': '100%', 'height': '80px', 'marginBottom': '15px'}
                ),
                
                html.Div([
                    html.Button("Envoyer", id='btn-submit-propose', className='btn-custom btn-success-custom'),
                    html.Button("Annuler", id='btn-cancel-propose', className='btn-custom btn-danger-custom'),
                ]),
                
                html.Div(id='propose-message', style={'marginTop': '15px'})
            ])
        ], className='modal-content')
    ], className='modal-overlay', id='propose-modal')

def create_admin_modal():
    """Modal pour l'administration"""
    return html.Div([
        html.Div([
            html.H3("🔐 Admin Login"),
            
            html.Div([
                html.Label("Username", className='control-label'),
                dcc.Input(
                    id='admin-username',
                    type='text',
                    placeholder='admin',
                    style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'borderRadius': '8px'}
                ),
                
                html.Label("Password", className='control-label'),
                dcc.Input(
                    id='admin-password',
                    type='password',
                    placeholder='••••••',
                    style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'borderRadius': '8px'}
                ),
                
                html.Div([
                    html.Button("Login", id='btn-admin-login', className='btn-custom btn-success-custom'),
                    html.Button("Annuler", id='btn-cancel-admin', className='btn-custom btn-danger-custom'),
                ]),
                
                html.Div(id='admin-login-message', style={'marginTop': '15px'})
            ], id='admin-login-form'),
            
            html.Div(id='admin-panel-content', style={'display': 'none'})
        ], className='modal-content')
    ], className='modal-overlay', id='admin-modal')

@app.callback(
    [Output('propose-modal', 'style'),
     Output('propose-message', 'children')],
    [Input('btn-submit-propose', 'n_clicks'),
     Input('btn-cancel-propose', 'n_clicks')],
    [State('propose-person1', 'value'),
     State('propose-person2', 'value'),
     State('propose-type', 'value'),
     State('propose-notes', 'value')],
    prevent_initial_call=True
)
def handle_propose(submit_clicks, cancel_clicks, person1, person2, rel_type, notes):
    if not ctx.triggered:
        return {'display': 'flex'}, ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-cancel-propose':
        return {'display': 'none'}, ""
    
    if button_id == 'btn-submit-propose':
        if not person1 or not person2:
            return {'display': 'flex'}, html.Div("❌ Veuillez sélectionner les deux personnes", style={'color': 'red'})
        
        if person1 == person2:
            return {'display': 'flex'}, html.Div("❌ Les deux personnes doivent être différentes", style={'color': 'red'})
        
        success = db.submit_pending_relation(person1, person2, rel_type, "user", notes or "")
        
        if success:
            return {'display': 'none'}, html.Div("✅ Proposition envoyée !", style={'color': 'green'})
        else:
            return {'display': 'flex'}, html.Div("⚠️ Cette relation est déjà en attente", style={'color': 'orange'})
    
    return {'display': 'flex'}, ""

if __name__ == '__main__':
    persons = db.get_all_persons()
    relations = db.get_all_relations()
    
    # Créer un admin par défaut si pas existant
    db.add_admin("admin", "admin123")
    
    print("\n" + "="*70)
    print("  🌐 SOCIAL NETWORK ANALYZER - Full Version")
    print("="*70)
    print(f"\n  📊 Data: {len(persons)} persons, {len(relations)} relations")
    print(f"  🔐 Admin: admin / admin123")
    print(f"  🚀 Dashboard: http://localhost:8051")
    print(f"  ⚡ Features: Propositions + Admin Panel\n")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=8051, debug=True)
