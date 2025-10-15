#!/usr/bin/env python3
"""Social Network Analyzer - Version Optimisée"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from database import RelationDB
from graph import compute_layout, build_graph, make_figure

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v6.1.1/css/all.css"],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

db = RelationDB()
app.title = "Social Network Analyzer"

# CSS moderne et responsive avec optimisations
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
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            display: flex;
            flex-direction: column;
            position: relative;
        }
        
        /* Bouton fullscreen */
        .fullscreen-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(102, 126, 234, 0.9);
            border: none;
            border-radius: 8px;
            width: 40px;
            height: 40px;
            color: white;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .fullscreen-btn:hover {
            background: rgba(102, 126, 234, 1);
            transform: scale(1.1);
        }
        
        /* Barre de recherche */
        .search-group {
            background: rgba(102, 126, 234, 0.08);
            padding: 12px;
            border-radius: 10px;
            border: 2px solid rgba(102, 126, 234, 0.2);
        }
        
        .search-input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .search-input:focus {
            border-color: rgba(102, 126, 234, 0.6);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .search-results {
            margin-top: 8px;
            max-height: 250px;
            overflow-y: auto;
        }
        
        .search-results::-webkit-scrollbar { width: 4px; }
        .search-results::-webkit-scrollbar-thumb { background: rgba(102, 126, 234, 0.5); border-radius: 4px; }
        
        .search-match {
            background: rgba(102, 126, 234, 0.12);
            padding: 8px 12px;
            border-radius: 6px;
            margin-top: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 13px;
            color: #2D3748;
            font-weight: 500;
            border: 1px solid rgba(102, 126, 234, 0.2);
            width: 100%;
            text-align: left;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
        }
        
        .search-match:hover {
            background: rgba(102, 126, 234, 0.3);
            border-color: rgba(102, 126, 234, 0.5);
            transform: translateX(3px);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
        }
        
        .search-match:active {
            transform: translateX(1px);
            background: rgba(102, 126, 234, 0.4);
        }
        
        .search-info {
            font-size: 11px;
            color: #718096;
            font-style: italic;
            padding: 4px 0;
        }
        
        /* Mode fullscreen */
        .graph-container:fullscreen {
            background: #F8F9FA;
            padding: 20px;
        }
        
        .graph-container:fullscreen .fullscreen-btn i:before {
            content: "\\f066"; /* Icône compress */
        }
        
        .controls-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            max-height: calc(100vh - 30px);
            overflow-y: auto;
        }
        
        .controls-panel::-webkit-scrollbar { width: 6px; }
        .controls-panel::-webkit-scrollbar-track { background: rgba(0,0,0,0.05); border-radius: 10px; }
        .controls-panel::-webkit-scrollbar-thumb { background: rgba(102, 126, 234, 0.4); border-radius: 10px; }
        
        h3 { 
            color: #2D3748; 
            font-size: 24px; 
            font-weight: 700; 
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .control-group { margin-bottom: 20px; }
        .control-label { display: block; color: #4A5568; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
        
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 18px;
            margin-top: 20px;
            color: white;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
        }
        
        .stats-card h5 { font-size: 16px; margin-bottom: 12px; font-weight: 700; }
        .stat-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; }
        .stat-value { font-weight: 700; font-size: 15px; }
        
        .graph-wrapper { 
            flex: 1; 
            min-height: 0; 
            border-radius: 8px; 
            overflow: hidden;
        }
        
        @media (max-width: 1024px) {
            .main-container { grid-template-columns: 1fr; }
            .controls-panel { order: -1; max-height: none; }
            .graph-container { min-height: 500px; }
        }
        
        @media (max-width: 768px) {
            .graph-container { min-height: 400px; }
            h3 { font-size: 18px; }
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
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(
                    id='network-graph',
                    config={
                        'displayModeBar': False,
                        'scrollZoom': True,
                        'displaylogo': False,
                        'doubleClick': 'reset',
                        'responsive': True,
                        # Optimisations de performance maximales
                        'staticPlot': False,
                        'editable': False,
                        'showAxisDragHandles': False,
                        'showAxisRangeEntryBoxes': False,
                        'showTips': False,
                    },
                    style={'height': '100%', 'width': '100%'},
                    # Désactiver le rechargement automatique
                    animate=False,
                )
            ], className='graph-wrapper'),
            
            # Bouton fullscreen
            html.Button(
                [html.I(className="fas fa-expand")],
                id='fullscreen-btn',
                className='fullscreen-btn',
                title='Mode plein écran'
            ),
        ], className='graph-container'),
        
        html.Div([
            html.H3([html.I(className="fas fa-network-wired"), " Controls"]),
            
            # Barre de recherche
            html.Div([
                html.Label("Rechercher une personne", className='control-label'),
                dcc.Input(
                    id='search-input',
                    type='text',
                    placeholder='Tapez un nom...',
                    className='search-input',
                    debounce=False,  # Réponse immédiate
                    value=''
                ),
                html.Div(id='search-results', className='search-results'),
                dcc.Store(id='selected-person')  # Store pour la personne sélectionnée
            ], className='control-group search-group'),
            
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
                html.Label("Taille des bulles", className='control-label'),
                dcc.Slider(
                    id='node-size-slider',
                    min=0.5,
                    max=2.0,
                    step=0.1,
                    value=1.0,
                    marks={0.5: '50%', 1.0: '100%', 1.5: '150%', 2.0: '200%'},
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ], className='control-group'),
            
            html.Div([
                html.Label("Largeur des liens", className='control-label'),
                dcc.Slider(
                    id='edge-width-slider',
                    min=0.5,
                    max=3.0,
                    step=0.25,
                    value=1.5,
                    marks={0.5: 'Fin', 1.5: 'Normal', 3.0: 'Épais'},
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ], className='control-group'),
            
            html.Div([
                html.Label("Force de répulsion", className='control-label'),
                dcc.Slider(
                    id='repulsion-slider',
                    min=0.5,
                    max=4.0,
                    step=0.25,
                    value=1.5,
                    marks={0.5: 'Faible', 1.5: 'Normal', 2.5: 'Fort', 4.0: 'Max'},
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ], className='control-group'),
            
            html.Div([
                html.H5("Network Stats"),
                html.Div([
                    html.Div([html.Span("Persons"), html.Span(f"{len(db.get_all_persons())}", className='stat-value')], className='stat-item'),
                    html.Div([html.Span("Relations"), html.Span(f"{len(db.get_all_relations())}", className='stat-value')], className='stat-item'),
                ])
            ], className='stats-card'),
            
        ], className='controls-panel'),
        
    ], className='main-container'),
])

@app.callback(
    Output('network-graph', 'figure'),
    [Input('layout-dropdown', 'value'),
     Input('node-size-slider', 'value'),
     Input('edge-width-slider', 'value'),
     Input('repulsion-slider', 'value'),
     Input('selected-person', 'data')]
)
def update_graph(layout_type, size_factor, edge_width, repulsion, selected_person):
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
    pos = compute_layout(G, mode=layout_type, repulsion=repulsion)
    fig = make_figure(G, pos, size_factor=size_factor, edge_width=edge_width)
    
    # Si une personne est sélectionnée, zoomer dessus
    xaxis_range = None
    yaxis_range = None
    
    if selected_person and selected_person in pos:
        x, y = pos[selected_person]
        zoom_range = 0.15  # Taille de la zone de zoom
        xaxis_range = [x - zoom_range, x + zoom_range]
        yaxis_range = [y - zoom_range, y + zoom_range]
    
    # Optimisations MAXIMALES pour fluidité parfaite
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False, 
            fixedrange=False,
            visible=False,
            range=xaxis_range,
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False, 
            fixedrange=False,
            visible=False,
            range=yaxis_range,
        ),
        hovermode='closest',
        dragmode='pan',
        uirevision='constant' if not selected_person else None,  # Reset UI uniquement si recherche
        transition={'duration': 0},  # Transitions instantanées
        # Optimisations de rendu
        modebar={'bgcolor': 'rgba(0,0,0,0)'},
        autosize=True,
    )
    
    return fig

# Callback pour la recherche de personne avec suggestions
@app.callback(
    Output('search-results', 'children'),
    Input('search-input', 'value')
)
def search_person(search_term):
    persons = db.get_all_persons()
    
    # Si vide, afficher toutes les personnes (limitées)
    if not search_term:
        return html.Div([
            html.Div(f"📋 {len(persons)} personnes disponibles", className='search-info'),
            html.Div([
                html.Button(
                    name, 
                    id={'type': 'person-btn', 'index': name},
                    n_clicks=0,
                    className='search-match'
                ) for name in sorted(persons)[:10]
            ])
        ])
    
    # Recherche avec filtre
    matches = [p for p in persons if search_term.lower() in p.lower()]
    
    if not matches:
        return html.Div("❌ Aucune personne trouvée", className='search-info')
    
    return html.Div([
        html.Div(f"✅ {len(matches)} résultat(s)", className='search-info'),
        html.Div([
            html.Button(
                name, 
                id={'type': 'person-btn', 'index': name},
                n_clicks=0,
                className='search-match'
            ) for name in sorted(matches)[:15]  # Limiter à 15 résultats
        ])
    ])

# Callback pour gérer le clic sur une personne
@app.callback(
    Output('selected-person', 'data'),
    Input({'type': 'person-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def select_person(n_clicks_list):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return None
    
    # Récupérer le bouton cliqué
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id:
        import json
        button_data = json.loads(button_id)
        return button_data['index']
    
    return None

# Callback pour le mode fullscreen (via clientside)
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            const container = document.querySelector('.graph-container');
            if (!document.fullscreenElement) {
                container.requestFullscreen().catch(err => {
                    console.log('Erreur fullscreen:', err);
                });
            } else {
                document.exitFullscreen();
            }
        }
        return '';
    }
    """,
    Output('fullscreen-btn', 'title'),
    Input('fullscreen-btn', 'n_clicks'),
    prevent_initial_call=True
)

if __name__ == '__main__':
    persons = db.get_all_persons()
    relations = db.get_all_relations()
    
    print("\n" + "="*70)
    print("  🌐 SOCIAL NETWORK ANALYZER - Optimized v2")
    print("="*70)
    print(f"\n  📊 Data: {len(persons)} persons, {len(relations)} relations")
    print(f"  🚀 Dashboard: http://localhost:8051")
    print(f"  ⚡ Performance: Optimized for smooth interaction\n")
    print("="*70 + "\n")
    
    # Nouveau port pour éviter le cache du navigateur
    app.run(host='0.0.0.0', port=8051, debug=False)
