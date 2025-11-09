"""
Admin Panel Component
Panel d'administration pour gérer les demandes en attente
"""

import dash_bootstrap_components as dbc
from dash import html
from typing import List, Dict


def create_admin_panel_tab():
    """Crée l'onglet Admin Panel"""
    return html.Div([
        html.Div("👑 Administration", className='section-title', style={'marginBottom': '20px'}),
        
        # Pending Accounts
        html.Div([
            html.H5("📋 Demandes de compte", style={'marginBottom': '15px'}),
            html.Div(id='pending-accounts-list', children=[
                html.P("Aucune demande en attente", className='text-muted')
            ]),
        ], style={'marginBottom': '30px'}),
        
        # Pending Persons
        html.Div([
            html.H5("👥 Personnes proposées", style={'marginBottom': '15px'}),
            html.Div(id='pending-persons-list', children=[
                html.P("Aucune proposition", className='text-muted')
            ]),
        ], style={'marginBottom': '30px'}),
        
        # Pending Relations
        html.Div([
            html.H5("🔗 Relations proposées", style={'marginBottom': '15px'}),
            html.Div(id='pending-relations-list', children=[
                html.P("Aucune proposition", className='text-muted')
            ]),
        ]),
        
        # Refresh button
        html.Div([
            dbc.Button([
                html.I(className="fas fa-sync", style={'marginRight': '8px'}),
                "Actualiser"
            ], id='btn-refresh-admin', color='secondary', className='w-100 mt-3'),
        ]),
    ])


def render_pending_account_item(account: Dict) -> html.Div:
    """Rend un item de demande de compte"""
    return html.Div([
        html.Div([
            html.Div([
                html.Strong(account['username']),
                html.Br(),
                html.Small(f"Demandé le: {str(account['submitted_at'])[:10]}", className='text-muted'),
            ], style={'flex': '1'}),
            html.Div([
                dbc.Button([
                    html.I(className="fas fa-check")
                ], id={'type': 'approve-account', 'index': account['id']}, 
                   color='success', size='sm', className='me-1'),
                dbc.Button([
                    html.I(className="fas fa-times")
                ], id={'type': 'reject-account', 'index': account['id']}, 
                   color='danger', size='sm'),
            ]),
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'padding': '10px',
            'border': '1px solid #e0e0e0',
            'borderRadius': '8px',
            'marginBottom': '10px',
            'backgroundColor': '#f8f9fa'
        }),
    ])


def render_pending_person_item(person: Dict) -> html.Div:
    """Rend un item de personne proposée"""
    return html.Div([
        html.Div([
            html.Div([
                html.Strong(person['name']),
                html.Br(),
                html.Small(f"Par: {person['submitted_by']} • {str(person['submitted_at'])[:10]}", 
                          className='text-muted'),
            ], style={'flex': '1'}),
            html.Div([
                dbc.Button([
                    html.I(className="fas fa-check")
                ], id={'type': 'approve-person', 'index': person['id']}, 
                   color='success', size='sm', className='me-1'),
                dbc.Button([
                    html.I(className="fas fa-times")
                ], id={'type': 'reject-person', 'index': person['id']}, 
                   color='danger', size='sm'),
            ]),
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'padding': '10px',
            'border': '1px solid #e0e0e0',
            'borderRadius': '8px',
            'marginBottom': '10px',
            'backgroundColor': '#f8f9fa'
        }),
    ])


def render_pending_relation_item(relation: Dict) -> html.Div:
    """Rend un item de relation proposée"""
    relation_types = {0: '💋 Bisou', 1: '😴 Dodo', 2: '🛏️ Couché', 3: '💑 Couple', 4: '💔 Ex'}
    rel_type = relation_types.get(relation['relation_type'], '❓')
    
    return html.Div([
        html.Div([
            html.Div([
                html.Strong(f"{relation['person1']} ↔ {relation['person2']}"),
                html.Br(),
                html.Span(rel_type, className='me-2'),
                html.Small(f"Par: {relation['submitted_by']} • {str(relation['submitted_at'])[:10]}", 
                          className='text-muted'),
            ], style={'flex': '1'}),
            html.Div([
                dbc.Button([
                    html.I(className="fas fa-check")
                ], id={'type': 'approve-relation', 'index': relation['id']}, 
                   color='success', size='sm', className='me-1'),
                dbc.Button([
                    html.I(className="fas fa-times")
                ], id={'type': 'reject-relation', 'index': relation['id']}, 
                   color='danger', size='sm'),
            ]),
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'padding': '10px',
            'border': '1px solid #e0e0e0',
            'borderRadius': '8px',
            'marginBottom': '10px',
            'backgroundColor': '#f8f9fa'
        }),
    ])


def render_pending_accounts_list(accounts: List[Dict]) -> html.Div:
    """Rend la liste complète des demandes de compte"""
    if not accounts:
        return html.P("Aucune demande en attente", className='text-muted')
    
    return html.Div([render_pending_account_item(acc) for acc in accounts])


def render_pending_persons_list(persons: List[Dict]) -> html.Div:
    """Rend la liste complète des personnes proposées"""
    if not persons:
        return html.P("Aucune proposition", className='text-muted')
    
    return html.Div([render_pending_person_item(p) for p in persons])


def render_pending_relations_list(relations: List[Dict]) -> html.Div:
    """Rend la liste complète des relations proposées"""
    if not relations:
        return html.P("Aucune proposition", className='text-muted')
    
    return html.Div([render_pending_relation_item(r) for r in relations])
