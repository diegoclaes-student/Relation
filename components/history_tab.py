"""
History/Audit Tab Component
Affiche l'historique des modifications
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime


def create_history_tab():
    """Crée l'onglet Historique des modifications"""
    return html.Div([
        html.Div("📋 Historique des Modifications", className='section-title', style={'marginBottom': '20px'}),
        
        # Filters
        html.Div([
            html.Div([
                html.Label("Filtrer par type:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Dropdown(
                    id='history-filter-type',
                    options=[
                        {'label': 'Tous', 'value': 'all'},
                        {'label': 'Personnes', 'value': 'person'},
                        {'label': 'Relations', 'value': 'relation'},
                        {'label': 'Utilisateurs', 'value': 'user'},
                        {'label': 'Comptes', 'value': 'account'},
                    ],
                    value='all',
                    style={'width': '100%'}
                ),
            ], style={'marginBottom': '15px', 'flex': '1'}),
            
            html.Div([
                html.Label("Filtrer par action:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Dropdown(
                    id='history-filter-action',
                    options=[
                        {'label': 'Tous', 'value': 'all'},
                        {'label': 'Créé', 'value': 'create'},
                        {'label': 'Modifié', 'value': 'update'},
                        {'label': 'Supprimé', 'value': 'delete'},
                        {'label': 'Approuvé', 'value': 'approve'},
                    ],
                    value='all',
                    style={'width': '100%'}
                ),
            ], style={'marginBottom': '15px', 'flex': '1'}),
        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),
        
        # Tabs: Récent vs Annulé
        dcc.Tabs([
            dcc.Tab(label="✅ Modifications Récentes", children=[
                html.Div([
                    html.Div(id='history-list-recent', children=[
                        html.P("Aucune modification", className='text-muted')
                    ]),
                    dbc.Button([
                        html.I(className="fas fa-sync", style={'marginRight': '8px'}),
                        "Actualiser"
                    ], id='btn-refresh-history-recent', color='secondary', className='w-100 mt-3'),
                ], style={'padding': '20px'}),
            ]),
            
            dcc.Tab(label="❌ Modifications Annulées", children=[
                html.Div([
                    html.Div(id='history-list-cancelled', children=[
                        html.P("Aucune modification annulée", className='text-muted')
                    ]),
                    dbc.Button([
                        html.I(className="fas fa-sync", style={'marginRight': '8px'}),
                        "Actualiser"
                    ], id='btn-refresh-history-cancelled', color='secondary', className='w-100 mt-3'),
                ], style={'padding': '20px'}),
            ]),
        ], style={'marginTop': '20px'}),
        
    ])


def render_history_item(record: dict, show_cancel_button: bool = True) -> html.Div:
    """Rend un item d'historique"""
    
    # Format action type
    action_type = record.get('action_type', 'unknown').upper()
    action_icons = {
        'CREATE': '🟢',
        'UPDATE': '🟡',
        'DELETE': '🔴',
        'APPROVE': '✅',
        'CANCEL': '❌',
    }
    icon = action_icons.get(action_type, '📝')
    
    # Format entity type
    entity_type = record.get('entity_type', 'unknown')
    entity_icons = {
        'person': '👤',
        'relation': '🔗',
        'user': '👥',
        'account': '🆔',
    }
    entity_icon = entity_icons.get(entity_type, '📦')
    
    # Format dates
    created_at = record.get('created_at', '')
    if created_at:
        try:
            dt = datetime.fromisoformat(created_at)
            created_at_fmt = dt.strftime('%d/%m/%Y %H:%M:%S')
        except:
            created_at_fmt = created_at[:10]
    else:
        created_at_fmt = 'N/A'
    
    cancelled_at = record.get('cancelled_at', '')
    if cancelled_at:
        try:
            dt = datetime.fromisoformat(cancelled_at)
            cancelled_at_fmt = dt.strftime('%d/%m/%Y %H:%M:%S')
        except:
            cancelled_at_fmt = cancelled_at[:10]
    else:
        cancelled_at_fmt = None
    
    cancelled_by = record.get('cancelled_by', '')
    
    # Build details
    details = []
    details.append(html.Div([
        html.Strong(f"{entity_icon} {record.get('entity_name', 'N/A')}"),
        html.Br(),
        html.Small(f"ID: {record.get('entity_id', 'N/A')}", className='text-muted'),
    ]))
    
    if record.get('old_value') or record.get('new_value'):
        details.append(html.Div([
            html.Strong("Changements:"),
            html.Br(),
            html.Small(f"Avant: {record.get('old_value', 'N/A')}", className='text-muted'),
            html.Br(),
            html.Small(f"Après: {record.get('new_value', 'N/A')}", className='text-muted'),
        ], style={'marginTop': '8px'}))
    
    # Build footer
    footer_text = f"{icon} {action_type} par {record.get('performed_by', 'unknown')} le {created_at_fmt}"
    if cancelled_at_fmt:
        footer_text += f" | ❌ Annulée par {cancelled_by} le {cancelled_at_fmt}"
    
    # Button
    button = None
    if show_cancel_button and record.get('status') != 'cancelled':
        button = dbc.Button(
            [html.I(className="fas fa-ban", style={'marginRight': '6px'}), "Annuler"],
            id={'type': 'cancel-history', 'index': record.get('id', 0)},
            size='sm',
            color='danger',
            outline=True
        )
    
    return html.Div([
        html.Div([
            html.Div(details, style={'flex': '1'}),
            html.Div([
                button
            ] if button else [], style={'textAlign': 'right'}),
        ], style={
            'display': 'flex',
            'alignItems': 'flex-start',
            'justifyContent': 'space-between',
            'padding': '15px',
            'border': '1px solid #e0e0e0',
            'borderRadius': '8px',
            'marginBottom': '10px',
            'backgroundColor': '#f8f9fa' if record.get('status') != 'cancelled' else '#fff3cd',
        }),
        html.Div(footer_text, style={
            'fontSize': '12px',
            'color': '#666',
            'marginTop': '8px',
            'paddingLeft': '15px',
        }),
    ], style={'marginBottom': '15px'})
