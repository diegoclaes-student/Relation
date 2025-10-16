#!/usr/bin/env python3
"""
Modals pour CRUD Personnes
- Modal Édition personne (modifier nom, genre, orientation)
- Modal Fusion personnes (fusionner 2 personnes)
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from utils.constants import GENDERS, SEXUAL_ORIENTATIONS


def create_edit_person_modal():
    """
    Modal pour éditer une personne
    Permet de modifier: nom, genre, orientation sexuelle
    """
    return dbc.Modal([
        dbc.ModalHeader("✏️ Modifier une Personne"),
        dbc.ModalBody([
            # Sélection de la personne à éditer
            html.Label("Personne à modifier:", className="form-label fw-bold"),
            dcc.Dropdown(
                id='edit-person-select',
                placeholder="Sélectionnez une personne...",
                clearable=False
            ),
            
            html.Hr(),
            
            # Champ nom
            html.Label("Nouveau nom (optionnel):", className="form-label mt-3"),
            dbc.Input(
                id='edit-person-name',
                placeholder="Laisser vide pour ne pas modifier",
                type="text"
            ),
            
            # Champ genre
            html.Label("Genre:", className="form-label mt-3"),
            dcc.Dropdown(
                id='edit-person-gender',
                options=[
                    {'label': GENDERS[k], 'value': k} 
                    for k in GENDERS.keys() if k is not None
                ],
                placeholder="Sélectionnez un genre...",
                clearable=True
            ),
            
            # Champ orientation
            html.Label("Orientation sexuelle:", className="form-label mt-3"),
            dcc.Dropdown(
                id='edit-person-orientation',
                options=[
                    {'label': SEXUAL_ORIENTATIONS[k], 'value': k}
                    for k in SEXUAL_ORIENTATIONS.keys() if k is not None
                ],
                placeholder="Sélectionnez une orientation...",
                clearable=True
            ),
            
            html.Hr(),
            
            # Message de résultat
            html.Div(id='edit-person-result', className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("💾 Enregistrer", id='edit-person-submit', color="primary"),
            dbc.Button("Annuler", id='edit-person-close', color="secondary")
        ])
    ], id='edit-person-modal', size="lg", is_open=False)


def create_merge_persons_modal():
    """
    Modal pour fusionner deux personnes
    Toutes les relations de la source sont transférées vers la cible
    La source est ensuite supprimée
    """
    return dbc.Modal([
        dbc.ModalHeader("🔀 Fusionner des Personnes"),
        dbc.ModalBody([
            dbc.Alert([
                html.Strong("⚠️ Attention: "),
                "Cette opération est irréversible ! ",
                "Toutes les relations de la personne source seront transférées vers la cible, ",
                "puis la source sera supprimée."
            ], color="warning"),
            
            # Personne source (à supprimer)
            html.Label("Personne à fusionner (sera supprimée):", className="form-label fw-bold mt-3"),
            dcc.Dropdown(
                id='merge-person-source',
                placeholder="Sélectionnez la personne source...",
                clearable=False
            ),
            
            html.Div([
                html.I(className="fas fa-arrow-down fa-2x text-primary", 
                      style={'display': 'block', 'textAlign': 'center', 'margin': '15px 0'})
            ]),
            
            # Personne cible (conservée)
            html.Label("Personne cible (sera conservée):", className="form-label fw-bold"),
            dcc.Dropdown(
                id='merge-person-target',
                placeholder="Sélectionnez la personne cible...",
                clearable=False
            ),
            
            html.Hr(),
            
            # Résumé de la fusion
            html.Div(id='merge-person-preview', className="mt-3"),
            
            # Message de résultat
            html.Div(id='merge-person-result', className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("🔀 Fusionner", id='merge-person-submit', color="danger"),
            dbc.Button("Annuler", id='merge-person-close', color="secondary")
        ])
    ], id='merge-person-modal', size="lg", is_open=False)


def create_delete_person_modal():
    """
    Modal pour supprimer une personne
    Avec option de supprimer les relations en cascade
    """
    return dbc.Modal([
        dbc.ModalHeader("🗑️ Supprimer une Personne"),
        dbc.ModalBody([
            dbc.Alert([
                html.Strong("⚠️ Attention: "),
                "Cette opération supprimera la personne et toutes ses relations !"
            ], color="danger"),
            
            # Sélection personne
            html.Label("Personne à supprimer:", className="form-label fw-bold mt-3"),
            dcc.Dropdown(
                id='delete-person-select',
                placeholder="Sélectionnez une personne...",
                clearable=False
            ),
            
            # Info sur nombre de relations
            html.Div(id='delete-person-info', className="mt-3"),
            
            # Checkbox cascade
            dbc.Checklist(
                id='delete-person-cascade',
                options=[
                    {'label': ' Supprimer aussi toutes les relations de cette personne', 'value': 'cascade'}
                ],
                value=['cascade'],
                className="mt-3"
            ),
            
            html.Hr(),
            
            # Message de résultat
            html.Div(id='delete-person-result', className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("🗑️ Supprimer", id='delete-person-submit', color="danger"),
            dbc.Button("Annuler", id='delete-person-close', color="secondary")
        ])
    ], id='delete-person-modal', size="lg", is_open=False)
