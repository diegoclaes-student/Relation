"""
Graph social interactif (NetworkX + Plotly)

Caractéristiques:
- Nœud = personne
- Arête orientée A -> B pour "A a pécho B"
- Taille et couleur des nœuds selon le degré total (entrants + sortants)
- Rendu interactif (zoom, déplacement/pan)
- Génère un fichier HTML autonome (graph.html) et ouvre une fenêtre

Exécution:
       fig.update_layout(
        title=dict(
            text="Graphe social (relations: 'a pécho')",
            x=0.5,
            xanchor="center",
            font=dict(size=20),
        ),
        showlegend=False,
        hovermode="closest",
        margin=dict(b=30, l=30, r=30, t=60),
        annotations=annotations,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )h.py --input relations.txt --output graph.html

Pré-requis:
    pip install -r requirements.txt
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Optional
import argparse

import networkx as nx
import plotly.graph_objects as go


# === DÉTECTION AUTOMATIQUE DU GENRE ===
def detect_gender(name: str) -> str:
    """
    Détecte automatiquement le genre d'un prénom (M/F/?)
    Basé sur les terminaisons et les prénoms français courants
    """
    name_lower = name.lower().strip()
    
    # Prénoms masculins courants (liste non exhaustive)
    male_names = {
        'diego', 'thomas', 'arthur', 'louis', 'lucas', 'paul', 'pierre', 'mathis',
        'jules', 'hugo', 'nathan', 'maxime', 'clement', 'antoine', 'nicolas', 'alex',
        'theo', 'tom', 'leo', 'adam', 'raphael', 'simon', 'gabriel', 'timeo', 'matheo',
        'ethan', 'nolan', 'baptiste', 'axel', 'enzo', 'yanis', 'noah', 'romain', 'quentin',
        'jeremy', 'kevin', 'florian', 'guillaume', 'benjamin', 'alexandre', 'anthony',
        'valentin', 'damien', 'julien', 'maxence', 'victor', 'pierre', 'charles', 'olivier'
    }
    
    # Prénoms féminins courants (liste non exhaustive)
    female_names = {
        'marie', 'lea', 'emma', 'lola', 'alice', 'chloe', 'sarah', 'julie', 'laura',
        'camille', 'manon', 'lisa', 'clara', 'lucie', 'oceane', 'charlotte', 'amelie',
        'morgane', 'pauline', 'marine', 'anaïs', 'juliette', 'clemence', 'elise', 'mathilde',
        'louise', 'jade', 'zoe', 'rose', 'lou', 'mila', 'nina', 'lina', 'anna', 'eva',
        'isaline', 'valentine', 'gabrielle', 'margaux', 'emilie', 'melissa', 'maeva',
        'celia', 'salome', 'romane', 'aurore', 'eloise', 'jeanne', 'adele', 'sophia'
    }
    
    # Vérifier d'abord dans les listes de prénoms connus
    base_name = name_lower.split()[0] if ' ' in name_lower else name_lower
    
    if base_name in male_names:
        return 'M'
    if base_name in female_names:
        return 'F'
    
    # Terminaisons typiquement féminines
    feminine_endings = ['a', 'e', 'ie', 'ine', 'elle', 'ette', 'ance', 'ence', 'otte', 'line']
    for ending in feminine_endings:
        if name_lower.endswith(ending) and len(name_lower) > 3:
            return 'F'
    
    # Terminaisons typiquement masculines
    masculine_endings = ['o', 'n', 'r', 'l', 'x', 's', 'c', 'k', 'go']
    for ending in masculine_endings:
        if name_lower.endswith(ending):
            return 'M'
    
    # Par défaut, inconnu
    return '?'


def analyze_gender_preference(node: str, G: nx.DiGraph, nodes: List[str]) -> Tuple[str, str]:
    """
    Analyse les préférences de genre d'une personne basées sur son historique.
    Retourne: (preference, description)
    - preference: 'M', 'F', 'BOTH', 'UNKNOWN'
    - description: texte descriptif
    
    IMPORTANT: Regarde TOUTES les relations (sortantes ET entrantes) pour avoir une vue complète
    """
    # Récupérer TOUTES les personnes liées (sortantes ET entrantes)
    outgoing_relations = set(G.successors(node))  # Personnes que node a pécho
    incoming_relations = set(G.predecessors(node))  # Personnes qui ont pécho node
    
    # Union des deux pour avoir toutes les relations
    all_relations = outgoing_relations.union(incoming_relations)
    
    if not all_relations:
        return 'UNKNOWN', 'Aucune relation'
    
    # Détecter le genre de chaque relation
    genders = [detect_gender(person) for person in all_relations]
    gender_counts = {
        'M': genders.count('M'),
        'F': genders.count('F'),
        '?': genders.count('?')
    }
    
    total_known = gender_counts['M'] + gender_counts['F']
    
    if total_known == 0:
        return 'UNKNOWN', 'Genres inconnus'
    
    # Déterminer la préférence stricte
    if gender_counts['M'] > 0 and gender_counts['F'] > 0:
        return 'BOTH', f"Mixte ({gender_counts['M']}H / {gender_counts['F']}F)"
    elif gender_counts['M'] > 0:
        return 'M', f"Que des hommes ({gender_counts['M']}H)"
    elif gender_counts['F'] > 0:
        return 'F', f"Que des femmes ({gender_counts['F']}F)"
    
    return 'UNKNOWN', 'Préférence inconnue'


def build_graph(relations: Dict[str, Iterable[str]] | Dict[str, List[Tuple[str, int]]]) -> nx.DiGraph:
    """Construit un graphe orienté à partir des relations.
    
    Supporte deux formats:
    - Ancien: {auteur: [cibles,...]}
    - Nouveau: {auteur: [(cible, type), ...]}
    
    Ajoute aussi les cibles en tant que nœuds si absentes en clef.
    Pour le nouveau format, stocke le type de relation comme attribut d'arête.
    """
    G = nx.DiGraph()

    # Ajouter toutes les arêtes (A -> B) et s'assurer que tous les nœuds existent
    for src, targets in relations.items():
        G.add_node(src)
        for item in targets:
            # Détecter le format
            if isinstance(item, tuple):
                # Nouveau format: (cible, type)
                dst, rel_type = item
                G.add_node(dst)
                if src != dst:
                    if not G.has_edge(src, dst):
                        G.add_edge(src, dst, relation_type=rel_type)
            else:
                # Ancien format: juste la cible
                dst = item
                G.add_node(dst)
                if src != dst:
                    if not G.has_edge(src, dst):
                        G.add_edge(src, dst, relation_type=0)  # Type par défaut: Bisous

    return G


def _enforce_min_separation(pos: Dict[str, Tuple[float, float]], min_dist: float = 0.04, steps: int = 8, damping: float = 0.5) -> Dict[str, Tuple[float, float]]:
    """Applique une répulsion locale pour garantir une distance minimale entre nœuds.

    min_dist: distance min en unités du layout
    steps: nombre d'itérations
    damping: facteur d'amortissement (0..1)
    """
    import math as _math
    nodes = list(pos.keys())
    for _ in range(max(1, steps)):
        moved = False
        for i in range(len(nodes)):
            xi, yi = pos[nodes[i]]
            shift_x = 0.0
            shift_y = 0.0
            for j in range(i + 1, len(nodes)):
                xj, yj = pos[nodes[j]]
                dx = xj - xi
                dy = yj - yi
                d2 = dx * dx + dy * dy
                if d2 <= 1e-12:
                    # même point: petit jitter aléatoire stable via hash
                    h = hash((nodes[i], nodes[j])) & 0xFFFF
                    rx = ((h % 257) - 128) / 128.0
                    ry = (((h // 257) % 257) - 128) / 128.0
                    dx = 1e-3 * rx
                    dy = 1e-3 * ry
                    d2 = dx * dx + dy * dy
                d = _math.sqrt(d2)
                if d < min_dist:
                    # vecteur de répulsion proportionnel à (min_dist - d)
                    ux, uy = dx / d, dy / d
                    push = (min_dist - d) * 0.5  # partager la poussée entre i et j
                    shift_x -= ux * push
                    shift_y -= uy * push
                    pos[nodes[j]] = (xj + ux * push * damping, yj + uy * push * damping)
                    moved = True
            if shift_x or shift_y:
                pos[nodes[i]] = (xi + shift_x * damping, yi + shift_y * damping)
        if not moved:
            break
    return pos


def _compute_spring(G: nx.Graph, seed: int, spread: float) -> Dict[str, Tuple[float, float]]:
    Gu = G.to_undirected()
    n = max(1, Gu.number_of_nodes())
    import math as _math
    k = spread / _math.sqrt(n)
    # Augmenter les itérations et ajuster les forces pour un meilleur espacement
    return nx.spring_layout(Gu, seed=seed, k=k, iterations=1200, scale=2.0)


def _compute_kk(G: nx.Graph, seed: int) -> Dict[str, Tuple[float, float]]:
    Gu = G.to_undirected()
    return nx.kamada_kawai_layout(Gu, weight=None, scale=1.0)


def _compute_spectral(G: nx.Graph, seed: int) -> Dict[str, Tuple[float, float]]:
    Gu = G.to_undirected()
    return nx.spectral_layout(Gu, scale=1.0)


def _compute_community_layout(G: nx.Graph, seed: int, spread: float) -> Dict[str, Tuple[float, float]]:
    """Place les communautés sur un grand cercle et dispose chaque communauté localement.

    Donne un résultat plus "logique" visuellement quand le graphe a plusieurs groupes.
    """
    from networkx.algorithms.community import greedy_modularity_communities
    import math as _math

    Gu = G.to_undirected()
    # Détecter les communautés
    comms = list(greedy_modularity_communities(Gu))
    if len(comms) <= 1:
        return _compute_spring(G, seed, spread)

    # Centres des communautés sur un cercle
    R = 3.5  # rayon du cercle global augmenté
    centers: List[Tuple[float, float]] = []
    for i in range(len(comms)):
        ang = 2 * _math.pi * i / len(comms)
        centers.append((R * _math.cos(ang), R * _math.sin(ang)))

    # Disposition interne par communauté
    pos: Dict[str, Tuple[float, float]] = {}
    for idx, nodes in enumerate(comms):
        sub = Gu.subgraph(nodes).copy()
        # layout interne avec plus d'itérations
        sub_pos = nx.spring_layout(sub, seed=seed + idx, k=spread / max(1, _math.sqrt(max(1, sub.number_of_nodes()))), iterations=800, scale=1.2)
        # centrer et normaliser
        xs = [sub_pos[n][0] for n in sub_pos]
        ys = [sub_pos[n][1] for n in sub_pos]
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        # échelle locale augmentée
        scale = 1.2  # rayon communautaire augmenté
        for n in sub_pos:
            x = (sub_pos[n][0] - cx) * scale + centers[idx][0]
            y = (sub_pos[n][1] - cy) * scale + centers[idx][1]
            pos[n] = (float(x), float(y))
    return pos


def compute_layout(G: nx.Graph, seed: int = 42, spread: float = 2.0, min_separation: float = 0.03, mode: str = "community", center_node: Optional[str] = None, repulsion: float = 1.0) -> Dict[str, Tuple[float, float]]:
    """Calcule une disposition 2D lisible.

    mode: 'community' | 'spring' | 'kk' | 'spectral'
    center_node: optionnel, nom du nœud à placer au centre (0,0)
    repulsion: facteur multiplicateur pour la force de répulsion (1.0 = normal)
    """
    # Ajuster min_separation avec le facteur repulsion
    adjusted_min_sep = min_separation * repulsion
    
    if mode == "spring":
        raw = _compute_spring(G, seed, spread * repulsion)
    elif mode == "kk":
        raw = _compute_kk(G, seed)
    elif mode == "spectral":
        raw = _compute_spectral(G, seed)
    else:
        raw = _compute_community_layout(G, seed, spread * repulsion)

    pos = {n: (float(x), float(y)) for n, (x, y) in raw.items()}
    
    # Si un nœud central est spécifié, translater pour le mettre à (0,0)
    if center_node and center_node in pos:
        cx, cy = pos[center_node]
        pos = {n: (x - cx, y - cy) for n, (x, y) in pos.items()}
    
    # Répulsion locale plus forte pour éviter les chevauchements
    pos = _enforce_min_separation(pos, min_dist=adjusted_min_sep, steps=12, damping=0.75)
    return pos


def scale(values: List[float], out_min: float, out_max: float) -> List[float]:
    if not values:
        return []
    vmin, vmax = min(values), max(values)
    if math.isclose(vmin, vmax):
        return [0.5 * (out_min + out_max) for _ in values]
    return [out_min + (v - vmin) * (out_max - out_min) / (vmax - vmin) for v in values]


def shorten_segment(x0: float, y0: float, x1: float, y1: float, cut_head: float, cut_tail: float) -> Tuple[float, float, float, float]:
    """Raccourcit un segment (x0,y0)->(x1,y1) pour ne pas entrer dans les marqueurs des nœuds.

    cut_head: raccourci côté tête (proche de x1,y1)
    cut_tail: raccourci côté queue (proche de x0,y0)
    """
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1e-6
    ux, uy = dx / L, dy / L
    sx0, sy0 = x0 + ux * cut_tail, y0 + uy * cut_tail
    sx1, sy1 = x1 - ux * cut_head, y1 - uy * cut_head
    return sx0, sy0, sx1, sy1


def make_figure(G: nx.DiGraph, pos: Dict[str, Tuple[float, float]], size_factor: float = 1.0, edge_width: float = 1.5) -> go.Figure:
    """Crée une figure Plotly style LinkedIn Maps avec communautés colorées distinctes.
    
    size_factor: multiplicateur pour les tailles de bulles (1.0 = normal, 2.0 = double)
    edge_width: épaisseur des liens
    """
    from networkx.algorithms.community import greedy_modularity_communities
    
    # Détecter les communautés
    Gu = G.to_undirected()
    communities = list(greedy_modularity_communities(Gu))
    
    # Assigner chaque nœud à sa communauté
    node_to_community = {}
    for idx, community in enumerate(communities):
        for node in community:
            node_to_community[node] = idx
    
    # Palette de couleurs PROFESSIONNELLE et ÉLÉGANTE (tons doux et saturés)
    color_palette = [
        '#5B8DEE',  # Bleu royal doux
        '#FF6B9D',  # Rose moderne
        '#20C997',  # Vert émeraude
        '#F59F00',  # Orange chaud
        '#AB7DF6',  # Violet élégant
        '#FF8C42',  # Corail chaleureux
        '#4ECDC4',  # Turquoise professionnel
        '#E74C3C',  # Rouge mat
        '#3498DB',  # Bleu ciel profond
        '#9B59B6',  # Violet profond
        '#1ABC9C',  # Turquoise mat
        '#F39C12',  # Jaune doré
    ]
    
    nodes = list(G.nodes())
    indeg = dict(G.in_degree())
    outdeg = dict(G.out_degree())
    deg_total = [indeg.get(n, 0) + outdeg.get(n, 0) for n in nodes]

    # Tailles de nœuds ajustables via size_factor
    base_min, base_max = 30, 80
    sizes = scale(deg_total, out_min=base_min * size_factor, out_max=base_max * size_factor)
    
    # Couleurs par communauté
    node_colors = [color_palette[node_to_community.get(n, 0) % len(color_palette)] for n in nodes]
    
    # === PRÉDICTION INTELLIGENTE DES PROCHAINES RELATIONS (avec détection de genre) ===
    def predict_next_connection(node):
        """
        Prédit la prochaine relation probable basée sur:
        1. Les préférences de genre (H/F/Mixte)
        2. Les connexions communes (amis d'amis)
        3. La communauté
        """
        # Analyser la préférence de genre de la personne
        gender_pref, gender_desc = analyze_gender_preference(node, G, nodes)
        
        # Récupérer TOUTES les relations (sortantes + entrantes)
        outgoing = set(G.successors(node))
        incoming = set(G.predecessors(node))
        all_neighbors = outgoing.union(incoming)
        
        # Fonction pour filtrer par genre selon la préférence STRICTE
        def matches_preference(candidate_name):
            """Vérifie si le candidat correspond STRICTEMENT à la préférence de genre"""
            candidate_gender = detect_gender(candidate_name)
            
            # Si genre inconnu du candidat, on le rejette pour être sûr
            if candidate_gender == '?':
                return False
            
            # Si pas de préférence établie, accepter tout le monde
            if gender_pref == 'UNKNOWN':
                return True
            
            # Si préférence mixte, accepter H et F
            if gender_pref == 'BOTH':
                return candidate_gender in ['M', 'F']
            
            # Sinon, matcher strictement avec la préférence
            return candidate_gender == gender_pref
        
        if not all_neighbors:
            # Si pas de connexions, suggérer quelqu'un de la même communauté avec le bon genre
            same_community = [n for n in nodes 
                            if node_to_community.get(n) == node_to_community.get(node) 
                            and n != node
                            and matches_preference(n)]
            if same_community:
                # Choisir celui avec le plus de connexions
                best = max(same_community, key=lambda n: deg_total[nodes.index(n)])
                gender_emoji = '👨' if detect_gender(best) == 'M' else '👩' if detect_gender(best) == 'F' else '👤'
                return best, f"Même communauté {gender_emoji}"
            return None, None
        
        # Calculer les amis d'amis (connexions à 2 degrés) AVEC FILTRE DE GENRE STRICT
        friends_of_friends = {}
        for neighbor in all_neighbors:
            # Regarder dans les deux directions (successeurs ET prédécesseurs)
            neighbor_connections = set(G.successors(neighbor)).union(set(G.predecessors(neighbor)))
            
            for friend in neighbor_connections:
                if friend != node and friend not in all_neighbors:
                    # VÉRIFICATION STRICTE DU GENRE
                    if matches_preference(friend):
                        # Compter les connexions communes
                        if friend not in friends_of_friends:
                            friends_of_friends[friend] = {'common': 0, 'via': []}
                        friends_of_friends[friend]['common'] += 1
                        friends_of_friends[friend]['via'].append(neighbor)
        
        if friends_of_friends:
            # Trouver le candidat avec le plus de connexions communes
            best_candidate = max(friends_of_friends.items(), key=lambda x: x[1]['common'])
            candidate_name = best_candidate[0]
            common_count = best_candidate[1]['common']
            via_person = best_candidate[1]['via'][0]
            
            # Emoji selon le genre
            candidate_gender = detect_gender(candidate_name)
            gender_emoji = '👨' if candidate_gender == 'M' else '👩' if candidate_gender == 'F' else '�'
            
            # Vérification de debug (ne devrait jamais arriver)
            if gender_pref not in ['BOTH', 'UNKNOWN'] and candidate_gender != gender_pref:
                print(f"⚠️ WARNING: Prédiction incorrecte pour {node} (pref:{gender_pref}, candidat:{candidate_name}={candidate_gender})")
            
            return candidate_name, f"Via {via_person} ({common_count} ami{'s' if common_count > 1 else ''} commun{'s' if common_count > 1 else ''}) {gender_emoji}"
        
        # Si pas d'amis d'amis, suggérer quelqu'un de la même communauté avec le bon genre
        same_community = [n for n in nodes 
                         if node_to_community.get(n) == node_to_community.get(node) 
                         and n != node 
                         and n not in all_neighbors
                         and matches_preference(n)]
        if same_community:
            best = max(same_community, key=lambda n: deg_total[nodes.index(n)])
            gender_emoji = '👨' if detect_gender(best) == 'M' else '👩' if detect_gender(best) == 'F' else '👤'
            return best, f"Même communauté {gender_emoji}"
        
        return None, None
    
    # Tracé des nœuds avec informations enrichies
    x_nodes = [pos[n][0] for n in nodes]
    y_nodes = [pos[n][1] for n in nodes]
    
    # Générer les hover texts enrichis avec analyse de genre
    hover_text = []
    for i, n in enumerate(nodes):
        # Récupérer les personnes connectées (relations sortantes = "a pécho")
        outgoing_relations = list(G.successors(n))
        neighbors_str = ", ".join(outgoing_relations[:5])  # Limiter à 5 pour la lisibilité
        if len(outgoing_relations) > 5:
            neighbors_str += f" ... (+{len(outgoing_relations)-5} autres)"
        
        # Analyser la préférence de genre
        gender_pref, gender_desc = analyze_gender_preference(n, G, nodes)
        
        # Emoji selon la préférence
        pref_emoji = {
            'M': '👨 (Préfère les hommes)',
            'F': '👩 (Préfère les femmes)',
            'BOTH': '👥 (Préfère H/F)',
            'UNKNOWN': '❓ (Préférence inconnue)'
        }.get(gender_pref, '❓')
        
        # Déterminer le genre de la personne elle-même
        own_gender = detect_gender(n)
        own_gender_emoji = '👨' if own_gender == 'M' else '👩' if own_gender == 'F' else '👤'
        
        # Prédiction de la prochaine relation
        next_person, reason = predict_next_connection(n)
        prediction_str = f"<b style='color:#4ECDC4'>→ {next_person}</b><br><span style='color:#999; font-size:11px'>{reason}</span>" if next_person else "<span style='color:#999'>Aucune suggestion</span>"
        
        # Construire le hover text complet
        hover = (
            f"<b style='font-size:16px; color:#667eea'>{own_gender_emoji} {n}</b><br>"
            f"<span style='color:#999'>──────────────</span><br>"
            f"<b>👥 Relations ({len(outgoing_relations)}):</b><br>"
            f"<span style='font-size:11px'>{neighbors_str if outgoing_relations else 'Aucune'}</span><br><br>"
            f"<b>💘 Préférence:</b> {pref_emoji}<br>"
            f"<span style='font-size:11px; color:#999'>{gender_desc}</span><br><br>"
            f"<b>📊 Total:</b> {deg_total[i]} connexion{'s' if deg_total[i] > 1 else ''}<br>"
            f"<span style='font-size:11px'>↓ {indeg.get(n, 0)} entrant{'s' if indeg.get(n, 0) > 1 else ''} | "
            f"↑ {outdeg.get(n, 0)} sortant{'s' if outdeg.get(n, 0) > 1 else ''}</span><br><br>"
            f"<b>🔮 Prochaine relation prédite:</b><br>"
            f"{prediction_str}"
        )
        hover_text.append(hover)
    
    # Seuil pour afficher les labels : seulement les gros nœuds (degré > médiane)
    median_deg = sorted(deg_total)[len(deg_total) // 2] if deg_total else 0
    
    # Labels conditionnels : afficher seulement pour les nœuds importants
    node_text = [str(n) if deg_total[i] > median_deg else "" for i, n in enumerate(nodes)]

    # Nœuds avec Scatter standard pour compatibilité maximale
    node_trace = go.Scatter(  # Scatter classique - pas de WebGL
        x=x_nodes,
        y=y_nodes,
        mode="markers+text",
        text=node_text,  # Labels conditionnels
        textposition="middle center",
        textfont=dict(
            size=12,
            color="#1a1a1a",  # Noir foncé pour contraste sur fond clair
            family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif",
        ),
        marker=dict(
            color=node_colors,
            size=sizes,
            opacity=0.88,  # Transparence élégante (88%)
            line=dict(width=2, color="rgba(255, 255, 255, 0.7)"),  # Contour réduit pour performance
        ),
        hovertext=hover_text,
        hoverinfo="text",
        hoverlabel=dict(
            bgcolor="rgba(30, 30, 40, 0.98)",  # Tooltip sombre élégant
            font=dict(size=12, color="white", family="Arial"),
            bordercolor="rgba(102, 126, 234, 0.8)",
            align="left",
        ),
        name="Personnes",
    )

    # Tracé des arêtes - VERSION INTELLIGENTE avec évitement des bulles
    # Créer des traces individuelles avec courbes optimisées
    edge_traces = []
    
    # Palette de couleurs variées pour différencier les liens
    edge_colors = [
        'rgba(102, 126, 234, 0.3)',   # Bleu violet
        'rgba(237, 100, 166, 0.3)',   # Rose
        'rgba(255, 159, 64, 0.3)',    # Orange
        'rgba(75, 192, 192, 0.3)',    # Turquoise
        'rgba(153, 102, 255, 0.3)',   # Violet
        'rgba(255, 99, 132, 0.3)',    # Rouge rose
        'rgba(54, 162, 235, 0.3)',    # Bleu ciel
        'rgba(255, 206, 86, 0.3)',    # Jaune
    ]
    
    # Fonction pour vérifier si un point est proche d'un nœud
    def is_near_node(x, y, exclude_nodes=None):
        """Vérifie si le point (x,y) est trop proche d'un nœud (sauf ceux exclus)"""
        min_distance = 0.08  # Distance minimale pour éviter les bulles
        for node in nodes:
            if exclude_nodes and node in exclude_nodes:
                continue
            nx_pos, ny_pos = pos[node]
            dist = ((x - nx_pos)**2 + (y - ny_pos)**2) ** 0.5
            if dist < min_distance:
                return True, dist
        return False, float('inf')
    
    # Note: edge_width est maintenant un paramètre de la fonction
    
    # Créer les arêtes COURBÉES avec évitement intelligent des bulles
    for idx, (src, dst) in enumerate(G.edges()):
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        
        # Calculer les paramètres de base
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = x1 - x0, y1 - y0
        length = (dx**2 + dy**2) ** 0.5
        
        if length > 0:
            # Perpendiculaire (rotation 90°)
            px, py = -dy / length, dx / length
            
            # ÉVITEMENT INTELLIGENT : tester plusieurs offsets pour éviter les bulles
            base_offset = length * 0.15
            direction = 1 if idx % 2 == 0 else -1
            
            # Tester le point de contrôle par défaut
            cx_candidate = mx + px * base_offset * direction
            cy_candidate = my + py * base_offset * direction
            
            # Vérifier s'il est proche d'une bulle (exclure source et destination)
            near_node, distance = is_near_node(cx_candidate, cy_candidate, exclude_nodes={src, dst})
            
            if near_node:
                # Augmenter la courbure pour éviter la bulle
                base_offset = length * 0.28  # Courbure plus prononcée
                # Essayer de l'autre côté si nécessaire
                cx_candidate = mx + px * base_offset * direction
                cy_candidate = my + py * base_offset * direction
                
                # Si encore trop proche, inverser la direction
                still_near, _ = is_near_node(cx_candidate, cy_candidate, exclude_nodes={src, dst})
                if still_near:
                    direction *= -1
                    cx_candidate = mx + px * base_offset * direction
                    cy_candidate = my + py * base_offset * direction
            
            cx, cy = cx_candidate, cy_candidate
        else:
            cx, cy = mx, my
        
        # Courbe avec 9 points (bon compromis beauté/performance)
        edge_x, edge_y = [], []
        t_values = [i/8 for i in range(9)]
        for t in t_values:
            curve_x = (1-t)**2 * x0 + 2*(1-t)*t * cx + t**2 * x1
            curve_y = (1-t)**2 * y0 + 2*(1-t)*t * cy + t**2 * y1
            edge_x.append(curve_x)
            edge_y.append(curve_y)
        
        # Choisir une couleur de la palette
        color = edge_colors[idx % len(edge_colors)]
        
        # Créer une trace pour cet edge
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(
                width=edge_width * 0.8,
                color=color,
            ),
            hoverinfo='text',
            hovertext=f"{src} → {dst}",
            showlegend=False,
            opacity=0.7,
        )
        edge_traces.append(edge_trace)

    # DÉSACTIVER les ombres pour performance
    # shadow_trace supprimé

    # Créer la figure avec TOUTES les traces d'edges + nodes
    fig = go.Figure(data=edge_traces + [node_trace])
    
    # Layout épuré et moderne avec optimisations de performance
    fig.update_layout(
        showlegend=False,
        hovermode="closest",
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            visible=False,
            fixedrange=False,
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            visible=False,
            fixedrange=False,
        ),
        plot_bgcolor="#F8F9FA",
        paper_bgcolor="#F8F9FA",
        # Optimisations MAXIMALES pour fluidité
        dragmode='pan',
        transition={'duration': 0},
        # Désactiver le rendu lors du drag
        modebar={'bgcolor': 'rgba(0,0,0,0)'},
    )
    
    # Configuration WebGL pour accélération matérielle
    fig.update_traces(
        # Désactiver le hover pendant le drag pour plus de fluidité
        hovertemplate=None
    )

    return fig

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color=base_arrow_color),
        hoverinfo="none",
        mode="lines",
        name="Relations",
        opacity=0.75,
    )

    fig = go.Figure(data=[edge_trace, node_trace, label_trace])
    fig.update_layout(
        title=dict(
            text="Graphe social (relations: ‘a pécho’)",
            x=0.5,
            xanchor="center",
        ),
        showlegend=False,
        hovermode="closest",
        margin=dict(b=20, l=20, r=20, t=50),
        annotations=annotations,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )

    # Rendre le graphe plus grand pour le confort et la clarté
    # Résolution adaptée à l'écran pour navigation interactive
    fig.update_layout(width=1400, height=1000)
    return fig


def default_relations() -> Dict[str, List[str]]:
    """Relations de l'énoncé."""
    return {
        "A": ["B", "C", "D"],
        "B": ["A", "X", "Y"],
        "C": ["D"],
        "D": ["B"],
        "X": ["A"],
        "Y": ["C"],
    }


def parse_relations_csv(path: Path) -> Tuple[Dict[str, List[Tuple[str, int]]], Dict[int, str]]:
    """Parse un fichier CSV avec types de relations: Person1;Person2;Type
    
    Returns:
        - relations: Dict[personne] -> [(cible, type), ...]
        - relation_types: Dict[type_id] -> label
    """
    # Définir les types de relations
    relation_types = {
        0: "Bisous",
        1: "Dodo ensemble",
        2: "Baise",
        3: "Couple"
    }
    
    relations: Dict[str, List[Tuple[str, int]]] = {}
    
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            
            parts = line.split(";")
            if len(parts) < 3:
                continue
            
            person1 = parts[0].strip()
            person2 = parts[1].strip()
            try:
                rel_type = int(parts[2].strip())
            except ValueError:
                rel_type = 0  # Défaut: Bisous
            
            # Ignorer auto-boucles
            if person1 == person2:
                continue
            
            # Ajouter la relation
            if person1 not in relations:
                relations[person1] = []
            
            # Éviter doublons
            if not any(t[0] == person2 and t[1] == rel_type for t in relations[person1]):
                relations[person1].append((person2, rel_type))
    
    return relations, relation_types


def parse_relations_txt(path: Path) -> Dict[str, List[str]]:
    """Parcours un fichier .txt de la forme: `A: B, C, D` par ligne.

    Règles:
    - Ignore lignes vides et celles qui commencent par '#'
    - Trim des espaces
    - Dédoublonnage des cibles par source
    - Ignore les auto-boucles (A: A)
    """
    relations: Dict[str, List[str]] = {}
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                # Ligne invalide: on ignore en silence pour robustesse
                continue
            left, right = line.split(":", 1)
            src = left.strip()
            targets = [t.strip() for t in right.split(",") if t.strip()]
            if not src:
                continue
            # Dédoublonnage en conservant l'ordre d'apparition
            seen = set()
            dedup = []
            for t in targets:
                if t == src:
                    continue
                if t not in seen:
                    seen.add(t)
                    dedup.append(t)
            if src in relations:
                # fusionner avec celles existantes (en dédoublonnant)
                for t in dedup:
                    if t not in relations[src]:
                        relations[src].append(t)
            else:
                relations[src] = dedup
    return relations


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Graphe social interactif (A: B, C, D)")
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Chemin du fichier .txt (format: A: B, C, D par ligne)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="graph.html",
        help="Nom du fichier HTML de sortie (par défaut: graph.html)",
    )
    parser.add_argument(
        "--layout",
        type=str,
        default="community",
        choices=["community", "spring", "kk", "spectral"],
        help="Algorithme de layout (par défaut: community)",
    )
    parser.add_argument(
        "--spread",
        type=float,
        default=5.0,
        help="Facteur d'espacement global pour spring/community",
    )
    parser.add_argument(
        "--min-separation",
        type=float,
        default=0.08,
        help="Distance minimale entre nœuds en unités du layout",
    )
    parser.add_argument(
        "--center",
        type=str,
        default=None,
        help="Nom du nœud à placer au centre du graphe (ex: Rachel)",
    )
    args = parser.parse_args(argv)

    # Priorité: --input; sinon relations.txt s'il existe; sinon valeurs par défaut
    input_path: Optional[Path] = None
    if args.input:
        input_path = Path(args.input)
    else:
        guess = Path(__file__).with_name("relations.txt")
        if guess.exists():
            input_path = guess

    if input_path and input_path.exists():
        relations = parse_relations_txt(input_path)
        if not relations:
            print(f"Aucune relation valide trouvée dans {input_path}. Utilisation des relations par défaut.")
            relations = default_relations()
    else:
        if input_path:
            print(f"Fichier introuvable: {input_path}. Utilisation des relations par défaut.")
        relations = default_relations()

    G = build_graph(relations)
    pos = compute_layout(G, seed=42, spread=args.spread, min_separation=args.min_separation, mode=args.layout, center_node=args.center)
    fig = make_figure(G, pos)

    out_path = Path(args.output).resolve()
    # Écrire un HTML léger (Plotly via CDN) pour réduire la taille du fichier
    # Si l'espace disque est insuffisant, afficher directement dans le navigateur
    try:
        fig.write_html(out_path, include_plotlyjs="cdn", full_html=True)
        print(f"Fichier généré: {out_path}")
    except OSError as e:
        # Espace disque insuffisant: afficher dans le navigateur sans sauvegarder
        if getattr(e, 'errno', None) == 28:  # No space left on device
            print(f"⚠️  DISQUE PLEIN! Impossible d'écrire {out_path}")
            print(f"   Espace libre: vérifiez avec 'df -h'")
            print(f"   Le graphe sera affiché dans le navigateur uniquement.")
            print(f"\n💡 Pour libérer de l'espace:")
            print(f"   - Vider la corbeille")
            print(f"   - Supprimer les fichiers de cache: ~/Library/Caches/")
            print(f"   - Désinstaller des applications inutilisées")
        else:
            raise
    try:
        fig.show()
        print("\n📊 Graphe affiché dans le navigateur.")
        print("   Pour exporter en PNG: cliquez sur l'icône 📷 dans le graphe.")
    except Exception:
        # En environnement sans affichage, l'HTML reste disponible
        pass


if __name__ == "__main__":
    main()
