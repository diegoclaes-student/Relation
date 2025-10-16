#!/usr/bin/env python3
"""
Social Network Analyzer - Version REFACTORISÉE
Architecture modulaire avec Services + Repositories
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, ctx, no_update
import dash_bootstrap_components as dbc

# Ancienne DB (pour compatibilité temporaire)
from database import RelationDB, RELATION_TYPES

# Nouvelle architecture
from database.persons import person_repository
from database.relations import relation_repository
from services.symmetry import symmetry_manager
from services.graph_builder import graph_builder
from services.history import history_service
from utils.constants import RELATION_TYPES as RELATION_TYPES_NEW

from graph import compute_layout, make_figure
from admin_components import create_admin_dashboard

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v6.1.1/css/all.css"],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True
)

db = RelationDB()
app.title = "Social Network Analyzer"

# CSS moderne
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

# Layout corrigé
app.layout = html.Div([
    # Store pour la session - storage_type par défaut est 'memory'
    dcc.Store(id='session-store', data={'logged_in': False, 'username': ''}),
    
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
                html.H5("Network Stats"),
                html.Div(id='stats-content')
            ], className='stats-card'),
            
        ], className='controls-panel'),
        
    ], className='main-container'),
    
    # Container pour les modals
    html.Div(id='modal-container'),
    
    # INTERVAL DÉSACTIVÉ pour éviter les rechargements intempestifs
    # dcc.Interval(id='refresh-interval', interval=5000, n_intervals=0),
])

# ===== CALLBACK 1: Graphique - REFACTORISÉ =====
@app.callback(
    Output('network-graph', 'figure'),
    Input('layout-dropdown', 'value'),
    prevent_initial_call=False  # Doit charger au démarrage
)
def update_graph(layout_type):
    """
    Mise à jour du graphique avec nouvelle architecture
    - Utilise RelationRepository pour déduplication automatique
    - Utilise GraphBuilder avec cache intelligent
    """
    # Récupérer relations avec déduplication automatique
    relations = relation_repository.read_all(deduplicate=True)
    
    if not relations:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune relation à afficher", 
            xref="paper", yref="paper", 
            x=0.5, y=0.5, 
            showarrow=False,
            font=dict(size=20, color="#999")
        )
        return fig
    
    # ✅ Construction graphe avec cache (évite reconstructions inutiles)
    G = graph_builder.build_graph(relations, deduplicate=False, use_cache=True)
    
    # Layout
    pos = compute_layout(G, mode=layout_type)
    
    # Figure
    fig = make_figure(G, pos)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        hovermode='closest',
    )
    
    return fig

# ===== CALLBACK 2: Stats - MANUEL uniquement =====
@app.callback(
    Output('stats-content', 'children'),
    Input('layout-dropdown', 'value'),  # Trigger sur changement layout seulement
    prevent_initial_call=False
)
def update_stats(layout_type):
    """Mise à jour des stats - SANS auto-refresh"""
    persons = db.get_all_persons()
    relations = db.get_all_relations()
    pending = db.get_pending_relations()
    
    return html.Div([
        html.Div([html.Span("Persons"), html.Span(f"{len(persons)}", className='stat-value')], className='stat-item'),
        html.Div([html.Span("Relations"), html.Span(f"{len(relations)}", className='stat-value')], className='stat-item'),
        html.Div([html.Span("Pending"), html.Span(f"{len(pending)}", className='stat-value')], className='stat-item'),
    ])

# ===== CALLBACK 3: Afficher modals - CORRIGÉ =====
@app.callback(
    Output('modal-container', 'children'),
    [Input('btn-propose', 'n_clicks'),
     Input('btn-admin', 'n_clicks')],
    [State('session-store', 'data')],
    prevent_initial_call=True
)
def show_modal(propose_clicks, admin_clicks, session):
    """Affiche le modal approprié selon le bouton cliqué"""
    if not ctx.triggered:
        return no_update
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # S'assurer que session est valide
    if not isinstance(session, dict):
        session = {'logged_in': False, 'username': ''}
    
    # ===== MODAL PROPOSITION =====
    if trigger == 'btn-propose':
        persons = sorted([p['name'] for p in db.get_all_persons()])
        return dbc.Modal([
            dbc.ModalHeader("➕ Proposer une nouvelle relation"),
            dbc.ModalBody([
                html.P("✨ La relation sera automatiquement symétrisée après approbation", 
                      style={'fontSize': '13px', 'color': '#666'}),
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
                html.Div(id='propose-result', style={'marginTop': '15px'})
            ]),
            dbc.ModalFooter([
                dbc.Button("Envoyer", id='propose-submit', color="success"),
                dbc.Button("Fermer", id='propose-close', color="secondary"),
            ])
        ], id='propose-modal', is_open=True, size="lg")
    
    # ===== MODAL ADMIN =====
    elif trigger == 'btn-admin':
        # Vérifier si connecté
        if session.get('logged_in'):
            # Panel admin
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
                    dbc.Button("🚪 Déconnexion", id='admin-logout', color="warning"),
                    dbc.Button("Fermer", id='admin-close', color="secondary"),
                ])
            ], id='admin-modal', is_open=True, size="xl")
        else:
            # Modal de login
            return dbc.Modal([
                dbc.ModalHeader("🔐 Admin Login"),
                dbc.ModalBody([
                    dbc.Label("Username"),
                    dbc.Input(id='login-username', type='text', placeholder='admin', value=''),
                    html.Br(),
                    dbc.Label("Password"),
                    dbc.Input(id='login-password', type='password', placeholder='••••••', value=''),
                    html.Div(id='login-feedback', style={'marginTop': '15px'})
                ]),
                dbc.ModalFooter([
                    dbc.Button("Login", id='login-submit', color="success"),
                    dbc.Button("Annuler", id='login-cancel', color="secondary"),
                ])
            ], id='login-modal', is_open=True)
    
    return no_update

# ===== CALLBACK 4: Gérer proposition - CORRIGÉ =====
@app.callback(
    [Output('propose-modal', 'is_open'),
     Output('propose-result', 'children')],
    [Input('propose-submit', 'n_clicks'),
     Input('propose-close', 'n_clicks')],
    [State('propose-p1', 'value'),
     State('propose-p2', 'value'),
     State('propose-type', 'value')],
    prevent_initial_call=True
)
def handle_propose(submit, close, p1, p2, rel_type):
    """Gère la soumission d'une proposition"""
    if not ctx.triggered:
        return no_update, no_update
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger == 'propose-close':
        return False, ""
    
    if trigger == 'propose-submit':
        if not p1 or not p2:
            return True, dbc.Alert("Sélectionnez les deux personnes", color="warning")
        if p1 == p2:
            return True, dbc.Alert("Les personnes doivent être différentes", color="warning")
        
        success = db.submit_pending_relation(p1, p2, rel_type, "user", "")
        if success:
            return False, dbc.Alert("✅ Proposition envoyée !", color="success")
        else:
            return True, dbc.Alert("Cette relation est déjà en attente", color="info")
    
    return no_update, no_update

# ===== CALLBACK 5: Gérer login - CORRIGÉ =====
@app.callback(
    [Output('login-modal', 'is_open'),
     Output('login-feedback', 'children'),
     Output('session-store', 'data'),
     Output('modal-container', 'children', allow_duplicate=True)],
    [Input('login-submit', 'n_clicks'),
     Input('login-cancel', 'n_clicks')],
    [State('login-username', 'value'),
     State('login-password', 'value')],
    prevent_initial_call=True
)
def handle_login(submit, cancel, username, password):
    """Gère la connexion admin"""
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    print(f"🔍 handle_login appelé: trigger={trigger}")
    
    if trigger == 'login-cancel':
        print("❌ Login annulé")
        return False, "", {'logged_in': False, 'username': ''}, no_update
    
    if trigger == 'login-submit':
        if not username or not password:
            print("⚠️ Identifiants manquants")
            return True, dbc.Alert("Entrez vos identifiants", color="warning"), {'logged_in': False, 'username': ''}, no_update
        
        if db.verify_admin(username, password):
            print(f"✅ Login réussi: {username}")
            # ✅ Connexion réussie - fermer le modal login ET ouvrir le panel admin
            new_session = {'logged_in': True, 'username': username}
            
            # Créer le modal admin
            admin_panel = dbc.Modal([
                dbc.ModalHeader([
                    html.Span("🎯 Admin Dashboard", style={'flex': '1'}),
                    html.Small(f"👤 {username}", style={'marginRight': '15px', 'color': '#64748b'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                dbc.ModalBody([
                    create_admin_dashboard(db)
                ], style={'maxHeight': '70vh', 'overflowY': 'auto'}),
                dbc.ModalFooter([
                    dbc.Button("🚪 Déconnexion", id='admin-logout', color="warning"),
                    dbc.Button("Fermer", id='admin-close', color="secondary"),
                ])
            ], id='admin-modal', is_open=True, size="xl")
            
            return False, None, new_session, admin_panel
        else:
            return True, dbc.Alert("❌ Identifiants incorrects", color="danger"), {'logged_in': False, 'username': ''}, no_update
    
    return no_update, no_update, no_update, no_update

# ===== CALLBACK 6: Gérer déconnexion - CORRIGÉ =====
@app.callback(
    [Output('session-store', 'data', allow_duplicate=True),
     Output('admin-modal', 'is_open')],
    [Input('admin-logout', 'n_clicks')],
    prevent_initial_call=True
)
def handle_logout(n):
    """Déconnexion - avec vérification stricte du trigger"""
    # ⚠️ CRITIQUE: Vérifier que c'est un vrai clic, pas une création de composant
    if not ctx.triggered:
        print("🔍 handle_logout: Aucun trigger, ignoré")
        return no_update, no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(f"🔍 handle_logout appelé: trigger={trigger_id}, n_clicks={n}")
    
    # Ne déclencher QUE si c'est vraiment le bouton logout
    if trigger_id == 'admin-logout' and n and n > 0:
        print(f"✅ Déconnexion effectuée")
        return {'logged_in': False, 'username': ''}, False
    
    print(f"⚠️ handle_logout: Trigger invalide ou n_clicks={n}, ignoré")
    return no_update, no_update

# ===== CALLBACK 7: Fermer modal admin - CORRIGÉ =====
@app.callback(
    Output('admin-modal', 'is_open', allow_duplicate=True),
    [Input('admin-close', 'n_clicks')],
    prevent_initial_call=True
)
def close_admin_modal(n):
    """Ferme le modal admin SANS déconnecter - avec vérification stricte"""
    # ⚠️ CRITIQUE: Vérifier que c'est un vrai clic
    if not ctx.triggered:
        print("🔍 close_admin_modal: Aucun trigger, ignoré")
        return no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(f"🔍 close_admin_modal appelé: trigger={trigger_id}, n_clicks={n}")
    
    # Ne fermer QUE si c'est vraiment le bouton close
    if trigger_id == 'admin-close' and n and n > 0:
        print(f"✅ Modal fermé (session conservée)")
        return False
    
    print(f"⚠️ close_admin_modal: Trigger invalide ou n_clicks={n}, ignoré")
    return no_update

# ===== CALLBACK 8: Actions admin - REFACTORISÉ =====
@app.callback(
    Output('modal-container', 'children', allow_duplicate=True),
    [Input({'type': 'btn-approve', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-reject', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-delete', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-undo', 'index': ALL}, 'n_clicks')],
    [State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_admin_actions(approve, reject, delete, undo, session):
    """
    Gère les actions admin avec nouvelle architecture
    - Utilise RelationRepository pour garantir symétrie
    - Enregistre dans HistoryService pour undo
    """
    if not ctx.triggered:
        print("🔍 handle_admin_actions: Aucun trigger, ignoré")
        return no_update
    
    trigger = ctx.triggered_id
    if not trigger:
        print("🔍 handle_admin_actions: trigger_id vide, ignoré")
        return no_update
    
    # Vérifier qu'il y a eu un vrai clic
    trigger_prop = ctx.triggered[0]['prop_id']
    trigger_value = ctx.triggered[0]['value']
    print(f"🔍 handle_admin_actions appelé: trigger_prop={trigger_prop}, value={trigger_value}, trigger_id={trigger}")
    
    if '.n_clicks' not in trigger_prop:
        print(f"⚠️ handle_admin_actions: pas de n_clicks dans trigger_prop, ignoré")
        return no_update
    
    # Ignorer si n_clicks est None ou 0 (création de composant)
    if trigger_value is None or trigger_value == 0:
        print(f"⚠️ handle_admin_actions: n_clicks={trigger_value}, ignoré (pas un vrai clic)")
        return no_update
    
    action_type = trigger['type']
    index = trigger['index']
    
    print(f"✅ Action admin confirmée: type={action_type}, index={index}")
    
    # Exécuter l'action avec nouvelle architecture
    if action_type == 'btn-approve':
        db.approve_pending_relation(index, "admin")
        
    elif action_type == 'btn-reject':
        db.reject_pending_relation(index, "admin")
        
    elif action_type == 'btn-delete':
        # Supprimer relation avec garantie symétrie
        parts = index.split('|')
        if len(parts) == 3:
            p1, p2, rel_type = parts[0], parts[1], int(parts[2])
            
            # ✅ Utiliser RelationRepository pour suppression symétrique
            success, msg = relation_repository.delete(p1, p2)
            
            if success:
                # Enregistrer dans historique pour undo
                history_service.record_action(
                    action_type='delete_relation',
                    person1=p1,
                    person2=p2,
                    relation_type=rel_type,
                    performed_by=session.get('username', 'admin')
                )
                print(f"🗑️ Relation supprimée: {msg}")
                
                # Invalider cache graphe
                graph_builder.clear_cache()
            else:
                print(f"❌ Erreur suppression: {msg}")
                
    elif action_type == 'btn-undo':
        # ✅ Utiliser HistoryService pour annulation
        success, msg = history_service.undo_last_action()
        
        if success:
            print(f"↩️ Action annulée: {msg}")
            # Invalider cache graphe
            graph_builder.clear_cache()
        else:
            print(f"❌ Erreur undo: {msg}")
    
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
            dbc.Button("🚪 Déconnexion", id='admin-logout', color="warning"),
            dbc.Button("Fermer", id='admin-close', color="secondary"),
        ])
    ], id='admin-modal', is_open=True, size="xl")
    
    return admin_panel

# ===== CALLBACK 9: Gestion des personnes et ajout de relations =====
@app.callback(
    Output('modal-container', 'children', allow_duplicate=True),
    [Input({'type': 'btn-edit-person', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-merge-person', 'index': ALL}, 'n_clicks'),
     Input({'type': 'btn-delete-person', 'index': ALL}, 'n_clicks'),
     Input('btn-admin-add-relation', 'n_clicks')],
    [State('admin-add-person1', 'value'),
     State('admin-add-person2', 'value'),
     State('admin-add-type', 'value'),
     State('admin-add-symmetrize', 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_person_and_relation_actions(edit, merge, delete_person, add_relation_clicks,
                                      person1, person2, rel_type, symmetrize, session):
    """Gère les actions sur les personnes et l'ajout de relations"""
    if not ctx.triggered:
        return no_update
    
    trigger = ctx.triggered_id
    if not trigger:
        return no_update
    
    trigger_value = ctx.triggered[0]['value']
    
    # Ignorer si n_clicks est None ou 0
    if trigger_value is None or trigger_value == 0:
        return no_update
    
    print(f"🔍 Person/Relation action: trigger={trigger}, value={trigger_value}")
    
    # Déterminer le type d'action
    if isinstance(trigger, dict):
        action_type = trigger['type']
        index = trigger['index']
        
        if action_type == 'btn-edit-person':
            print(f"✏️ TODO: Éditer la personne: {index}")
            # TODO: Implémenter l'édition de personne
            # Pour l'instant, on rafraîchit juste le modal
            
        elif action_type == 'btn-merge-person':
            print(f"🔀 TODO: Fusionner la personne: {index}")
            # TODO: Implémenter la fusion de personnes
            
        elif action_type == 'btn-delete-person':
            print(f"🗑️ Suppression de la personne: {index}")
            # Supprimer toutes les relations de cette personne
            all_relations = db.get_all_relations()
            for p1, p2, rt in all_relations:
                if p1 == index or p2 == index:
                    db.delete_relation(p1, p2, rt, "admin", auto_symmetrize=False)
            
            # Supprimer la personne de la table persons
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM persons WHERE name = ?", (index,))
            conn.commit()
            conn.close()
            
            db.log_action("DELETE_PERSON", person1=index, details=f"Personne supprimée avec toutes ses relations")
            print(f"✅ Personne {index} supprimée")
            
    elif trigger == 'btn-admin-add-relation':
        # Ajouter une relation directement
        if not person1 or not person2:
            print("⚠️ Erreur: person1 ou person2 manquant")
            return no_update
        
        if person1 == person2:
            print("⚠️ Erreur: une personne ne peut pas avoir de relation avec elle-même")
            return no_update
        
        auto_sym = 'sym' in (symmetrize or [])
        
        # Ajouter la relation
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO relations (person1, person2, relation_type)
                VALUES (?, ?, ?)
            """, (person1, person2, rel_type))
            
            if auto_sym:
                cursor.execute("""
                    INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                    VALUES (?, ?, ?)
                """, (person2, person1, rel_type))
            
            conn.commit()
            db.log_action("ADD", person1, person2, rel_type, "admin", 
                        f"Relation ajoutée directement" + (" avec symétrie" if auto_sym else ""))
            print(f"✅ Relation ajoutée: {person1} → {person2}" + (" (symétrique)" if auto_sym else ""))
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout: {e}")
            conn.rollback()
        finally:
            conn.close()
    
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
            dbc.Button("🚪 Déconnexion", id='admin-logout', color="warning"),
            dbc.Button("Fermer", id='admin-close', color="secondary"),
        ])
    ], id='admin-modal', is_open=True, size="xl")
    
    return admin_panel

if __name__ == '__main__':
    persons = db.get_all_persons()
    relations = db.get_all_relations()
    
    print("\n" + "="*70)
    print("  🌐 SOCIAL NETWORK ANALYZER - Version STABLE")
    print("="*70)
    print(f"\n  📊 Données: {len(persons)} personnes, {len(relations)} relations")
    print(f"  🔐 Admin: admin / admin123")
    print(f"  🚀 URL: http://localhost:8051")
    print(f"\n  ✅ Correctifs appliqués:")
    print(f"     • Auto-refresh DÉSACTIVÉ (pas de rechargement intempestif)")
    print(f"     • Graphique se met à jour uniquement sur changement layout")
    print(f"     • Modals ne rechargent plus le graphique")
    print(f"     • Session persiste après fermeture modal\n")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=8051, debug=True)
