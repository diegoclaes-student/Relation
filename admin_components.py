"""Composants et callbacks pour le panel administrateur"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from database import RELATION_TYPES

def create_admin_dashboard(db):
    """Crée le tableau de bord admin complet"""
    pending = db.get_pending_relations()
    all_relations = db.get_all_relations()
    persons = db.get_all_persons()
    persons_detailed = db.get_all_persons_detailed()
    history = db.get_history(50)
    
    return html.Div([
        html.H3("🎯 Admin Dashboard"),
        
        # Tabs pour différentes sections
        dbc.Tabs([
            # Tab 1: Pending Relations
            dbc.Tab(
                create_pending_tab(pending),
                label=f"📬 Propositions ({len(pending)})",
                tab_id="tab-pending"
            ),
            
            # Tab 2: Manage Relations
            dbc.Tab(
                create_manage_tab(all_relations, persons),
                label=f"📝 Gérer Relations ({len(all_relations)})",
                tab_id="tab-manage"
            ),
            
            # Tab 3: Manage Persons
            dbc.Tab(
                create_persons_tab(persons_detailed),
                label=f"👥 Gérer Personnes ({len(persons_detailed)})",
                tab_id="tab-persons"
            ),
            
            # Tab 4: Add New
            dbc.Tab(
                create_add_tab(persons),
                label="➕ Ajouter",
                tab_id="tab-add"
            ),
            
            # Tab 5: History
            dbc.Tab(
                create_history_tab(history),
                label="📜 Historique",
                tab_id="tab-history"
            ),
        ], id="admin-tabs", active_tab="tab-pending"),
        
        html.Div(id='admin-action-result', style={'marginTop': '20px'})
    ])

def create_pending_tab(pending):
    """Tab moderne pour approuver/rejeter les propositions"""
    if not pending:
        return html.Div([
            html.Div([
                html.I(className="fas fa-inbox", style={'fontSize': '48px', 'color': '#cbd5e1', 'marginBottom': '15px'}),
                html.P("Aucune proposition en attente", style={'color': '#94a3b8', 'fontSize': '16px', 'fontWeight': '500'})
            ], style={'textAlign': 'center', 'padding': '60px'})
        ])
    
    items = []
    for rel in pending:
        items.append(
            html.Div([
                html.Div([
                    html.Div([
                        html.Span(f"{rel['person1']}", style={'fontWeight': '700', 'color': '#1e293b'}),
                        html.I(className="fas fa-arrow-right", style={'margin': '0 10px', 'color': '#94a3b8', 'fontSize': '12px'}),
                        html.Span(f"{rel['person2']}", style={'fontWeight': '700', 'color': '#1e293b'}),
                    ], style={'marginBottom': '8px'}),
                    html.Div([
                        html.Span([
                            html.I(className="fas fa-tag", style={'marginRight': '5px', 'fontSize': '11px'}),
                            f"{RELATION_TYPES.get(rel['relation_type'], 'Inconnu')}"
                        ], style={
                            'background': '#dbeafe',
                            'color': '#1e40af',
                            'padding': '3px 10px',
                            'borderRadius': '12px',
                            'fontSize': '12px',
                            'fontWeight': '600',
                            'marginRight': '8px'
                        }),
                        html.Span([
                            html.I(className="fas fa-user", style={'marginRight': '5px', 'fontSize': '11px'}),
                            f"{rel['submitted_by']}"
                        ], style={
                            'background': '#f3f4f6',
                            'color': '#6b7280',
                            'padding': '3px 10px',
                            'borderRadius': '12px',
                            'fontSize': '11px',
                            'marginRight': '8px'
                        }),
                        html.Span([
                            html.I(className="fas fa-clock", style={'marginRight': '5px', 'fontSize': '11px'}),
                            f"{rel['submitted_at']}"
                        ], style={
                            'color': '#9ca3af',
                            'fontSize': '11px'
                        })
                    ]),
                    html.Div(rel['notes'], style={'fontSize': '12px', 'color': '#64748b', 'fontStyle': 'italic', 'marginTop': '6px'}) if rel['notes'] else None
                ], style={'flex': '1'}),
                
                html.Div([
                    html.Button([
                        html.I(className="fas fa-check", style={'marginRight': '6px'}),
                        "Approuver"
                    ],
                        id={'type': 'btn-approve', 'index': rel['id']},
                        style={
                            'background': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '8px',
                            'padding': '8px 14px',
                            'fontSize': '13px',
                            'fontWeight': '600',
                            'cursor': 'pointer',
                            'marginRight': '6px',
                            'boxShadow': '0 2px 8px rgba(16, 185, 129, 0.3)'
                        }
                    ),
                    html.Button([
                        html.I(className="fas fa-times", style={'marginRight': '6px'}),
                        "Rejeter"
                    ],
                        id={'type': 'btn-reject', 'index': rel['id']},
                        style={
                            'background': '#ef4444',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '8px',
                            'padding': '8px 14px',
                            'fontSize': '13px',
                            'fontWeight': '600',
                            'cursor': 'pointer',
                            'boxShadow': '0 2px 8px rgba(239, 68, 68, 0.3)'
                        }
                    )
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'background': 'white',
                'borderRadius': '12px',
                'padding': '16px 18px',
                'marginBottom': '10px',
                'border': '1px solid #e2e8f0',
                'boxShadow': '0 1px 3px rgba(0, 0, 0, 0.08)'
            })
        )
    
    return html.Div(items, style={'maxHeight': '400px', 'overflowY': 'auto', 'paddingRight': '5px'})

def create_manage_tab(all_relations, persons):
    """Tab pour gérer les relations existantes"""
    # Grouper par personne
    relations_by_person = {}
    for p1, p2, rel_type in all_relations:
        if p1 not in relations_by_person:
            relations_by_person[p1] = []
        relations_by_person[p1].append((p2, rel_type))
    
    items = []
    for person in sorted(relations_by_person.keys())[:20]:  # Limiter à 20 pour performance
        rels = relations_by_person[person]
        items.append(
            html.Div([
                html.Strong(f"{person} ({len(rels)} relations)"),
                html.Div([
                    html.Div([
                        html.Span(f"→ {target} ", style={'marginRight': '10px'}),
                        html.Small(f"({RELATION_TYPES.get(rel_type, '?')})", style={'color': '#666'}),
                        html.Button(
                            "🗑️",
                            id={'type': 'btn-delete', 'index': f"{person}|{target}|{rel_type}"},
                            className='btn-sm',
                            style={
                                'background': '#dc3545',
                                'color': 'white',
                                'marginLeft': '10px',
                                'padding': '2px 6px',
                                'fontSize': '10px'
                            }
                        )
                    ], style={'padding': '5px 0'})
                    for target, rel_type in rels[:5]  # Limiter à 5 relations affichées
                ])
            ], className='relation-item', style={'marginBottom': '10px'})
        )
    
    return html.Div([
        html.P(f"Affichage des 20 premières personnes sur {len(relations_by_person)}", 
               style={'fontSize': '12px', 'color': '#666', 'marginBottom': '10px'}),
        html.Div(items, style={'maxHeight': '400px', 'overflowY': 'auto'})
    ])

def create_persons_tab(persons_detailed):
    """Tab pour gérer les personnes (renommer, genre, orientation, fusionner)"""
    if not persons_detailed:
        return html.Div([
            html.Div([
                html.I(className="fas fa-users", style={'fontSize': '48px', 'color': '#ccc', 'marginBottom': '15px'}),
                html.P("Aucune personne", style={'color': '#999', 'fontSize': '16px'})
            ], style={'textAlign': 'center', 'padding': '60px'})
        ])
    
    items = []
    for person in persons_detailed[:30]:  # Limiter à 30 pour performance
        name = person['name']
        gender = person['gender'] or '?'
        orientation = person['sexual_orientation'] or '?'
        
        # Icône et couleur selon le genre
        if gender == 'M':
            gender_icon = 'fas fa-mars'
            gender_color = '#3b82f6'
        elif gender == 'F':
            gender_icon = 'fas fa-venus'
            gender_color = '#ec4899'
        else:
            gender_icon = 'fas fa-question'
            gender_color = '#94a3b8'
        
        items.append(
            html.Div([
                # Partie gauche : Info personne
                html.Div([
                    html.Div([
                        html.I(className=gender_icon, style={
                            'fontSize': '24px',
                            'color': gender_color,
                            'marginRight': '12px'
                        }),
                        html.Div([
                            html.Div(name, style={
                                'fontSize': '16px',
                                'fontWeight': '600',
                                'color': '#1e293b',
                                'marginBottom': '4px'
                            }),
                            html.Div([
                                html.Span([
                                    html.I(className="fas fa-user-tag", style={'marginRight': '4px', 'fontSize': '11px'}),
                                    gender
                                ], style={
                                    'background': f'{gender_color}15',
                                    'color': gender_color,
                                    'padding': '2px 8px',
                                    'borderRadius': '12px',
                                    'fontSize': '11px',
                                    'fontWeight': '600',
                                    'marginRight': '6px'
                                }),
                                html.Span([
                                    html.I(className="fas fa-heart", style={'marginRight': '4px', 'fontSize': '11px'}),
                                    orientation
                                ], style={
                                    'background': '#f1f5f9',
                                    'color': '#64748b',
                                    'padding': '2px 8px',
                                    'borderRadius': '12px',
                                    'fontSize': '11px',
                                    'fontWeight': '600'
                                })
                            ])
                        ])
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1'}),
                
                # Partie droite : Actions
                html.Div([
                    html.Button([
                        html.I(className="fas fa-edit", style={'marginRight': '6px'}),
                        "Modifier"
                    ],
                        id={'type': 'btn-edit-person', 'index': name},
                        style={
                            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '8px',
                            'padding': '8px 14px',
                            'fontSize': '13px',
                            'fontWeight': '600',
                            'cursor': 'pointer',
                            'marginRight': '6px',
                            'boxShadow': '0 2px 8px rgba(102, 126, 234, 0.3)',
                            'transition': 'all 0.2s'
                        }
                    ),
                    html.Button([
                        html.I(className="fas fa-code-branch", style={'marginRight': '6px'}),
                        "Fusionner"
                    ],
                        id={'type': 'btn-merge-person', 'index': name},
                        style={
                            'background': 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '8px',
                            'padding': '8px 14px',
                            'fontSize': '13px',
                            'fontWeight': '600',
                            'cursor': 'pointer',
                            'marginRight': '6px',
                            'boxShadow': '0 2px 8px rgba(245, 158, 11, 0.3)',
                            'transition': 'all 0.2s'
                        }
                    ),
                    html.Button(
                        html.I(className="fas fa-trash-alt"),
                        id={'type': 'btn-delete-person', 'index': name},
                        style={
                            'background': '#ef4444',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '8px',
                            'padding': '8px 12px',
                            'fontSize': '13px',
                            'cursor': 'pointer',
                            'boxShadow': '0 2px 8px rgba(239, 68, 68, 0.3)',
                            'transition': 'all 0.2s'
                        }
                    )
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'background': 'white',
                'borderRadius': '12px',
                'padding': '16px 18px',
                'marginBottom': '10px',
                'border': '1px solid #e2e8f0',
                'boxShadow': '0 1px 3px rgba(0, 0, 0, 0.08)',
                'transition': 'all 0.2s',
                ':hover': {
                    'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.12)',
                    'transform': 'translateY(-2px)'
                }
            })
        )
    
    return html.Div([
        html.Div([
            html.I(className="fas fa-info-circle", style={'marginRight': '8px', 'color': '#667eea'}),
            html.Span(f"Affichage de {min(30, len(persons_detailed))} personnes sur {len(persons_detailed)}", 
                style={'fontSize': '13px', 'color': '#64748b', 'fontWeight': '500'})
        ], style={'marginBottom': '15px', 'padding': '10px', 'background': '#f8fafc', 'borderRadius': '8px'}),
        html.Div(items, style={'maxHeight': '400px', 'overflowY': 'auto', 'paddingRight': '5px'})
    ])

def create_add_tab(persons):
    """Tab pour ajouter directement une relation"""
    return html.Div([
        html.Div([
            html.Label("Personne 1", className='control-label'),
            dcc.Dropdown(
                id='admin-add-person1',
                options=[{'label': p, 'value': p} for p in sorted(persons)],
                placeholder="Sélectionner...",
                style={'marginBottom': '15px'}
            ),
            
            html.Label("Personne 2", className='control-label'),
            dcc.Dropdown(
                id='admin-add-person2',
                options=[{'label': p, 'value': p} for p in sorted(persons)],
                placeholder="Sélectionner...",
                style={'marginBottom': '15px'}
            ),
            
            html.Label("Type de relation", className='control-label'),
            dcc.Dropdown(
                id='admin-add-type',
                options=[{'label': v, 'value': k} for k, v in RELATION_TYPES.items()],
                value=0,
                clearable=False,
                style={'marginBottom': '15px'}
            ),
            
            html.Div([
                dcc.Checklist(
                    id='admin-add-symmetrize',
                    options=[{'label': ' Créer aussi la relation inverse (symétrie)', 'value': 'sym'}],
                    value=['sym'],
                    style={'marginBottom': '15px'}
                )
            ]),
            
            html.Button(
                "➕ Ajouter la relation",
                id='btn-admin-add-relation',
                className='btn-custom btn-success-custom'
            )
        ])
    ])

def create_history_tab(history):
    """Tab pour afficher l'historique des actions"""
    if not history:
        return html.Div([
            html.P("📝 Aucun historique", style={'textAlign': 'center', 'padding': '40px', 'color': '#999'})
        ])
    
    items = []
    for action in history[:30]:  # Limiter à 30 dernières actions
        icon_map = {
            'ADD': '➕',
            'DELETE': '🗑️',
            'APPROVE': '✅',
            'REJECT': '❌',
            'UPDATE': '✏️'
        }
        icon = icon_map.get(action['action_type'], '📝')
        
        items.append(
            html.Div([
                html.Div([
                    html.Span(icon, style={'marginRight': '8px'}),
                    html.Strong(action['action_type']),
                    html.Br(),
                    html.Small([
                        f"{action['person1'] or '?'} → {action['person2'] or '?'}",
                        f" | Type: {RELATION_TYPES.get(action['relation_type'], '?') if action['relation_type'] is not None else '?'}",
                        html.Br(),
                        f"Par: {action['performed_by']} | {action['created_at']}"
                    ], style={'color': '#666'}),
                    html.Br(),
                    html.Small(action['details'], style={'color': '#888', 'fontStyle': 'italic'}) if action['details'] else None
                ])
            ], style={
                'background': '#f8f9fa',
                'borderRadius': '8px',
                'padding': '10px',
                'marginBottom': '8px',
                'borderLeft': '3px solid #667eea'
            })
        )
    
    return html.Div(items, style={'maxHeight': '400px', 'overflowY': 'auto'})
