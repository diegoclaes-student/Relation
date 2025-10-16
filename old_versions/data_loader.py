"""
Module pour charger les données de relations avec support multi-format.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import networkx as nx
from graph import parse_relations_txt, parse_relations_csv, build_graph


# Types de relations globaux
RELATION_TYPES = {
    0: "Bisous",
    1: "Dodo ensemble",
    2: "Baise",
    3: "Couple"
}


def load_relations(data_dir: Path | None = None) -> Tuple[nx.DiGraph, Dict[int, str]]:
    """Charge les relations depuis le fichier disponible (CSV prioritaire, sinon TXT).
    
    Returns:
        - G: graphe NetworkX avec attributs relation_type sur les arêtes
        - relation_types: dict des types de relations
    """
    if data_dir is None:
        data_dir = Path(__file__).parent
    
    csv_path = data_dir / "relations.csv"
    txt_path = data_dir / "relations.txt"
    
    # Prioriser le CSV si disponible
    if csv_path.exists():
        print(f"Loading from {csv_path}")
        relations_typed, relation_types = parse_relations_csv(csv_path)
        G = build_graph(relations_typed)
        return G, relation_types
    
    elif txt_path.exists():
        print(f"Loading from {txt_path} (legacy format)")
        relations_simple = parse_relations_txt(txt_path)
        G = build_graph(relations_simple)
        # Tous les types à 0 (Bisous) par défaut
        return G, RELATION_TYPES
    
    else:
        raise FileNotFoundError(f"No relations file found in {data_dir}")


def get_relation_type_label(rel_type: int, relation_types: Dict[int, str] | None = None) -> str:
    """Récupère le label d'un type de relation."""
    if relation_types is None:
        relation_types = RELATION_TYPES
    return relation_types.get(rel_type, "Inconnu")


def get_edge_relation_type(G: nx.DiGraph, src: str, dst: str) -> int:
    """Récupère le type de relation d'une arête."""
    if G.has_edge(src, dst):
        return G[src][dst].get('relation_type', 0)
    return 0
