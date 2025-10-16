"""
Application Dash complète - Graphe Social avec gestion des relations
"""

from __future__ import annotations
import math
import networkx as nx
import dash
from dash import dcc, html, Input, Output, State, callback, ALL, ctx, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, List, Tuple
from graph import compute_layout, scale
from database import RelationDB, RELATION_TYPES
from data_loader import get_relation_type_label, get_edge_relation_type

# Initialiser la base de données
db = RelationDB()

# Configuration de l'app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
)

app.title = "Social Network Analyzer"

# CSS personnalisé pour le style Apple moderne
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
                background-color: #f5f5f7;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                margin: 0;
                padding: 0;
                overflow: hidden;
                height: 100vh;
            }
            
            /* Dark mode */
            body.dark-mode {
                background-color: #000000;
                color: #f5f5f7;
            }
            
            body.dark-mode .card {
                background: rgba(28, 28, 30, 0.8) !important;
                color: #f5f5f7 !important;
            }
            
            body.dark-mode .card-header {
                color: #f5f5f7 !important;
            }
            
            body.dark-mode label,
            body.dark-mode .form-label {
                color: #f5f5f7 !important;
            }
            
            body.dark-mode .form-control,
            body.dark-mode .Select-control {
                background-color: rgba(58, 58, 60, 0.8) !important;
                color: #f5f5f7 !important;
                border-color: rgba(99, 99, 102, 0.5) !important;
            }
            
            body.dark-mode input,
            body.dark-mode textarea {
                background-color: rgba(58, 58, 60, 0.8) !important;
                color: #f5f5f7 !important;
                border-color: rgba(99, 99, 102, 0.5) !important;
            }
            
            body.dark-mode .Select-menu-outer {
                background-color: rgba(28, 28, 30, 0.95) !important;
            }
            
            body.dark-mode .Select-option {
                background-color: rgba(28, 28, 30, 0.95) !important;
                color: #f5f5f7 !important;
            }
            
            body.dark-mode .Select-option.is-focused {
                background-color: rgba(58, 58, 60, 0.95) !important;
            }
            
            body.dark-mode .modal-content {
                background-color: rgba(28, 28, 30, 0.95) !important;
                color: #f5f5f7 !important;
            }
            
            body.dark-mode .modal-header,
            body.dark-mode .modal-footer {
                border-color: rgba(99, 99, 102, 0.3) !important;
            }
            
            body.dark-mode h1, body.dark-mode h2, body.dark-mode h3, 
            body.dark-mode h4, body.dark-mode h5, body.dark-mode h6,
            body.dark-mode p {
                color: #f5f5f7 !important;
            }
            
            body.dark-mode .table {
                color: #f5f5f7 !important;
            }
            
            body.dark-mode .table td,
            body.dark-mode .table th {
                border-color: rgba(99, 99, 102, 0.3) !important;
            }
            
            /* Dark mode pour sliders */
            body.dark-mode .apple-slider .rc-slider-rail {
                background: rgba(255, 255, 255, 0.2) !important;
            }
            
            body.dark-mode .apple-slider .rc-slider-mark-text {
                color: #f5f5f7 !important;
            }
            
            /* Fullscreen mode */
            .container-fluid {
                height: 100vh;
                overflow: hidden;
                padding: 0;
                margin: 0;
            }
            
            /* Style des boutons flottants avec effet hover Apple */
            #open-add-modal:hover {
                transform: scale(1.05);
                box-shadow: 0 12px 32px rgba(0, 122, 255, 0.4), 0 4px 12px rgba(0, 122, 255, 0.3);
            }
            
            #open-add-modal:active {
                transform: scale(0.95);
            }
            
            #admin-btn:hover {
                transform: scale(1.05);
                box-shadow: 0 12px 32px rgba(156, 39, 176, 0.4), 0 4px 12px rgba(156, 39, 176, 0.3);
            }
            
            #admin-btn:active {
                transform: scale(0.95);
            }
            
            #dark-mode-btn:hover {
                transform: scale(1.05);
                box-shadow: 0 12px 32px rgba(255, 193, 7, 0.4), 0 4px 12px rgba(255, 193, 7, 0.3);
            }
            
            #dark-mode-btn:active {
                transform: scale(0.95);
            }
            
            #fullscreen-btn:hover {
                transform: scale(1.05);
                background-color: rgba(255, 255, 255, 1) !important;
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.1);
            }
            
            #fullscreen-btn:active {
                transform: scale(0.95);
            }
            
            #close-fullscreen-btn:hover {
                transform: scale(1.05);
                background-color: rgba(255, 255, 255, 1) !important;
            }
            
            /* Style des sliders iOS */
            .apple-slider .rc-slider-track {
                background: linear-gradient(90deg, #007aff 0%, #0051d5 100%);
                height: 4px;
            }
            
            .apple-slider .rc-slider-rail {
                background: rgba(0, 0, 0, 0.06);
                height: 4px;
            }
            
            .apple-slider .rc-slider-handle {
                width: 20px;
                height: 20px;
                margin-top: -8px;
                border: 2px solid #007aff;
                background-color: white;
                box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
            }
            
            .apple-slider .rc-slider-handle:hover {
                border-color: #0051d5;
                box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4);
            }
            
            /* Style des dropdowns */
            .Select-control {
                border-radius: 10px !important;
                border: 1px solid rgba(0, 0, 0, 0.1) !important;
                transition: all 0.2s ease;
            }
            
            .Select-control:hover {
                border-color: rgba(0, 122, 255, 0.5) !important;
            }
            
            .Select--is-focused .Select-control {
                border-color: #007aff !important;
                box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1) !important;
            }
            
            /* Animations smooth */
            * {
                transition-timing-function: cubic-bezier(0.25, 0.46, 0.45, 0.94);
            }
            
            /* Style du bouton toggle controls */
            #toggle-controls:hover {
                background-color: rgba(255, 255, 255, 0.95) !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12) !important;
                transform: translateY(-1px);
            }
            
            #toggle-controls:active {
                transform: translateY(0px);
            }
            
            /* Menu hamburger */
            #hamburger-btn:hover {
                transform: scale(1.05);
                box-shadow: 0 12px 32px rgba(0, 122, 255, 0.4), 0 4px 12px rgba(0, 122, 255, 0.3);
            }
            
            #hamburger-btn:active {
                transform: scale(0.95);
            }
            
            .menu-item:hover {
                background-color: rgba(0, 122, 255, 0.1) !important;
            }
            
            body.dark-mode #hamburger-menu {
                background-color: rgba(28, 28, 30, 0.95) !important;
            }
            
            body.dark-mode .menu-item,
            body.dark-mode #hamburger-menu a {
                color: #f5f5f7 !important;
            }
            
            /* Style des cartes */
            .card {
                transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            }
            
            /* Inputs focus */
            input:focus, .form-control:focus {
                border-color: #007aff !important;
                box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1) !important;
                outline: none;
            }
            
            /* Modal backdrop */
            .modal-backdrop {
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                background-color: rgba(0, 0, 0, 0.4) !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Fonction pour charger le graphe depuis la DB
def load_graph_from_db() -> Tuple[nx.DiGraph, Dict[int, str]]:
    """Charge le graphe depuis la base de données."""
    from graph import build_graph
    
    relations_data = db.get_all_relations()
    
    # Convertir en format dict pour build_graph
    relations_dict = {}
    for person1, person2, rel_type in relations_data:
        if person1 not in relations_dict:
            relations_dict[person1] = []
        relations_dict[person1].append((person2, rel_type))
    
    G = build_graph(relations_dict)
    return G, {0: "Bisous", 1: "Dodo ensemble", 2: "Baise", 3: "Couple"}

# Charger les données initiales
G, relation_types = load_graph_from_db()

# Calculer les statistiques
def compute_stats(G):
    total_nodes = G.number_of_nodes()
    total_edges = G.number_of_edges()
    indeg = dict(G.in_degree())
    outdeg = dict(G.out_degree())
    deg_total = {n: indeg.get(n, 0) + outdeg.get(n, 0) for n in G.nodes()}
    avg_degree = sum(deg_total.values()) / len(deg_total) if deg_total else 0
    max_degree_node = max(deg_total.items(), key=lambda x: x[1]) if deg_total else ("", 0)
    return total_nodes, total_edges, indeg, outdeg, deg_total, avg_degree, max_degree_node

total_nodes, total_edges, indeg, outdeg, deg_total, avg_degree, max_degree_node = compute_stats(G)

# Import de la fonction make_graph_figure
from dashboard import make_graph_figure

# Layout principal sans navbar pour maximiser l'espace
def create_layout():
    return dbc.Container([
        # URL routing
        dcc.Location(id='url', refresh=False),
    
    # Modal pour ajouter une relation - Style Apple
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Add New Relationship", style={
            'fontWeight': '600',
            'fontSize': '22px',
            'letterSpacing': '-0.3px',
            'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif'
        }), close_button=True),
        dbc.ModalBody([
            html.P("This relationship will be pending approval by an admin.", 
                   style={
                       'color': '#86868b',
                       'fontSize': '14px',
                       'marginBottom': '24px',
                       'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
                       'lineHeight': '1.5'
                   }),
            
            html.Label("Person 1:", style={
                'fontWeight': '500',
                'marginBottom': '8px',
                'display': 'block',
                'fontSize': '14px',
                'color': '#1d1d1f',
                'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
            }),
            dcc.Dropdown(
                id='modal-person1',
                options=[],
                placeholder="Select or type a name...",
                searchable=True,
                clearable=True,
                style={'marginBottom': '20px'}
            ),
            
            html.Label("Person 2:", style={
                'fontWeight': '500',
                'marginBottom': '8px',
                'display': 'block',
                'fontSize': '14px',
                'color': '#1d1d1f',
                'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
            }),
            dcc.Dropdown(
                id='modal-person2',
                options=[],
                placeholder="Select or type a name...",
                searchable=True,
                clearable=True,
                style={'marginBottom': '20px'}
            ),
            
            html.Label("Relationship Type:", style={
                'fontWeight': '500',
                'marginBottom': '8px',
                'display': 'block',
                'fontSize': '14px',
                'color': '#1d1d1f',
                'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
            }),
            dcc.Dropdown(
                id='modal-relation-type',
                options=[
                    {'label': 'Bisous', 'value': 0},
                    {'label': 'Dodo ensemble', 'value': 1},
                    {'label': 'Baise', 'value': 2},
                    {'label': 'Couple', 'value': 3},
                ],
                value=0,
                clearable=False,
                style={'marginBottom': '20px'}
            ),
            
            html.Label("Your Name (optional):", style={
                'fontWeight': '500',
                'marginBottom': '8px',
                'display': 'block',
                'fontSize': '14px',
                'color': '#1d1d1f',
                'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
            }),
            dcc.Input(
                id='modal-username',
                type='text',
                placeholder='Anonymous',
                className='form-control',
                style={
                    'marginBottom': '20px',
                    'borderRadius': '10px',
                    'border': '1px solid #d2d2d7',
                    'padding': '12px 16px',
                    'fontSize': '14px',
                    'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
                }
            ),
            
            html.Div(id='modal-message'),
        ], style={'padding': '24px'}),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="close-add-modal", color="light", className="me-2", style={
                'borderRadius': '10px',
                'padding': '10px 24px',
                'fontWeight': '500',
                'fontSize': '14px',
                'border': '1px solid #d2d2d7',
                'color': '#1d1d1f',
                'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
            }),
            dbc.Button("Submit", id="submit-modal-relation", color="primary", style={
                'borderRadius': '10px',
                'padding': '10px 24px',
                'fontWeight': '500',
                'fontSize': '14px',
                'backgroundColor': '#007aff',
                'border': 'none',
                'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
            }),
        ], style={'padding': '16px 24px', 'borderTop': '1px solid #f5f5f7'}),
    ], id="add-relation-modal", size="lg", is_open=False, style={
        'borderRadius': '16px',
        'boxShadow': '0 4px 16px rgba(0,0,0,0.12)'
    }),
    
    # Bouton flottant pour ajouter - Style Apple
    html.Button(
        html.I(className="fas fa-plus"),
        id="open-add-modal",
        style={
            "position": "fixed",
            "bottom": "160px",
            "right": "30px",
            "width": "56px",
            "height": "56px",
            "borderRadius": "50%",
            "backgroundColor": "#007aff",
            "color": "white",
            "border": "none",
            "boxShadow": "0 8px 24px rgba(0, 122, 255, 0.3), 0 2px 8px rgba(0, 122, 255, 0.2)",
            "cursor": "pointer",
            "fontSize": "20px",
            "display": "none",  # Caché car dans le menu
            "alignItems": "center",
            "justifyContent": "center",
            "zIndex": "999",
            "transition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
            "WebkitTransition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
        }
    ),
    
    # Bouton Admin flottant - Style Apple
    html.A(
        html.Button(
            html.I(className="fas fa-user-shield"),
            id="admin-btn",
            style={
                "width": "56px",
                "height": "56px",
                "borderRadius": "50%",
                "backgroundColor": "#9c27b0",
                "color": "white",
                "border": "none",
                "boxShadow": "0 8px 24px rgba(156, 39, 176, 0.3), 0 2px 8px rgba(156, 39, 176, 0.2)",
                "cursor": "pointer",
                "fontSize": "20px",
                "display": "none",  # Caché car dans le menu
                "alignItems": "center",
                "justifyContent": "center",
                "transition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
                "WebkitTransition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
            }
        ),
        href="/admin",
        style={
            "position": "fixed",
            "bottom": "100px",
            "right": "30px",
            "zIndex": "999",
            "display": "none"  # Caché car dans le menu
        }
    ),
    
    # Bouton Dark Mode flottant - Style Apple
    html.Button(
        html.I(className="fas fa-moon", id="dark-mode-icon"),
        id="dark-mode-btn",
        style={
            "position": "fixed",
            "bottom": "40px",
            "right": "100px",
            "width": "56px",
            "height": "56px",
            "borderRadius": "50%",
            "backgroundColor": "#ffc107",
            "color": "white",
            "border": "none",
            "boxShadow": "0 8px 24px rgba(255, 193, 7, 0.3), 0 2px 8px rgba(255, 193, 7, 0.2)",
            "cursor": "pointer",
            "fontSize": "20px",
            "display": "none",  # Caché car dans le menu
            "alignItems": "center",
            "justifyContent": "center",
            "zIndex": "999",
            "transition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
            "WebkitTransition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
        }
    ),
    
    # Menu hamburger et ses options
    html.Div([
        # Bouton hamburger principal
        html.Button(
            html.I(className="fas fa-bars", id="menu-icon"),
            id="hamburger-btn",
            style={
                "width": "56px",
                "height": "56px",
                "borderRadius": "50%",
                "backgroundColor": "#007aff",
                "color": "white",
                "border": "none",
                "boxShadow": "0 8px 24px rgba(0, 122, 255, 0.3), 0 2px 8px rgba(0, 122, 255, 0.2)",
                "cursor": "pointer",
                "fontSize": "24px",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "transition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
                "zIndex": "1001"
            }
        ),
        
        # Menu déroulant
        html.Div([
            # Option Add
            html.Div([
                html.Button(
                    [html.I(className="fas fa-plus me-2"), "Add"],
                    id="menu-add-btn",
                    className="menu-item",
                    style={
                        "width": "100%",
                        "padding": "12px 20px",
                        "backgroundColor": "transparent",
                        "border": "none",
                        "color": "#1d1d1f",
                        "fontSize": "16px",
                        "fontWeight": "500",
                        "cursor": "pointer",
                        "display": "flex",
                        "alignItems": "center",
                        "transition": "background-color 0.2s ease",
                        "borderRadius": "8px"
                    }
                )
            ]),
            # Option Admin
            html.Div([
                html.A(
                    [html.I(className="fas fa-user-shield me-2"), "Admin"],
                    href="/admin",
                    style={
                        "width": "100%",
                        "padding": "12px 20px",
                        "backgroundColor": "transparent",
                        "border": "none",
                        "color": "#1d1d1f",
                        "fontSize": "16px",
                        "fontWeight": "500",
                        "cursor": "pointer",
                        "display": "flex",
                        "alignItems": "center",
                        "textDecoration": "none",
                        "transition": "background-color 0.2s ease",
                        "borderRadius": "8px"
                    }
                )
            ]),
            # Option Dark Mode
            html.Div([
                html.Button(
                    [html.I(className="fas fa-moon me-2", id="menu-dark-icon"), "Dark Mode"],
                    id="menu-dark-btn",
                    className="menu-item",
                    style={
                        "width": "100%",
                        "padding": "12px 20px",
                        "backgroundColor": "transparent",
                        "border": "none",
                        "color": "#1d1d1f",
                        "fontSize": "16px",
                        "fontWeight": "500",
                        "cursor": "pointer",
                        "display": "flex",
                        "alignItems": "center",
                        "transition": "background-color 0.2s ease",
                        "borderRadius": "8px"
                    }
                )
            ]),
            # Option Fullscreen
            html.Div([
                html.Button(
                    [html.I(className="fas fa-expand me-2"), "Fullscreen"],
                    id="menu-fullscreen-btn",
                    className="menu-item",
                    style={
                        "width": "100%",
                        "padding": "12px 20px",
                        "backgroundColor": "transparent",
                        "border": "none",
                        "color": "#1d1d1f",
                        "fontSize": "16px",
                        "fontWeight": "500",
                        "cursor": "pointer",
                        "display": "flex",
                        "alignItems": "center",
                        "transition": "background-color 0.2s ease",
                        "borderRadius": "8px"
                    }
                )
            ]),
        ], id="hamburger-menu", style={
            "position": "absolute",
            "bottom": "70px",
            "right": "0",
            "minWidth": "200px",
            "backgroundColor": "rgba(255, 255, 255, 0.95)",
            "backdropFilter": "blur(20px)",
            "WebkitBackdropFilter": "blur(20px)",
            "borderRadius": "12px",
            "boxShadow": "0 8px 24px rgba(0, 0, 0, 0.15), 0 2px 8px rgba(0, 0, 0, 0.08)",
            "padding": "8px",
            "display": "none",
            "zIndex": "1000"
        }),
    ], style={
        "position": "fixed",
        "bottom": "30px",
        "right": "30px",
        "zIndex": "1001"
    }),
    
    # Bouton plein écran flottant - Style Apple (gardé mais caché)
    html.Div([
        dbc.Button(
            html.I(className="fas fa-expand fa-lg"),
            id="fullscreen-btn",
            color="light",
            className="rounded-circle",
            style={
                "position": "fixed",
                "bottom": "30px",
                "right": "30px",
                "width": "56px",
                "height": "56px",
                "backgroundColor": "rgba(255, 255, 255, 0.9)",
                "backdropFilter": "blur(10px)",
                "WebkitBackdropFilter": "blur(10px)",
                "border": "1px solid rgba(0, 0, 0, 0.08)",
                "color": "#1d1d1f",
                "boxShadow": "0 8px 24px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08)",
                "zIndex": "2000",
                "display": "none",  # Caché car dans le menu
                "transition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
                "WebkitTransition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
            },
        ),
    ], id="fullscreen-btn-container"),
    
    # Overlay plein écran (caché par défaut) - Style Apple
    html.Div([
        # Bouton fermer
        dbc.Button(
            html.I(className="fas fa-times fa-2x"),
            id="close-fullscreen-btn",
            color="light",
            className="rounded-circle",
            style={
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "width": "56px",
                "height": "56px",
                "backgroundColor": "rgba(255, 255, 255, 0.9)",
                "backdropFilter": "blur(10px)",
                "WebkitBackdropFilter": "blur(10px)",
                "border": "1px solid rgba(0, 0, 0, 0.08)",
                "color": "#1d1d1f",
                "boxShadow": "0 8px 24px rgba(0, 0, 0, 0.12)",
                "zIndex": "3000",
                "transition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
            },
        ),
        # Graphe en plein écran
        dcc.Graph(
            id='fullscreen-graph',
            style={'height': '100vh', 'width': '100vw'},
            config={
                'displayModeBar': False,  # Pas de barre d'outils en plein écran
                'scrollZoom': True,
                'doubleClick': False,
            },
        ),
    ], id="fullscreen-overlay", style={
        "position": "fixed",
        "top": "0",
        "left": "0",
        "width": "100vw",
        "height": "100vh",
        "backgroundColor": "white",
        "zIndex": "2500",
        "display": "none",
    }),
    
    html.Div(id='page-content', children=[]),  # Will be populated by callback or set to graph initially
    dcc.Interval(id='refresh-interval', interval=5000, n_intervals=0),
    
    dcc.Store(id='admin-auth', data={'authenticated': False}),
    dcc.Store(id='dark-mode-state', data={'enabled': False}),
    ], fluid=True)

# Page 1: Graphe principal avec panneau de contrôle style Apple
def create_graph_page():
    return html.Div([
        dbc.Row([
            # Panneau de contrôle rétractable - Style glassmorphism Apple
            dbc.Col([
                html.Div([
                    # Bouton pour ranger/afficher le panneau
                    dbc.Button(
                        html.I(className="fas fa-sliders-h"),
                        id="toggle-controls",
                        color="light",
                        className="mb-3 w-100",
                        style={
                            'border': '1px solid rgba(0, 0, 0, 0.08)',
                            'borderRadius': '12px',
                            'padding': '12px',
                            'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                            'backdropFilter': 'blur(20px)',
                            'WebkitBackdropFilter': 'blur(20px)',
                            'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.08)',
                            'transition': 'all 0.2s ease',
                            'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif'
                        }
                    ),
                    
                    # Panneau de contrôle
                    dbc.Collapse([
                        dbc.Card([
                            dbc.CardHeader("Graph Controls", style={
                                'fontWeight': '600',
                                'fontSize': '16px',
                                'backgroundColor': 'transparent',
                                'border': 'none',
                                'padding': '16px 16px 12px 16px',
                                'color': '#1d1d1f',
                                'letterSpacing': '-0.2px',
                                'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif'
                            }),
                            dbc.CardBody([
                                html.Label("Layout Algorithm", style={
                                    'fontWeight': '500',
                                    'fontSize': '13px',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'color': '#1d1d1f',
                                    'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
                                }),
                                dcc.Dropdown(
                                    id='layout-dropdown',
                                    options=[
                                        {'label': 'Communities', 'value': 'community'},
                                        {'label': 'Force-directed', 'value': 'spring'},
                                        {'label': 'Kamada-Kawai', 'value': 'kk'},
                                        {'label': 'Spectral', 'value': 'spectral'},
                                        {'label': 'Circular', 'value': 'circular'},
                                    ],
                                    value='community',
                                    clearable=False,
                                    style={'marginBottom': '20px', 'fontSize': '14px'}
                                ),
                                
                                html.Label("Node Spacing", style={
                                    'fontWeight': '500',
                                    'fontSize': '13px',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'color': '#1d1d1f',
                                    'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
                                }),
                                dcc.Slider(
                                    id='spread-slider',
                                    min=1,
                                    max=10,
                                    step=0.5,
                                    value=5.0,
                                    marks={i: str(i) for i in [1, 3, 5, 7, 10]},
                                    tooltip={"placement": "bottom", "always_visible": False},
                                    className="apple-slider"
                                ),
                                
                                html.Label("Node Size", style={
                                    'fontWeight': '500',
                                    'fontSize': '13px',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'marginTop': '20px',
                                    'color': '#1d1d1f',
                                    'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
                                }),
                                dcc.Slider(
                                    id='node-size-slider',
                                    min=5,
                                    max=30,
                                    step=1,
                                    value=15,
                                    marks={i: str(i) for i in [5, 10, 15, 20, 25, 30]},
                                    tooltip={"placement": "bottom", "always_visible": False},
                                    className="apple-slider"
                                ),
                                
                                html.Label("Edge Width", style={
                                    'fontWeight': '500',
                                    'fontSize': '13px',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'marginTop': '20px',
                                    'color': '#1d1d1f',
                                    'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
                                }),
                                dcc.Slider(
                                    id='edge-width-slider',
                                    min=1,
                                    max=8,
                                    step=0.5,
                                    value=2,
                                    marks={i: str(i) for i in [1, 3, 5, 8]},
                                    tooltip={"placement": "bottom", "always_visible": False},
                                    className="apple-slider"
                                ),
                                
                                html.Hr(style={'margin': '24px 0', 'border': 'none', 'borderTop': '1px solid rgba(0, 0, 0, 0.06)'}),
                                
                                html.Label("Filter by Relationship", style={
                                    'fontWeight': '500',
                                    'fontSize': '13px',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'color': '#1d1d1f',
                                    'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
                                }),
                                dcc.Dropdown(
                                    id='relation-filter',
                                    options=[
                                        {'label': 'All Types', 'value': 'all'},
                                        {'label': 'Bisous', 'value': '0'},
                                        {'label': 'Dodo ensemble', 'value': '1'},
                                        {'label': 'Baise', 'value': '2'},
                                        {'label': 'Couple', 'value': '3'},
                                    ],
                                    value='all',
                                    clearable=False,
                                    style={'marginBottom': '20px', 'fontSize': '14px'}
                                ),
                                
                                html.Label("Center on Person", style={
                                    'fontWeight': '500',
                                    'fontSize': '13px',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'color': '#1d1d1f',
                                    'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
                                }),
                                dcc.Dropdown(
                                    id='center-dropdown',
                                    options=[{'label': n, 'value': n} for n in sorted(G.nodes())],
                                    value=None,
                                    placeholder="Select to center...",
                                    style={'marginBottom': '20px', 'fontSize': '14px'}
                                ),
                                
                                html.Label("Search Person", style={
                                    'fontWeight': '500',
                                    'fontSize': '13px',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'marginTop': '20px',
                                    'color': '#1d1d1f',
                                    'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
                                }),
                                dcc.Input(
                                    id='search-input',
                                    type='text',
                                    placeholder="Type a name...",
                                    style={
                                        'width': '100%',
                                        'marginBottom': '20px',
                                        'fontSize': '14px',
                                        'padding': '10px 14px',
                                        'borderRadius': '10px',
                                        'border': '1px solid rgba(0, 0, 0, 0.1)',
                                        'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
                                        'transition': 'all 0.2s ease'
                                    }
                                ),
                                
                                html.Hr(style={'margin': '24px 0', 'border': 'none', 'borderTop': '1px solid rgba(0, 0, 0, 0.06)'}),
                                
                                dbc.Checklist(
                                    id='show-labels-check',
                                    options=[{'label': ' Show all labels', 'value': 'show'}],
                                    value=['show'],
                                    style={
                                        'fontSize': '14px',
                                        'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
                                        'color': '#1d1d1f'
                                    }
                                ),
                            ], style={
                                'padding': '20px',
                                'maxHeight': 'calc(100vh - 200px)',
                                'overflowY': 'auto'
                            }),
                        ], style={
                            'border': '1px solid rgba(0, 0, 0, 0.08)',
                            'borderRadius': '16px',
                            'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                            'backdropFilter': 'blur(20px)',
                            'WebkitBackdropFilter': 'blur(20px)',
                            'boxShadow': '0 4px 16px rgba(0, 0, 0, 0.08)',
                        }),
                    ], id="controls-collapse", is_open=True),
                ], className="sticky-top", style={"top": "80px"}),
            ], width=3, id="controls-column"),
            
            # Zone du graphe adaptatif
            dbc.Col([
                html.Div([
                    dcc.Graph(
                        id='social-graph',
                        figure=make_graph_figure(G, layout_mode='community', spread=5.0, show_labels=True, dark_mode=False),
                        style={'height': '100vh', 'width': '100%'},
                        config={
                            # Pas de barre d'outils
                            'displayModeBar': False,
                            # Zoom avec molette de souris/trackpad activé
                            'scrollZoom': True,
                            # Double-clic pour reset le zoom désactivé
                            'doubleClick': False,
                            # Responsive
                            'responsive': True,
                        },
                    ),
                ], style={'height': 'calc(100vh - 120px)'}),
            ], width=9, id="graph-column"),
        ], style={'height': 'calc(100vh - 100px)'}),
    ])

# Page 2: Panneau admin
def create_admin_page():
    """Page Admin avec onglets: Pending, History, Manage"""
    return dbc.Container([
        # Bouton flottant pour retourner au graphe
        html.A(
            html.Button(
                html.I(className="fas fa-arrow-left"),
                style={
                    "width": "56px",
                    "height": "56px",
                    "borderRadius": "50%",
                    "backgroundColor": "#007aff",
                    "color": "white",
                    "border": "none",
                    "boxShadow": "0 8px 24px rgba(0, 122, 255, 0.3), 0 2px 8px rgba(0, 122, 255, 0.2)",
                    "cursor": "pointer",
                    "fontSize": "20px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "transition": "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
                }
            ),
            href="/",
            style={
                "position": "fixed",
                "bottom": "30px",
                "right": "30px",
                "zIndex": "999"
            }
        ),
        
        dbc.Row([
            dbc.Col([
                html.H2("🔐 Administration", className="text-center mb-4"),
                
                # Section de connexion
                html.Div([
                    dbc.Card([
                        dbc.CardHeader(html.H3("🔐 Connexion Admin")),
                        dbc.CardBody([
                            html.Label("Username:", className="fw-bold"),
                            dcc.Input(
                                id='admin-username',
                                type='text',
                                className='form-control mb-3',
                            ),
                            
                            html.Label("Password:", className="fw-bold"),
                            dcc.Input(
                                id='admin-password',
                                type='password',
                                className='form-control mb-3',
                            ),
                            
                            dbc.Button("Login", id='login-button', color="primary", className="w-100"),
                            html.Div(id='login-message', className="mt-2"),
                        ]),
                    ]),
                ], id='login-section'),
                
                # Section admin authentifié avec onglets
                html.Div([
                    dbc.Alert("Logged in as administrator", color="success", className="mb-3", dismissable=True),
                    
                    dbc.Tabs([
                        # Onglet Pending Relations
                        dbc.Tab([
                            html.Div([
                                html.H4("Pending Approvals", className="mt-3 mb-3", style={'fontWeight': '600'}),
                                html.Div(id='pending-list'),
                                dcc.Interval(id='admin-refresh', interval=3000, n_intervals=0),
                            ]),
                        ], label="Pending", tab_id="pending"),
                        
                        # Onglet History
                        dbc.Tab([
                            html.Div([
                                html.H4("Modification History", className="mt-3", style={'fontWeight': '600'}),
                                dbc.Button("Refresh", id='refresh-history-btn', color='primary', size='sm', className='mb-3', outline=True),
                                html.Div(id='history-list'),
                            ]),
                        ], label="History", tab_id="history"),
                        
                        # Onglet Manage Relations
                        dbc.Tab([
                            html.Div([
                                html.H4("Manage Relationships", className="mt-3", style={'fontWeight': '600'}),
                                html.Label("Search person:", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                                dcc.Input(
                                    id='manage-search',
                                    type='text',
                                    placeholder='Name...',
                                    className='form-control mb-3',
                                    debounce=True,
                                ),
                                html.Hr(),
                                html.Div(id='manage-relations-list'),
                            ]),
                        ], label="Manage", tab_id="manage"),
                    ], id="admin-tabs", active_tab="pending"),
                    
                ], id='admin-section', style={'display': 'none'}),
                
                # Modal pour éditer une relation
                dbc.Modal([
                    dbc.ModalHeader(dbc.ModalTitle("Edit Relationship"), close_button=True),
                    dbc.ModalBody([
                        html.Div(id='edit-relation-info'),
                        html.Label("New relationship type:", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                        dcc.Dropdown(
                            id='edit-relation-type',
                            options=[
                                {'label': 'Bisous', 'value': 0},
                                {'label': 'Dodo ensemble', 'value': 1},
                                {'label': 'Baise', 'value': 2},
                                {'label': 'Couple', 'value': 3},
                            ],
                            clearable=False,
                        ),
                        html.Div(id='edit-message', className="mt-3"),
                    ]),
                    dbc.ModalFooter([
                        dbc.Button("Cancel", id="close-edit-modal", color="secondary", outline=True, className="me-2"),
                        dbc.Button("Save Changes", id="save-edit-relation", color="primary"),
                    ]),
                ], id="edit-relation-modal", is_open=False),
                
                dcc.Store(id='edit-relation-data'),
                
            ], width=10, className="mx-auto mt-4"),
        ]),
    ], fluid=True)

# Create layout after page functions are defined
# Call create_layout() and initialize page-content with graph page
layout = create_layout()
# Initialize page-content with graph page by default
for component in layout.children:
    if hasattr(component, 'id') and component.id == 'page-content':
        component.children = create_graph_page()
        break

# Assign the layout (not a function)
app.layout = layout

# Callback to handle navigation (even though page-content has initial content)
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('url', 'href')]  # Add href as trigger to force initial load
)
def display_page(pathname, href):
    print(f"DEBUG: display_page called with pathname={pathname}, href={href}")
    if pathname == '/admin':
        print("DEBUG: Returning admin page")
        return create_admin_page()
    else:
        print("DEBUG: Returning graph page")
        return create_graph_page()

# Callback pour le dark mode (bouton et menu)
@app.callback(
    [
        Output('dark-mode-state', 'data'),
        Output('dark-mode-icon', 'className'),
        Output('menu-dark-icon', 'className'),
    ],
    [
        Input('dark-mode-btn', 'n_clicks'),
        Input('menu-dark-btn', 'n_clicks'),
    ],
    State('dark-mode-state', 'data'),
    prevent_initial_call=True,
)
def toggle_dark_mode(btn_clicks, menu_clicks, state):
    new_state = not state.get('enabled', False)
    btn_icon = "fas fa-sun" if new_state else "fas fa-moon"
    menu_icon = "fas fa-sun me-2" if new_state else "fas fa-moon me-2"
    return {'enabled': new_state}, btn_icon, menu_icon

# Clientside callback pour appliquer le dark mode au body
app.clientside_callback(
    """
    function(darkModeState) {
        if (darkModeState && darkModeState.enabled) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('dark-mode-btn', 'data-dummy'),
    Input('dark-mode-state', 'data'),
)

# Callback pour le menu hamburger
@app.callback(
    Output('hamburger-menu', 'style'),
    Input('hamburger-btn', 'n_clicks'),
    State('hamburger-menu', 'style'),
    prevent_initial_call=True,
)
def toggle_hamburger_menu(n_clicks, current_style):
    print(f"DEBUG: toggle_hamburger_menu called with n_clicks={n_clicks}, current_style={current_style}")
    
    # Récupérer le style actuel ou utiliser un dict vide
    if not current_style:
        current_style = {}
    
    # Créer une copie du style
    new_style = dict(current_style)
    
    # Toggle display
    if new_style.get('display') == 'none' or 'display' not in new_style:
        new_style['display'] = 'block'
        print("DEBUG: Setting display to block")
    else:
        new_style['display'] = 'none'
        print("DEBUG: Setting display to none")
    
    print(f"DEBUG: Returning style={new_style}")
    return new_style

# Callback pour les actions du menu
@app.callback(
    Output('add-relation-modal', 'is_open'),
    [
        Input('menu-add-btn', 'n_clicks'),
        Input('open-add-modal', 'n_clicks'),
        Input('close-add-modal', 'n_clicks'),
        Input('submit-modal-relation', 'n_clicks'),
    ],
    State('add-relation-modal', 'is_open'),
    prevent_initial_call=True,
)
def toggle_modal_from_menu(menu_clicks, old_btn_clicks, close_clicks, submit_clicks, is_open):
    if ctx.triggered_id in ['menu-add-btn', 'open-add-modal']:
        return not is_open
    return not is_open

# Callback fullscreen depuis le menu
@app.callback(
    [
        Output('fullscreen-overlay', 'style', allow_duplicate=True),
        Output('fullscreen-btn-container', 'style', allow_duplicate=True),
    ],
    Input('menu-fullscreen-btn', 'n_clicks'),
    prevent_initial_call=True,
)
def toggle_fullscreen_from_menu(n_clicks):
    # Ouvrir le plein écran
    return (
        {"position": "fixed", "top": "0", "left": "0", "width": "100vw", "height": "100vh",
         "backgroundColor": "white", "zIndex": "2500", "display": "block"},
        {"display": "none"}
    )

# Callback pour gérer le plein écran
@app.callback(
    [
        Output('fullscreen-overlay', 'style'),
        Output('fullscreen-btn-container', 'style'),
    ],
    [
        Input('fullscreen-btn', 'n_clicks'),
        Input('close-fullscreen-btn', 'n_clicks'),
    ],
    prevent_initial_call=True,
)
def toggle_fullscreen(open_clicks, close_clicks):
    if ctx.triggered_id == 'fullscreen-btn':
        # Ouvrir le plein écran
        return (
            {
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100vw",
                "height": "100vh",
                "backgroundColor": "white",
                "zIndex": "2500",
                "display": "block",
            },
            {"display": "none"}  # Cacher le bouton d'ouverture
        )
    else:
        # Fermer le plein écran
        return (
            {
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100vw",
                "height": "100vh",
                "backgroundColor": "white",
                "zIndex": "2500",
                "display": "none",
            },
            {
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "width": "60px",
                "height": "60px",
                "zIndex": "2000",
                "display": "block",
            }
        )

# Callback pour mettre à jour le graphe plein écran
@app.callback(
    Output('fullscreen-graph', 'figure'),
    [
        Input('fullscreen-btn', 'n_clicks'),
        Input('refresh-interval', 'n_intervals'),
        Input('dark-mode-state', 'data'),
    ],
    [
        State('layout-dropdown', 'value'),
        State('spread-slider', 'value'),
        State('center-dropdown', 'value'),
        State('search-input', 'value'),
        State('show-labels-check', 'value'),
    ],
)
def update_fullscreen_graph(open_clicks, n_intervals, dark_mode_state, layout_mode, spread, center_node, search_term, show_labels_check):
    # Recharger le graphe depuis la DB
    G, relation_types = load_graph_from_db()
    
    show_labels = 'show' in (show_labels_check or [])
    search_highlight = search_term or ""
    dark_mode = dark_mode_state.get('enabled', False) if dark_mode_state else False
    
    # Récupérer les statistiques
    _, _, _, _, deg_total, _, _ = compute_stats(G)
    
    return make_graph_figure(
        G,
        layout_mode=layout_mode or 'community',
        center_node=center_node,
        min_degree=0,
        max_degree=1000,
        search_highlight=search_highlight,
        spread=spread or 5.0,
        show_labels=show_labels,
        dark_mode=dark_mode,
    )

# Callback pour ouvrir/fermer le modal d'ajout
@app.callback(
    [
        Output("add-relation-modal", "is_open"),
        Output('modal-person1', 'options'),
        Output('modal-person2', 'options'),
    ],
    [
        Input("open-add-modal", "n_clicks"),
        Input("close-add-modal", "n_clicks"),
        Input("submit-modal-relation", "n_clicks"),
    ],
    State("add-relation-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_add_modal(n_open, n_close, n_submit, is_open):
    persons = db.get_all_persons()
    options = [{'label': p, 'value': p} for p in sorted(persons)]
    
    if ctx.triggered_id == "submit-modal-relation":
        # Garder ouvert après soumission pour afficher le message
        return True, options, options
    
    return not is_open, options, options

# Callback pour toggle le panneau de contrôle
@app.callback(
    [
        Output("controls-collapse", "is_open"),
        Output("controls-column", "width"),
        Output("graph-column", "width"),
    ],
    Input("toggle-controls", "n_clicks"),
    State("controls-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_controls(n, is_open):
    if is_open:
        # Cacher le panneau -> graphe prend toute la largeur
        return False, 0, 12
    else:
        # Montrer le panneau -> partage 3/9
        return True, 3, 9

# Callback pour soumettre une relation via le modal
@app.callback(
    Output('modal-message', 'children'),
    Input('submit-modal-relation', 'n_clicks'),
    [
        State('modal-person1', 'value'),
        State('modal-person2', 'value'),
        State('modal-relation-type', 'value'),
        State('modal-username', 'value'),
    ],
    prevent_initial_call=True,
)
def submit_modal_relation(n_clicks, person1, person2, rel_type, username):
    if not person1 or not person2:
        return dbc.Alert("Please select both persons.", color="danger", dismissable=True)
    
    if person1 == person2:
        return dbc.Alert("A person cannot have a relationship with themselves.", color="danger", dismissable=True)
    
    username = username or "anonymous"
    
    success = db.submit_pending_relation(person1, person2, rel_type, username, "")
    
    if success:
        return dbc.Alert("Relationship submitted successfully! It will be visible after admin approval.", color="success", dismissable=True)
    else:
        return dbc.Alert("This relationship already exists or is pending approval.", color="warning", dismissable=True)

# Callback pour le graphe
@app.callback(
    Output('social-graph', 'figure'),
    [
        Input('layout-dropdown', 'value'),
        Input('spread-slider', 'value'),
        Input('center-dropdown', 'value'),
        Input('search-input', 'value'),
        Input('show-labels-check', 'value'),
        Input('refresh-interval', 'n_intervals'),
        Input('dark-mode-state', 'data'),
    ],
)
def update_graph(layout_mode, spread, center_node, search_text, show_labels_check, n_intervals, dark_mode_state):
    # Recharger le graphe depuis la DB
    global G, total_nodes, total_edges, indeg, outdeg, deg_total, avg_degree, max_degree_node
    G, relation_types = load_graph_from_db()
    total_nodes, total_edges, indeg, outdeg, deg_total, avg_degree, max_degree_node = compute_stats(G)
    
    show_labels = 'show' in (show_labels_check or [])
    search_highlight = search_text or ""
    dark_mode = dark_mode_state.get('enabled', False) if dark_mode_state else False
    
    return make_graph_figure(
        G,
        layout_mode=layout_mode,
        center_node=center_node,
        min_degree=0,
        max_degree=1000,
        search_highlight=search_highlight,
        spread=spread,
        show_labels=show_labels,
        dark_mode=dark_mode,
    )

# Callback pour connexion admin
@app.callback(
    [
        Output('admin-auth', 'data'),
        Output('login-message', 'children'),
        Output('login-section', 'style'),
        Output('admin-section', 'style'),
    ],
    Input('login-button', 'n_clicks'),
    [
        State('admin-username', 'value'),
        State('admin-password', 'value'),
    ],
    prevent_initial_call=True,
)
def login_admin(n_clicks, username, password):
    if not username or not password:
        return {'authenticated': False}, dbc.Alert("Please fill in all fields.", color="danger", dismissable=True), {}, {'display': 'none'}
    
    if db.verify_admin(username, password):
        return (
            {'authenticated': True, 'username': username},
            None,
            {'display': 'none'},
            {},
        )
    else:
        return {'authenticated': False}, dbc.Alert("Incorrect credentials.", color="danger", dismissable=True), {}, {'display': 'none'}

# Callback pour afficher les relations en attente
@app.callback(
    Output('pending-list', 'children'),
    [
        Input('admin-refresh', 'n_intervals'),
        Input({'type': 'approve-btn', 'index': ALL}, 'n_clicks'),
        Input({'type': 'reject-btn', 'index': ALL}, 'n_clicks'),
    ],
    State('admin-auth', 'data'),
)
def update_pending_list(n_intervals, approve_clicks, reject_clicks, auth_data):
    if not auth_data.get('authenticated'):
        return html.P("Non authentifié", className="text-muted")
    
    # Gérer approbation/rejet
    if ctx.triggered_id and isinstance(ctx.triggered_id, dict):
        if ctx.triggered_id.get('type') in ['approve-btn', 'reject-btn']:
            pending_id = ctx.triggered_id['index']
            
            if ctx.triggered_id['type'] == 'approve-btn':
                db.approve_relation(pending_id, auth_data.get('username', 'admin'))
            else:
                db.reject_relation(pending_id)
    
    # Récupérer les relations en attente
    pending = db.get_pending_relations()
    
    if not pending:
        return dbc.Alert("No pending relationships.", color="info")
    
    items = []
    for rel in pending:
        rel_type_label = get_relation_type_label(rel['relation_type'], relation_types)
        
        items.append(
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5(f"{rel['person1']} - {rel['person2']}", style={'fontWeight': '600'}),
                            html.P([
                                html.Strong("Type: "),
                                rel_type_label,
                                html.Br(),
                                html.Strong("Submitted by: "),
                                rel['submitted_by'],
                                html.Br(),
                                html.Strong("Date: "),
                                rel['submitted_at'],
                            ], style={'fontSize': '14px'}),
                        ], width=8),
                        dbc.Col([
                            dbc.Button(
                                "Approve",
                                id={'type': 'approve-btn', 'index': rel['id']},
                                color="success",
                                size="sm",
                                className="w-100 mb-2",
                            ),
                            dbc.Button(
                                "Reject",
                                id={'type': 'reject-btn', 'index': rel['id']},
                                color="danger",
                                outline=True,
                                size="sm",
                                className="w-100",
                            ),
                        ], width=4),
                    ]),
                ]),
            ], className="mb-3")
        )
    
    return items

# Callback pour afficher l'historique
@app.callback(
    Output('history-list', 'children'),
    [
        Input('refresh-history-btn', 'n_clicks'),
        Input('admin-refresh', 'n_intervals'),
    ],
    State('admin-auth', 'data'),
)
def update_history_list(n_clicks, n_intervals, auth_data):
    if not auth_data.get('authenticated'):
        return html.P("Non authentifié", className="text-muted")
    
    # Récupérer l'historique
    history = db.get_history(limit=100)
    
    if not history:
        return dbc.Alert("📭 Aucun historique pour le moment", color="info")
    
    # Mapper les types d'actions aux icônes et couleurs
    action_config = {
        'APPROVE': {'icon': '✅', 'color': 'success'},
        'REJECT': {'icon': '❌', 'color': 'danger'},
        'DELETE': {'icon': '🗑️', 'color': 'warning'},
        'UPDATE': {'icon': '✏️', 'color': 'info'},
    }
    
    items = []
    for entry in history:
        action_type = entry['action_type']
        config = action_config.get(action_type, {'icon': '📝', 'color': 'secondary'})
        
        # Construire le texte de l'action
        if entry['person1'] and entry['person2']:
            rel_text = f"{entry['person1']} ↔️ {entry['person2']}"
            if entry['relation_type'] is not None:
                rel_type_label = get_relation_type_label(entry['relation_type'], relation_types)
                rel_text += f" ({rel_type_label})"
        else:
            rel_text = "N/A"
        
        details_text = entry.get('details', '') or ''
        performed_by = entry.get('performed_by', 'system')
        
        items.append(
            dbc.ListGroupItem([
                dbc.Row([
                    dbc.Col([
                        html.Span(config['icon'], className="me-2"),
                        html.Strong(action_type),
                    ], width=2),
                    dbc.Col([
                        html.Div(rel_text),
                        html.Small(details_text, className="text-muted"),
                    ], width=6),
                    dbc.Col([
                        html.Small(f"Par: {performed_by}", className="text-muted"),
                    ], width=2),
                    dbc.Col([
                        html.Small(entry['created_at'], className="text-muted"),
                    ], width=2),
                ], align="center"),
            ], color=config['color'], className="mb-1")
        )
    
    return dbc.ListGroup(items)

# Callback pour gérer les relations
@app.callback(
    Output('manage-relations-list', 'children'),
    [
        Input('manage-search', 'value'),
        Input({'type': 'delete-rel-btn', 'index': ALL}, 'n_clicks'),
        Input('save-edit-relation', 'n_clicks'),
    ],
    State('admin-auth', 'data'),
)
def update_manage_list(search_term, delete_clicks, save_clicks, auth_data):
    if not auth_data.get('authenticated'):
        return html.P("Non authentifié", className="text-muted")
    
    # Gérer suppression
    if ctx.triggered_id and isinstance(ctx.triggered_id, dict):
        if ctx.triggered_id.get('type') == 'delete-rel-btn':
            person_data = ctx.triggered_id['index']  # Format: "Person1|Person2"
            p1, p2 = person_data.split('|')
            db.delete_relation(p1, p2, auth_data.get('username', 'admin'))
    
    # Récupérer toutes les relations
    all_relations = db.get_all_relations()
    
    # Filtrer par recherche
    if search_term:
        filtered = [r for r in all_relations if search_term.lower() in r[0].lower() or search_term.lower() in r[1].lower()]
    else:
        filtered = all_relations[:50]  # Limiter à 50 pour performance
    
    if not filtered:
        return dbc.Alert("Aucune relation trouvée", color="info")
    
    items = []
    for i, (p1, p2, rel_type) in enumerate(filtered):
        rel_type_label = get_relation_type_label(rel_type, relation_types)
        person_key = f"{p1}|{p2}"
        
        items.append(
            dbc.ListGroupItem([
                dbc.Row([
                    dbc.Col([
                        html.Strong(f"{p1} ↔️ {p2}"),
                        html.Span(f" ({rel_type_label})", className="text-muted ms-2"),
                    ], width=8),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button(
                                "✏️",
                                id={'type': 'edit-rel-btn', 'index': person_key},
                                color="primary",
                                size="sm",
                                outline=True,
                            ),
                            dbc.Button(
                                "🗑️",
                                id={'type': 'delete-rel-btn', 'index': person_key},
                                color="danger",
                                size="sm",
                                outline=True,
                            ),
                        ], size="sm"),
                    ], width=4, className="text-end"),
                ], align="center"),
            ])
        )
    
    return dbc.ListGroup(items)

# Callback pour ouvrir le modal d'édition
@app.callback(
    [
        Output('edit-relation-modal', 'is_open'),
        Output('edit-relation-data', 'data'),
        Output('edit-relation-info', 'children'),
        Output('edit-relation-type', 'value'),
    ],
    [
        Input({'type': 'edit-rel-btn', 'index': ALL}, 'n_clicks'),
        Input('close-edit-modal', 'n_clicks'),
        Input('save-edit-relation', 'n_clicks'),
    ],
    State('edit-relation-data', 'data'),
)
def toggle_edit_modal(edit_clicks, close_clicks, save_clicks, stored_data):
    if not ctx.triggered_id:
        return False, None, "", None
    
    # Ouvrir le modal
    if isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get('type') == 'edit-rel-btn':
        person_key = ctx.triggered_id['index']
        p1, p2 = person_key.split('|')
        
        # Récupérer le type actuel
        all_relations = db.get_all_relations()
        current_type = None
        for rel in all_relations:
            if rel[0] == p1 and rel[1] == p2:
                current_type = rel[2]
                break
        
        info_text = html.Div([
            html.P([
                html.Strong("Relation: "),
                f"{p1} ↔️ {p2}",
            ]),
        ])
        
        return True, {'person1': p1, 'person2': p2}, info_text, current_type
    
    # Fermer le modal
    return False, None, "", None

# Callback pour sauvegarder l'édition
@app.callback(
    Output('edit-message', 'children'),
    Input('save-edit-relation', 'n_clicks'),
    [
        State('edit-relation-data', 'data'),
        State('edit-relation-type', 'value'),
        State('admin-auth', 'data'),
    ],
)
def save_relation_edit(n_clicks, relation_data, new_type, auth_data):
    if not n_clicks or not relation_data:
        return ""
    
    if not auth_data.get('authenticated'):
        return dbc.Alert("Not authenticated.", color="danger", dismissable=True)
    
    p1 = relation_data['person1']
    p2 = relation_data['person2']
    
    success = db.update_relation_type(p1, p2, new_type, auth_data.get('username', 'admin'))
    
    if success:
        return dbc.Alert("Relationship updated successfully!", color="success", dismissable=True)
    else:
        return dbc.Alert("Error updating relationship.", color="danger", dismissable=True)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SOCIAL NETWORK ANALYZER")
    print("="*60)
    print(f"\nData: {total_nodes} persons, {total_edges} relationships")
    print(f"\nDashboard: http://localhost:8050")
    print(f"Admin Panel: http://localhost:8050/admin")
    print(f"\nAdmin credentials: admin / admin123")
    print("\nVisitors: View graph + Propose relationship")
    print("Admins: Approve, View history, Manage relationships")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=8050)
