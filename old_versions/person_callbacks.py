#!/usr/bin/env python3
"""
Callbacks pour CRUD Personnes
- Édition personne
- Fusion personnes  
- Suppression personne
"""

from dash import Input, Output, State, ctx, no_update, html
import dash_bootstrap_components as dbc

from database.persons import person_repository
from services.graph_builder import graph_builder
from services.history import history_service


def register_person_crud_callbacks(app, db):
    """Enregistre tous les callbacks CRUD personnes"""
    
    # ===== CALLBACK: Ouvrir modal édition =====
    @app.callback(
        [Output('edit-person-modal', 'is_open'),
         Output('edit-person-select', 'options')],
        [Input({'type': 'btn-edit-person', 'index': 'open'}, 'n_clicks'),
         Input('edit-person-close', 'n_clicks')],
        prevent_initial_call=True
    )
    def toggle_edit_modal(open_clicks, close_clicks):
        """Ouvre/ferme modal édition"""
        if not ctx.triggered:
            return no_update, no_update
        
        trigger_id = ctx.triggered_id
        
        if trigger_id == 'edit-person-close':
            return False, no_update
        
        # Ouvrir modal: charger liste personnes
        persons = person_repository.read_all()
        options = [{'label': p['name'], 'value': p['id']} for p in persons]
        
        return True, options
    
    
    # ===== CALLBACK: Soumettre édition =====
    @app.callback(
        [Output('edit-person-modal', 'is_open', allow_duplicate=True),
         Output('edit-person-result', 'children')],
        Input('edit-person-submit', 'n_clicks'),
        [State('edit-person-select', 'value'),
         State('edit-person-name', 'value'),
         State('edit-person-gender', 'value'),
         State('edit-person-orientation', 'value')],
        prevent_initial_call=True
    )
    def submit_edit_person(n_clicks, person_id, new_name, gender, orientation):
        """Soumet l'édition d'une personne"""
        if not person_id:
            return True, dbc.Alert("Sélectionnez une personne", color="warning")
        
        # Construire dict de modifications
        updates = {}
        if new_name and new_name.strip():
            updates['name'] = new_name.strip()
        if gender:
            updates['gender'] = gender
        if orientation:
            updates['orientation'] = orientation
        
        if not updates:
            return True, dbc.Alert("Aucune modification spécifiée", color="info")
        
        # Appliquer modifications
        success, msg = person_repository.update(person_id, **updates)
        
        if success:
            # Invalider cache graphe
            graph_builder.clear_cache()
            
            # Enregistrer dans historique
            history_service.record_action(
                action_type='edit_person',
                person1=str(person_id),
                details=str(updates),
                performed_by='user'
            )
            
            return False, dbc.Alert(f"✅ {msg}", color="success")
        else:
            return True, dbc.Alert(f"❌ {msg}", color="danger")
    
    
    # ===== CALLBACK: Ouvrir modal fusion =====
    @app.callback(
        [Output('merge-person-modal', 'is_open'),
         Output('merge-person-source', 'options'),
         Output('merge-person-target', 'options')],
        [Input({'type': 'btn-merge-person', 'index': 'open'}, 'n_clicks'),
         Input('merge-person-close', 'n_clicks')],
        prevent_initial_call=True
    )
    def toggle_merge_modal(open_clicks, close_clicks):
        """Ouvre/ferme modal fusion"""
        if not ctx.triggered:
            return no_update, no_update, no_update
        
        trigger_id = ctx.triggered_id
        
        if trigger_id == 'merge-person-close':
            return False, no_update, no_update
        
        # Ouvrir modal: charger liste personnes
        persons = person_repository.read_all()
        options = [{'label': p['name'], 'value': p['id']} for p in persons]
        
        return True, options, options
    
    
    # ===== CALLBACK: Preview fusion =====
    @app.callback(
        Output('merge-person-preview', 'children'),
        [Input('merge-person-source', 'value'),
         Input('merge-person-target', 'value')],
        prevent_initial_call=True
    )
    def preview_merge(source_id, target_id):
        """Affiche un aperçu de la fusion"""
        if not source_id or not target_id:
            return ""
        
        if source_id == target_id:
            return dbc.Alert("⚠️ Source et cible doivent être différentes", color="warning")
        
        # Récupérer infos
        source = person_repository.read(source_id)
        target = person_repository.read(target_id)
        
        if not source or not target:
            return ""
        
        # Compter relations
        source_rels = person_repository.get_relation_count(source_id)
        target_rels = person_repository.get_relation_count(target_id)
        
        return dbc.Alert([
            html.H6("📋 Aperçu de la fusion:", className="mb-3"),
            html.Ul([
                html.Li([
                    html.Strong(f"{source['name']}"),
                    f" ({source_rels} relations) → sera supprimée"
                ]),
                html.Li([
                    html.Strong(f"{target['name']}"),
                    f" ({target_rels} relations) → recevra toutes les relations"
                ]),
                html.Li([
                    "Relations finales: environ ",
                    html.Strong(f"{source_rels + target_rels}"),
                    " (dédupliquées si doublons)"
                ])
            ])
        ], color="info")
    
    
    # ===== CALLBACK: Soumettre fusion =====
    @app.callback(
        [Output('merge-person-modal', 'is_open', allow_duplicate=True),
         Output('merge-person-result', 'children')],
        Input('merge-person-submit', 'n_clicks'),
        [State('merge-person-source', 'value'),
         State('merge-person-target', 'value')],
        prevent_initial_call=True
    )
    def submit_merge_persons(n_clicks, source_id, target_id):
        """Soumet la fusion de personnes"""
        if not source_id or not target_id:
            return True, dbc.Alert("Sélectionnez source et cible", color="warning")
        
        # Fusionner
        success, msg = person_repository.merge(source_id, target_id)
        
        if success:
            # Invalider cache graphe
            graph_builder.clear_cache()
            
            # Enregistrer dans historique
            history_service.record_action(
                action_type='merge_persons',
                person1=str(source_id),
                person2=str(target_id),
                details=msg,
                performed_by='user'
            )
            
            return False, dbc.Alert(f"✅ {msg}", color="success")
        else:
            return True, dbc.Alert(f"❌ {msg}", color="danger")
    
    
    # ===== CALLBACK: Ouvrir modal suppression =====
    @app.callback(
        [Output('delete-person-modal', 'is_open'),
         Output('delete-person-select', 'options')],
        [Input({'type': 'btn-delete-person', 'index': 'open'}, 'n_clicks'),
         Input('delete-person-close', 'n_clicks')],
        prevent_initial_call=True
    )
    def toggle_delete_modal(open_clicks, close_clicks):
        """Ouvre/ferme modal suppression"""
        if not ctx.triggered:
            return no_update, no_update
        
        trigger_id = ctx.triggered_id
        
        if trigger_id == 'delete-person-close':
            return False, no_update
        
        # Ouvrir modal: charger liste personnes
        persons = person_repository.read_all()
        options = [{'label': p['name'], 'value': p['id']} for p in persons]
        
        return True, options
    
    
    # ===== CALLBACK: Info suppression =====
    @app.callback(
        Output('delete-person-info', 'children'),
        Input('delete-person-select', 'value'),
        prevent_initial_call=True
    )
    def show_delete_info(person_id):
        """Affiche infos sur la personne à supprimer"""
        if not person_id:
            return ""
        
        person = person_repository.read(person_id)
        if not person:
            return ""
        
        rel_count = person_repository.get_relation_count(person_id)
        
        return dbc.Alert([
            html.Strong(f"👤 {person['name']}"),
            html.Br(),
            f"📊 {rel_count} relations seront également supprimées"
        ], color="info")
    
    
    # ===== CALLBACK: Soumettre suppression =====
    @app.callback(
        [Output('delete-person-modal', 'is_open', allow_duplicate=True),
         Output('delete-person-result', 'children')],
        Input('delete-person-submit', 'n_clicks'),
        [State('delete-person-select', 'value'),
         State('delete-person-cascade', 'value')],
        prevent_initial_call=True
    )
    def submit_delete_person(n_clicks, person_id, cascade_value):
        """Soumet la suppression d'une personne"""
        if not person_id:
            return True, dbc.Alert("Sélectionnez une personne", color="warning")
        
        cascade = 'cascade' in (cascade_value or [])
        
        # Supprimer
        success, msg = person_repository.delete(person_id, cascade=cascade)
        
        if success:
            # Invalider cache graphe
            graph_builder.clear_cache()
            
            # Enregistrer dans historique
            history_service.record_action(
                action_type='delete_person',
                person1=str(person_id),
                details=msg,
                performed_by='user'
            )
            
            return False, dbc.Alert(f"✅ {msg}", color="success")
        else:
            return True, dbc.Alert(f"❌ {msg}", color="danger")
