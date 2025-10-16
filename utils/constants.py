"""Constantes utilisées dans l'application"""

# Types de relations
RELATION_TYPES = {
    0: "💋 Bisou",
    1: "� Dodo",
    2: "�️ Couché ensemble",
    3: "💑 Couple",
    4: "💔 Ex"
}

# Types d'actions pour l'historique
ACTION_TYPES = {
    'ADD': 'Ajout',
    'DELETE': 'Suppression',
    'UPDATE': 'Modification',
    'APPROVE': 'Approbation',
    'REJECT': 'Rejet',
    'UNDO': 'Annulation',
    'ADD_PERSON': 'Ajout personne',
    'UPDATE_PERSON': 'Modification personne',
    'DELETE_PERSON': 'Suppression personne',
    'MERGE_PERSON': 'Fusion personnes'
}

# Types d'actions annulables
UNDOABLE_ACTIONS = ['ADD', 'DELETE', 'APPROVE']

# Layout algorithms pour le graphe
LAYOUT_ALGORITHMS = {
    'community': '🎯 Community',
    'spring': '🌸 Spring',
    'kk': '🔷 Kamada-Kawai',
    'spectral': '⭐ Spectral'
}

# Couleurs pour les types de relations
RELATION_COLORS = {
    0: '#e11d48',  # Bisous - Rouge
    1: '#f97316',  # Plan cul - Orange
    2: '#ec4899',  # Relation sérieuse - Rose
    3: '#64748b',  # Ex - Gris
    4: '#f59e0b',  # Crush - Ambre
    5: '#0ea5e9'   # Ami(e) - Bleu
}
