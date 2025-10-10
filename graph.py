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


def compute_layout(G: nx.Graph, seed: int = 42, spread: float = 2.0, min_separation: float = 0.03, mode: str = "community", center_node: Optional[str] = None) -> Dict[str, Tuple[float, float]]:
    """Calcule une disposition 2D lisible.

    mode: 'community' | 'spring' | 'kk' | 'spectral'
    center_node: optionnel, nom du nœud à placer au centre (0,0)
    """
    if mode == "spring":
        raw = _compute_spring(G, seed, spread)
    elif mode == "kk":
        raw = _compute_kk(G, seed)
    elif mode == "spectral":
        raw = _compute_spectral(G, seed)
    else:
        raw = _compute_community_layout(G, seed, spread)

    pos = {n: (float(x), float(y)) for n, (x, y) in raw.items()}
    
    # Si un nœud central est spécifié, translater pour le mettre à (0,0)
    if center_node and center_node in pos:
        cx, cy = pos[center_node]
        pos = {n: (x - cx, y - cy) for n, (x, y) in pos.items()}
    
    # Répulsion locale plus forte pour éviter les chevauchements
    pos = _enforce_min_separation(pos, min_dist=min_separation, steps=12, damping=0.75)
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


def make_figure(G: nx.DiGraph, pos: Dict[str, Tuple[float, float]]) -> go.Figure:
    # Degrés
    nodes = list(G.nodes())
    indeg = dict(G.in_degree())
    outdeg = dict(G.out_degree())
    deg_total = [indeg.get(n, 0) + outdeg.get(n, 0) for n in nodes]

    # Tailles et couleurs de nœuds selon degré total (un peu plus petites)
    sizes = scale(deg_total, out_min=18, out_max=45)
    colors = deg_total  # utilisé directement avec colorscale continue
    
    # Opacités selon le degré (plus connecté = plus opaque)
    opacities = scale(deg_total, out_min=0.4, out_max=1.0)

    # Tracé des nœuds
    x_nodes = [pos[n][0] for n in nodes]
    y_nodes = [pos[n][1] for n in nodes]
    hover_text = [
        f"{n}<br>degré total: {deg_total[i]}\n"
        f"entrants: {indeg.get(n, 0)} | sortants: {outdeg.get(n, 0)}"
        for i, n in enumerate(nodes)
    ]

    # Marqueurs pour tous les nœuds (labels au survol seulement)
    node_trace = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode="markers",
        hoverinfo="text",
        text=[str(n) for n in nodes],
        textposition="top center",
        textfont=dict(size=12),
        marker=dict(
            showscale=True,
            colorscale="Viridis",
            reversescale=False,
            color=colors,
            size=sizes,
            opacity=opacities,
            colorbar=dict(
                thickness=15,
                title="Degré total",
                xanchor="left",
                titleside="right",
                titlefont=dict(size=14),
                tickfont=dict(size=11),
            ),
            line=dict(width=1.5, color="#333"),
        ),
        hovertext=hover_text,
        name="Personnes",
    )

    # Afficher tous les noms avec fond blanc semi-transparent pour la lisibilité
    # Alterner les positions pour réduire les collisions de texte
    positions_cycle = ["top center", "bottom center", "middle right", "middle left"]
    label_x, label_y, label_text, label_pos = [], [], [], []
    for idx, n in enumerate(nodes):
        x, y = pos[n]
        label_x.append(x)
        label_y.append(y)
        label_text.append(str(n))
        # Alterner par ordre d'apparition pour répartir les positions
        label_pos.append(positions_cycle[idx % len(positions_cycle)])

    # Labels avec fond blanc pour contraste maximal
    label_trace = go.Scatter(
        x=label_x,
        y=label_y,
        mode="text",
        text=label_text,
        textposition=label_pos,
        textfont=dict(size=12, color="#000", family="Arial Black, Arial, sans-serif"),
        hoverinfo="skip",
        name="Labels",
        # Ajouter un padding virtuel via le mode marker invisible pour créer de l'espace
    )

    # Tracé des arêtes comme segments (pour la lisibilité), plus annotations pour les flèches
    edge_x: List[float] = []
    edge_y: List[float] = []
    annotations = []

    # Paramètres visuels - scalables avec le zoom
    base_arrow_color = "#444"
    base_edge_width = 1.5
    # Ces marges évitent que les segments/arrows touchent le centre des nœuds
    # Elles sont en coordonnées de layout (unités sans dimension). Ajustées empiriquement.
    cut_head = 0.08
    cut_tail = 0.08

    for src, dst in G.edges():
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        sx0, sy0, sx1, sy1 = shorten_segment(x0, y0, x1, y1, cut_head=cut_head, cut_tail=cut_tail)

        # Segment visuel
        edge_x += [sx0, sx1, None]
        edge_y += [sy0, sy1, None]

        # Annotation en flèche: tête = (sx1,sy1), queue proche (sx0,sy0)
        # Utiliser standoff pour mieux gérer la distance avec le marqueur
        annotations.append(
            dict(
                x=sx1,
                y=sy1,
                ax=sx0,
                ay=sy0,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=0,  # Pas de pointe de flèche, juste une ligne
                arrowwidth=1.5,
                arrowcolor=base_arrow_color,
                opacity=0.85,
                standoff=6,  # Distance en pixels depuis le nœud cible
            )
        )

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
