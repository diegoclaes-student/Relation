from __future__ import annotations

"""
Dashboard professionnel pour le graphe social interactif

Fonctionnalités:
- Interface moderne avec sidebar de contrôle
- Communautés colorées avec courbes de Bézier
- Filtres par degré de connexion
- Recherche de personnes
- Statistiques en temps réel
- Export haute qualité
- Navigation fluide et responsive
"""

import math
import networkx as nx
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, List, Tuple

# Importer les fonctions du script graph.py
from graph import compute_layout, scale
from data_loader import load_relations, get_relation_type_label, get_edge_relation_type, RELATION_TYPES

# Configuration de l'app avec thème moderne Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.title = "Centrale Plot1"

# CSS personnalisé - Design moderne inspiré d'Apple  
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Apple Design System */
            :root {
                --apple-text: #1d1d1f;
                --apple-secondary: #86868b;
                --apple-blue: #007aff;
                --apple-bg: #f5f5f7;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
                background-color: var(--apple-bg);
                color: var(--apple-text);
                overflow: hidden;
                height: 100vh;
            }
            
            /* Container en pleine hauteur sans scroll */
            .container-fluid {
                height: 100vh;
                overflow: hidden;
                padding-top: 10px;
            }
            
            /* Row du graphique occupe toute la hauteur disponible */
            .graph-row {
                height: calc(100vh - 80px);
                overflow: hidden;
            }
            
            /* Cards avec glassmorphism */
            .card {
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 0.5px solid rgba(0, 0, 0, 0.1);
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }
            
            .card-header {
                background: transparent;
                border-bottom: 0.5px solid rgba(0, 0, 0, 0.1);
                font-weight: 600;
            }
            
            /* Boutons style iOS */
            .btn {
                border-radius: 10px;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            
            .btn:hover {
                transform: scale(1.02);
            }
            
            /* Scrollbar Apple style */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: transparent;
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
            }
            
            /* Panel scrollable */
            .controls-panel {
                max-height: calc(100vh - 200px);
                overflow-y: auto;
                overflow-x: hidden;
            }
            
            /* Sidebar sticky en pleine hauteur */
            #sidebar-card {
                position: sticky;
                top: 10px;
                max-height: calc(100vh - 20px);
                overflow: hidden;
            }
            
            /* Système de collapse du sidebar */
            #sidebar-col {
                transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            }
            
            #sidebar-col.collapsed {
                max-width: 0 !important;
                flex: 0 0 0% !important;
                padding: 0 !important;
                margin: 0 !important;
                opacity: 0;
                overflow: hidden;
            }
            
            #graph-col {
                transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            }
            
            #graph-col.expanded {
                flex: 0 0 100% !important;
                max-width: 100% !important;
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

# Charger les données
G, relation_types = load_relations()

# Calculer les statistiques
total_nodes = G.number_of_nodes()
total_edges = G.number_of_edges()
indeg = dict(G.in_degree())
outdeg = dict(G.out_degree())
deg_total = {n: indeg.get(n, 0) + outdeg.get(n, 0) for n in G.nodes()}
avg_degree = sum(deg_total.values()) / len(deg_total) if deg_total else 0
max_degree_node = max(deg_total.items(), key=lambda x: x[1]) if deg_total else ("", 0)


def make_graph_figure(
    G: nx.DiGraph,
    layout_mode: str = "community",
    center_node: str | None = None,
    min_degree: int = 0,
    max_degree: int = 1000,
    search_highlight: str = "",
    spread: float = 5.0,
    show_labels: bool = True,
    node_size: int = 15,
    edge_width: float = 2.0,
    dark_mode: bool = False,
) -> go.Figure:
    """Génère la figure Plotly du graphe avec filtres et style moderne coloré par communautés."""
    from networkx.algorithms.community import greedy_modularity_communities
    
    # Filtrer les nœuds par degré
    nodes = list(G.nodes())
    filtered_nodes = [n for n in nodes if min_degree <= deg_total.get(n, 0) <= max_degree]
    
    if not filtered_nodes:
        # Graphe vide si aucun nœud ne correspond
        fig = go.Figure()
        fig.update_layout(
            title="Aucun nœud ne correspond aux filtres",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig
    
    # Sous-graphe filtré
    G_filtered = G.subgraph(filtered_nodes).copy()
    
    # Détecter les communautés pour la coloration
    G_undir = G_filtered.to_undirected()
    communities = list(greedy_modularity_communities(G_undir))
    
    # Palette de couleurs vibrantes pour les communautés
    community_colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
        "#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5",
        "#c49c94", "#f7b6d2", "#c7c7c7", "#dbdb8d", "#9edae5",
    ]
    
    # Mapper chaque nœud à sa communauté
    node_to_community = {}
    for idx, comm in enumerate(communities):
        for node in comm:
            node_to_community[node] = idx
    
    # Layout
    pos = compute_layout(
        G_filtered,
        seed=42,
        spread=spread,
        min_separation=0.08,
        mode=layout_mode,
        center_node=center_node if center_node in G_filtered.nodes() else None,
    )
    
    # Préparer les données des nœuds
    nodes_list = list(G_filtered.nodes())
    deg_filtered = {n: deg_total.get(n, 0) for n in nodes_list}
    
    # Tailles des nœuds basées sur le degré et le paramètre node_size
    base_min = node_size * 0.8  # Taille minimale basée sur node_size
    base_max = node_size * 2.5  # Taille maximale basée sur node_size
    sizes = scale(
        [deg_filtered[n] for n in nodes_list],
        out_min=base_min,
        out_max=base_max,
    )
    
    # Couleurs par communauté
    node_colors = []
    for n in nodes_list:
        comm_idx = node_to_community.get(n, 0)
        if search_highlight and search_highlight.lower() in n.lower():
            node_colors.append("#FF1744")  # Rouge vif pour highlight
        else:
            node_colors.append(community_colors[comm_idx % len(community_colors)])
    
    # Opacité basée sur le degré
    opacities = scale([deg_filtered[n] for n in nodes_list], out_min=0.7, out_max=1.0)
    
    # Tracé des arêtes avec style courbé pour les connexions inter-communautés
    edge_traces = []
    
    # Définir les styles visuels par type de relation (avec largeur basée sur edge_width)
    relation_styles = {
        0: {"color": "#CCCCCC", "width": edge_width * 0.4, "dash": "solid"},      # Bisous: gris clair, fin
        1: {"color": "#FFB74D", "width": edge_width * 0.6, "dash": "solid"},      # Dodo: orange, moyen
        2: {"color": "#E91E63", "width": edge_width * 0.75, "dash": "solid"},     # Baise: rose vif, épais
        3: {"color": "#9C27B0", "width": edge_width * 1.0, "dash": "solid"},      # Couple: violet, très épais
    }
    
    # Séparer arêtes intra-communauté et inter-communauté par type
    intra_edges_by_type = {t: [] for t in relation_styles.keys()}
    inter_edges_by_type = {t: [] for t in relation_styles.keys()}
    
    for src, dst in G_filtered.edges():
        if src in pos and dst in pos:
            src_comm = node_to_community.get(src, 0)
            dst_comm = node_to_community.get(dst, 0)
            rel_type = get_edge_relation_type(G_filtered, src, dst)
            
            if src_comm == dst_comm:
                intra_edges_by_type[rel_type].append((src, dst, src_comm))
            else:
                inter_edges_by_type[rel_type].append((src, dst, src_comm, dst_comm))
    
    # Arêtes intra-communautés (lignes droites, colorées par communauté et type)
    for rel_type, edges in intra_edges_by_type.items():
        style = relation_styles.get(rel_type, relation_styles[0])
        
        for comm_idx in range(len(communities)):
            edge_x, edge_y = [], []
            for src, dst, c_idx in edges:
                if c_idx == comm_idx:
                    x0, y0 = pos[src]
                    x1, y1 = pos[dst]
                    edge_x += [x0, x1, None]
                    edge_y += [y0, y1, None]
            
            if edge_x:
                edge_traces.append(
                    go.Scatter(
                        x=edge_x,
                        y=edge_y,
                        line=dict(
                            width=style["width"],
                            color=community_colors[comm_idx % len(community_colors)],
                            dash=style["dash"]
                        ),
                        hoverinfo="none",
                        mode="lines",
                        opacity=0.5,
                        showlegend=False,
                    )
                )
    
    # Arêtes inter-communautés (courbes, colorées par type de relation)
    for rel_type, edges in inter_edges_by_type.items():
        style = relation_styles.get(rel_type, relation_styles[0])
        
        for src, dst, src_comm, dst_comm in edges:
            x0, y0 = pos[src]
            x1, y1 = pos[dst]
            
            # Créer une courbe de Bézier quadratique
            # Point de contrôle au milieu mais décalé perpendiculairement
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            dx = x1 - x0
            dy = y1 - y0
            length = math.sqrt(dx*dx + dy*dy) or 1
            # Perpendiculaire
            perp_x = -dy / length
            perp_y = dx / length
            # Décalage du point de contrôle (créer la courbure)
            curve_strength = 0.15
            ctrl_x = mid_x + perp_x * length * curve_strength
            ctrl_y = mid_y + perp_y * length * curve_strength
            
            # Générer la courbe
            t_values = [i / 20 for i in range(21)]
            curve_x = []
            curve_y = []
            for t in t_values:
                # Formule de Bézier quadratique: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
                bx = (1-t)**2 * x0 + 2*(1-t)*t * ctrl_x + t**2 * x1
                by = (1-t)**2 * y0 + 2*(1-t)*t * ctrl_y + t**2 * y1
                curve_x.append(bx)
                curve_y.append(by)
            
            edge_traces.append(
                go.Scatter(
                    x=curve_x,
                    y=curve_y,
                    line=dict(
                        width=style["width"],
                        color=style["color"],
                        dash=style["dash"]
                    ),
                    hoverinfo="none",
                    mode="lines",
                    opacity=0.4,
                    showlegend=False,
                )
            )
    
    # Tracé des nœuds
    x_nodes = [pos[n][0] for n in nodes_list]
    y_nodes = [pos[n][1] for n in nodes_list]
    
    # Créer le texte de hover avec la liste complète des connexions ET les types
    hover_text = []
    for n in nodes_list:
        # Récupérer tous les voisins (les relations sont symétriques)
        neighbors = set(G_filtered.successors(n)) | set(G_filtered.predecessors(n))
        
        # Construire dict: neighbor -> liste des types de relations
        neighbor_types = {}
        for neighbor in neighbors:
            # Vérifier dans les deux sens (A->B et B->A)
            types_set = set()
            if G_filtered.has_edge(n, neighbor):
                types_set.add(get_edge_relation_type(G_filtered, n, neighbor))
            if G_filtered.has_edge(neighbor, n):
                types_set.add(get_edge_relation_type(G_filtered, neighbor, n))
            neighbor_types[neighbor] = sorted(types_set)
        
        neighbors_sorted = sorted(neighbors)
        nb_pechos = len(neighbors_sorted) // 2
        
        # Construire le texte
        text = f"<b>{n}</b><br>"
        text += f"<b>Pechos: {nb_pechos}</b><br><br>"
        
        # Afficher chaque voisin avec son/ses type(s) de relation
        for neighbor in neighbors_sorted:
            types = neighbor_types[neighbor]
            type_labels = [get_relation_type_label(t, relation_types) for t in types]
            type_str = ", ".join(type_labels)
            text += f"  • {neighbor} <i>({type_str})</i><br>"
        
        hover_text.append(text)
    
    node_trace = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode="markers",
        hoverinfo="text",
        hovertext=hover_text,
        marker=dict(
            color=node_colors,
            size=sizes,
            opacity=opacities,
            line=dict(width=2, color="white"),
        ),
        name="Personnes",
        showlegend=False,
    )
    
    # Labels avec fond blanc semi-transparent pour lisibilité
    data_traces = edge_traces + [node_trace]
    
    if show_labels:
        # Afficher seulement les labels des nœuds les plus connectés pour éviter surcharge
        top_nodes = sorted(nodes_list, key=lambda n: deg_filtered[n], reverse=True)[:min(30, len(nodes_list))]
        
        label_x, label_y, label_text = [], [], []
        for n in top_nodes:
            x, y = pos[n]
            label_x.append(x)
            label_y.append(y)
            label_text.append(str(n))
        
        label_trace = go.Scatter(
            x=label_x,
            y=label_y,
            mode="text",
            text=label_text,
            textposition="top center",
            textfont=dict(size=10, color="#f5f5f7" if dark_mode else "#000", family="Arial, sans-serif"),
            hoverinfo="skip",
            showlegend=False,
        )
        data_traces.append(label_trace)
    
    # Ne plus créer la légende des communautés (supprimée pour plus d'espace)
    
    # Couleurs selon le mode
    bg_color = "#000000" if dark_mode else "white"
    paper_color = "#1c1c1e" if dark_mode else "#F8F9FA"
    
    fig = go.Figure(data=data_traces)
    fig.update_layout(
        # Pas de titre
        showlegend=False,  # Légende désactivée
        hovermode="closest",
        margin=dict(b=5, l=5, r=5, t=5),  # Marges minimales
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            visible=False,
            fixedrange=False,  # Permet le zoom/pan sur l'axe X
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            visible=False,
            fixedrange=False,  # Permet le zoom/pan sur l'axe Y
        ),
        plot_bgcolor=bg_color,
        paper_bgcolor=paper_color,
        # Pas de hauteur fixe pour permettre l'adaptation
        autosize=True,
        # Configuration pour une navigation fluide et intuitive
        dragmode="pan",  # Mode déplacement par défaut (cliquer-glisser pour se déplacer)
        # uirevision permet de conserver le zoom/position lors des mises à jour
        uirevision="constant",
    )
    
    # Configuration avancée pour améliorer l'interactivité
    fig.update_xaxes(
        scaleanchor=None,
        constrain="domain",
    )
    fig.update_yaxes(
        scaleanchor=None,
        constrain="domain",
    )
    
    return fig


# ============ LAYOUT ============

# Sidebar avec contrôles
sidebar = dbc.Card(
    [
        dbc.CardHeader(
            html.H4([html.I(className="fas fa-sliders-h me-2"), "Contrôles"], className="mb-0"),
            className="bg-primary text-white",
        ),
        dbc.CardBody(
            html.Div([
                # Statistiques
                html.Div(
                    [
                        html.H5([html.I(className="fas fa-chart-bar me-2"), "Statistiques"], className="mb-3"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H6("Personnes", className="text-muted mb-1"),
                                                    html.H3(total_nodes, className="mb-0 text-primary"),
                                                ]
                                            )
                                        ],
                                        className="text-center shadow-sm",
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H6("Relations", className="text-muted mb-1"),
                                                    html.H3(total_edges, className="mb-0 text-success"),
                                                ]
                                            )
                                        ],
                                        className="text-center shadow-sm",
                                    ),
                                    width=6,
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.P([html.B("Plus connecté: "), f"{max_degree_node[0]} ({max_degree_node[1]})"]),
                                        html.P([html.B("Degré moyen: "), f"{avg_degree:.1f}"]),
                                    ],
                                    className="small",
                                )
                            ],
                            className="shadow-sm mb-3",
                        ),
                    ]
                ),
                html.Hr(),
                # Layout
                html.Div(
                    [
                        html.H5([html.I(className="fas fa-project-diagram me-2"), "Layout"], className="mb-3"),
                        dbc.Label("Algorithme"),
                        dcc.Dropdown(
                            id="layout-dropdown",
                            options=[
                                {"label": "🎯 Communautés", "value": "community"},
                                {"label": "🌐 Force-Directed", "value": "spring"},
                                {"label": "📏 Kamada-Kawai", "value": "kk"},
                                {"label": "🔢 Spectral", "value": "spectral"},
                            ],
                            value="community",
                            clearable=False,
                            className="mb-3",
                        ),
                        dbc.Label("Espacement"),
                        dcc.Slider(
                            id="spread-slider",
                            min=2,
                            max=8,
                            step=0.5,
                            value=5.0,
                            marks={i: str(i) for i in range(2, 9, 2)},
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="mb-3",
                        ),
                        dbc.Label("Nœud central"),
                        dcc.Dropdown(
                            id="center-dropdown",
                            options=[{"label": "Aucun", "value": ""}]
                            + [{"label": n, "value": n} for n in sorted(G.nodes())],
                            value="Rachel",
                            clearable=True,
                            placeholder="Sélectionner...",
                            className="mb-3",
                        ),
                    ]
                ),
                html.Hr(),
                # Filtres
                html.Div(
                    [
                        html.H5([html.I(className="fas fa-filter me-2"), "Filtres"], className="mb-3"),
                        dbc.Label("Degré minimum"),
                        dcc.Slider(
                            id="min-degree-slider",
                            min=0,
                            max=max(deg_total.values()) if deg_total else 10,
                            step=1,
                            value=0,
                            marks={i: str(i) for i in range(0, (max(deg_total.values()) if deg_total else 10) + 1, 2)},
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="mb-3",
                        ),
                        dbc.Label("Degré maximum"),
                        dcc.Slider(
                            id="max-degree-slider",
                            min=0,
                            max=max(deg_total.values()) if deg_total else 10,
                            step=1,
                            value=max(deg_total.values()) if deg_total else 10,
                            marks={i: str(i) for i in range(0, (max(deg_total.values()) if deg_total else 10) + 1, 2)},
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="mb-3",
                        ),
                        dbc.Label("Recherche"),
                        dbc.Input(
                            id="search-input",
                            type="text",
                            placeholder="Chercher une personne...",
                            className="mb-2",
                        ),
                        dbc.FormText("Les résultats seront mis en surbrillance en rouge"),
                    ]
                ),
                html.Hr(),
                # Options d'affichage
                html.Div(
                    [
                        html.H5([html.I(className="fas fa-eye me-2"), "Affichage"], className="mb-3"),
                        dbc.Checklist(
                            id="show-labels-check",
                            options=[{"label": " Afficher les noms", "value": True}],
                            value=[True],
                            switch=True,
                        ),
                    ]
                ),
                html.Hr(),
                # Personnalisation
                html.Div(
                    [
                        html.H5([html.I(className="fas fa-palette me-2"), "Personnalisation"], className="mb-3"),
                        dbc.Label("Taille des nœuds"),
                        dcc.Slider(
                            id="node-size-slider",
                            min=5,
                            max=30,
                            step=1,
                            value=15,
                            marks={5: '5', 15: '15', 30: '30'},
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="mb-3",
                        ),
                        dbc.Label("Épaisseur des liens"),
                        dcc.Slider(
                            id="edge-width-slider",
                            min=0.5,
                            max=5,
                            step=0.5,
                            value=2.0,
                            marks={0.5: '0.5', 2: '2', 5: '5'},
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="mb-3",
                        ),
                    ]
                ),
            ], className="controls-panel")
        ),
    ],
    className="shadow-sm",
    style={"position": "sticky", "top": "10px"},
    id="sidebar-card",
)

# Layout principal
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            [
                                html.I(className="fas fa-network-wired me-3", style={'color': '#1d1d1f'}),
                                "Centrale Plot1",
                            ],
                            style={'color': '#1d1d1f'},
                            className="mb-3",
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-bars me-2"), "Menu"],
                            id="toggle-sidebar",
                            color="primary",
                            className="mb-3",
                            style={'display': 'none'}
                        ),
                    ],
                    width=12,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(sidebar, width=12, md=3, className="mb-3", id="sidebar-col"),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        dcc.Loading(
                                            type="circle",
                                            children=dcc.Graph(
                                                id="social-graph",
                                                style={'height': '85vh'},
                                                config={
                                                    # Export haute qualité
                                                    "toImageButtonOptions": {
                                                        "format": "png",
                                                        "filename": "graphe_social",
                                                        "height": 2400,
                                                        "width": 3200,
                                                        "scale": 2,
                                                    },
                                                    # Masquer la barre d'outils
                                                    "displayModeBar": False,
                                                    "displaylogo": False,
                                                    # Zoom avec molette de souris/trackpad activé
                                                    "scrollZoom": True,
                                                    # Double-clic pour reset le zoom
                                                    "doubleClick": "reset",
                                                },
                                            ),
                                        )
                                    ]
                                )
                            ],
                            className="shadow-sm",
                        )
                    ],
                    width=12,
                    md=9,
                    id="graph-col",
                ),
            ],
            className="graph-row",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Footer(
                        [
                            html.Hr(),
                            html.P(
                                [
                                    html.I(className="fas fa-heart text-danger me-2"),
                                    "Graphe Social Dashboard - Propulsé par Plotly Dash",
                                ],
                                className="text-center text-muted small",
                            ),
                        ]
                    ),
                    width=12,
                )
            ]
        ),
    ],
    fluid=True,
    className="py-4",
)


# ============ CALLBACKS ============

@app.callback(
    Output("social-graph", "figure"),
    [
        Input("layout-dropdown", "value"),
        Input("center-dropdown", "value"),
        Input("min-degree-slider", "value"),
        Input("max-degree-slider", "value"),
        Input("search-input", "value"),
        Input("spread-slider", "value"),
        Input("show-labels-check", "value"),
        Input("node-size-slider", "value"),
        Input("edge-width-slider", "value"),
    ],
)
def update_graph(layout_mode, center_node, min_degree, max_degree, search_text, spread, show_labels_check, 
                 node_size, edge_width):
    """Met à jour le graphe en fonction des contrôles."""
    show_labels = True in (show_labels_check or [])
    
    return make_graph_figure(
        G,
        layout_mode=layout_mode,
        center_node=center_node if center_node else None,
        min_degree=min_degree,
        max_degree=max_degree,
        search_highlight=search_text if search_text else "",
        spread=spread,
        show_labels=show_labels,
        node_size=node_size or 15,
        edge_width=edge_width or 2.0,
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Lancement du Dashboard Centrale Plot1")
    print("=" * 60)
    print(f"\n📊 Données chargées: {total_nodes} personnes, {total_edges} relations")
    print(f"\n🌐 Accédez au dashboard sur: http://localhost:8052")
    print("\n💡 Fonctionnalités:")
    print("   • Filtres interactifs par degré de connexion")
    print("   • Recherche et highlighting de personnes")
    print("   • Plusieurs algorithmes de layout")
    print("   • Export PNG haute qualité (3200x2400px)")
    print("   • Zoom, pan, et sélection interactive")
    print("   • Sliders de personnalisation (taille nœuds, épaisseur liens)")
    print("\n⌨️  Appuyez sur Ctrl+C pour arrêter le serveur\n")
    print("=" * 60 + "\n")
    
    app.run(debug=False, host="127.0.0.1", port=8052)
