#!/usr/bin/env python3
"""
GraphBuilder - Construction optimisée du graphe NetworkX avec déduplication
Cache et memoization pour performance maximale
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional
from functools import lru_cache
import hashlib
import json


class GraphBuilder:
    """Constructeur de graphe optimisé avec cache"""
    
    def __init__(self):
        self._cache: Dict[str, nx.Graph] = {}
        self._last_hash: Optional[str] = None
    
    @staticmethod
    def _compute_relations_hash(relations: List[Tuple[str, str, int]]) -> str:
        """Calcule un hash des relations pour détection de changement"""
        # Normaliser les relations pour détecter les changements
        normalized = sorted([(p1, p2, rt) for p1, p2, rt in relations])
        relations_str = json.dumps(normalized, sort_keys=True)
        return hashlib.md5(relations_str.encode()).hexdigest()
    
    def build_graph(self, 
                   relations: List[Tuple[str, str, int]], 
                   deduplicate: bool = True,
                   use_cache: bool = True) -> nx.Graph:
        """
        Construit un graphe NetworkX à partir des relations
        
        Args:
            relations: Liste de (person1, person2, relation_type)
            deduplicate: Si True, déduplique les relations bidirectionnelles
            use_cache: Si True, utilise le cache pour éviter reconstruction
        
        Returns:
            NetworkX Graph avec attributs sur nodes et edges
        """
        # Vérifier le cache
        if use_cache:
            current_hash = self._compute_relations_hash(relations)
            if current_hash == self._last_hash and current_hash in self._cache:
                return self._cache[current_hash].copy()  # Return copy pour éviter mutations
        
        G = nx.Graph()
        
        if not relations:
            return G
        
        # Dédupliquer si demandé
        if deduplicate:
            relations = self._deduplicate_relations(relations)
        
        # Extraire toutes les personnes
        persons = set()
        for p1, p2, _ in relations:
            persons.add(p1)
            persons.add(p2)
        
        # Ajouter les nœuds
        for person in persons:
            G.add_node(person, name=person)
        
        # Ajouter les arêtes avec type de relation
        for p1, p2, rel_type in relations:
            G.add_edge(p1, p2, relation_type=rel_type)
        
        # Calculer attributs de nœuds (degré, centralité, etc.)
        self._compute_node_attributes(G)
        
        # Mettre en cache
        if use_cache:
            self._cache[current_hash] = G.copy()
            self._last_hash = current_hash
        
        return G
    
    @staticmethod
    def _deduplicate_relations(relations: List[Tuple[str, str, int]]) -> List[Tuple[str, str, int]]:
        """
        Déduplique les relations bidirectionnelles
        Garde une seule paire (p1, p2) au lieu de (p1, p2) + (p2, p1)
        """
        seen = set()
        unique = []
        
        for p1, p2, rel_type in relations:
            # Créer une paire normalisée (ordre alphabétique)
            pair = tuple(sorted([p1, p2]))
            
            if pair not in seen:
                seen.add(pair)
                unique.append((p1, p2, rel_type))
        
        return unique
    
    @staticmethod
    def _compute_node_attributes(G: nx.Graph) -> None:
        """
        Calcule et ajoute des attributs aux nœuds
        (degré, centralité, clustering coefficient)
        """
        if len(G) == 0:
            return
        
        # Degré
        degrees = dict(G.degree())
        nx.set_node_attributes(G, degrees, 'degree')
        
        # Centralité de proximité (closeness centrality)
        try:
            closeness = nx.closeness_centrality(G)
            nx.set_node_attributes(G, closeness, 'closeness')
        except:
            # Si graphe non connexe, mettre 0
            nx.set_node_attributes(G, {node: 0 for node in G.nodes()}, 'closeness')
        
        # Betweenness centrality (combien de fois un nœud est sur le chemin entre 2 autres)
        try:
            betweenness = nx.betweenness_centrality(G)
            nx.set_node_attributes(G, betweenness, 'betweenness')
        except:
            nx.set_node_attributes(G, {node: 0 for node in G.nodes()}, 'betweenness')
        
        # Clustering coefficient (combien d'amis sont aussi amis entre eux)
        try:
            clustering = nx.clustering(G)
            nx.set_node_attributes(G, clustering, 'clustering')
        except:
            nx.set_node_attributes(G, {node: 0 for node in G.nodes()}, 'clustering')
    
    def detect_communities(self, G: nx.Graph) -> Dict[str, int]:
        """
        Détecte les communautés dans le graphe
        
        Args:
            G: NetworkX Graph
        
        Returns:
            Dictionnaire {person: community_id}
        """
        if len(G) == 0:
            return {}
        
        try:
            # Utiliser l'algorithme de Louvain pour détecter les communautés
            from networkx.algorithms import community
            communities = community.greedy_modularity_communities(G)
            
            # Créer mapping personne -> communauté
            community_map = {}
            for idx, comm in enumerate(communities):
                for person in comm:
                    community_map[person] = idx
            
            return community_map
        except:
            # Fallback: tout le monde dans la même communauté
            return {node: 0 for node in G.nodes()}
    
    def get_graph_stats(self, G: nx.Graph) -> Dict[str, any]:
        """
        Calcule des statistiques sur le graphe
        
        Returns:
            Dictionnaire de statistiques
        """
        if len(G) == 0:
            return {
                'nodes': 0,
                'edges': 0,
                'density': 0,
                'components': 0,
                'avg_degree': 0,
                'diameter': 0,
            }
        
        try:
            # Nombre de composantes connexes
            num_components = nx.number_connected_components(G)
            
            # Densité (ratio arêtes réelles / arêtes possibles)
            density = nx.density(G)
            
            # Degré moyen
            degrees = dict(G.degree())
            avg_degree = sum(degrees.values()) / len(degrees) if degrees else 0
            
            # Diamètre (plus long chemin entre 2 nœuds)
            try:
                if nx.is_connected(G):
                    diameter = nx.diameter(G)
                else:
                    # Pour graphe non connexe, prendre max diameter des composantes
                    diameter = max(nx.diameter(G.subgraph(c)) 
                                 for c in nx.connected_components(G))
            except:
                diameter = 0
            
            return {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': round(density, 3),
                'components': num_components,
                'avg_degree': round(avg_degree, 2),
                'diameter': diameter,
            }
        except Exception as e:
            return {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'error': str(e)
            }
    
    def clear_cache(self) -> None:
        """Vide le cache (utile après modifications importantes)"""
        self._cache.clear()
        self._last_hash = None


# Singleton instance
graph_builder = GraphBuilder()
