#!/usr/bin/env python3
"""
RelationRepository - CRUD complet pour les relations
Garantit la symétrie automatique via SymmetryManager
"""

from typing import List, Dict, Optional, Tuple
import sqlite3
from config import DB_PATH
from utils.validators import Validator, ValidationError
from services.symmetry import symmetry_manager


class RelationRepository:
    """Repository pour la gestion des relations avec garantie symétrie"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.symmetry = symmetry_manager
    
    def _get_connection(self) -> sqlite3.Connection:
        """Connexion avec row_factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create(self, person1: str, person2: str, relation_type: int) -> Tuple[bool, str]:
        """
        Crée une relation symétrique
        
        Args:
            person1: Première personne
            person2: Deuxième personne
            relation_type: Type de relation (0-5)
        
        Returns:
            (success, message)
        """
        try:
            # Validation
            Validator.validate_relation(person1, person2, relation_type)
        except ValidationError as e:
            return False, str(e)
        
        # Utiliser le SymmetryManager pour garantir la symétrie
        return self.symmetry.ensure_symmetric_relation(person1, person2, relation_type)
    
    def read_all(self, deduplicate: bool = False) -> List[Tuple[str, str, int]]:
        """
        Récupère toutes les relations
        
        Args:
            deduplicate: Si True, retourne seulement une relation par paire
        
        Returns:
            Liste de (person1, person2, relation_type)
        """
        if deduplicate:
            return self.symmetry.get_deduplicated_relations()
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT person1, person2, relation_type FROM relations")
            return [(row['person1'], row['person2'], row['relation_type']) 
                   for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def read_by_person(self, person_name: str) -> List[Tuple[str, int]]:
        """
        Récupère toutes les relations d'une personne
        
        Args:
            person_name: Nom de la personne
        
        Returns:
            Liste de (autre_personne, relation_type)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT person2, relation_type FROM relations 
                WHERE person1 = ?
                ORDER BY person2
            """, (person_name,))
            
            return [(row['person2'], row['relation_type']) 
                   for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def update_type(self, person1: str, person2: str, new_type: int) -> Tuple[bool, str]:
        """
        Met à jour le type de relation (dans les deux sens)
        
        Args:
            person1: Première personne
            person2: Deuxième personne
            new_type: Nouveau type de relation
        
        Returns:
            (success, message)
        """
        try:
            Validator.validate_relation(person1, person2, new_type)
        except ValidationError as e:
            return False, str(e)
        
        # Utiliser le SymmetryManager pour mise à jour symétrique
        return self.symmetry.update_relation_type(person1, person2, new_type)
    
    def delete(self, person1: str, person2: str) -> Tuple[bool, str]:
        """
        Supprime une relation (dans les deux sens)
        
        Args:
            person1: Première personne
            person2: Deuxième personne
        
        Returns:
            (success, message)
        """
        # Utiliser le SymmetryManager pour suppression symétrique
        return self.symmetry.delete_symmetric_relation(person1, person2)
    
    def delete_all_for_person(self, person_name: str) -> Tuple[bool, str]:
        """
        Supprime toutes les relations d'une personne
        
        Args:
            person_name: Nom de la personne
        
        Returns:
            (success, message)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Supprimer toutes les relations (dans les deux sens)
            cursor.execute("""
                DELETE FROM relations 
                WHERE person1 = ? OR person2 = ?
            """, (person_name, person_name))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return True, f"{deleted_count} relations supprimées"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur suppression: {str(e)}"
        finally:
            conn.close()
    
    def exists(self, person1: str, person2: str) -> bool:
        """
        Vérifie si une relation existe (dans un sens ou l'autre)
        
        Args:
            person1: Première personne
            person2: Deuxième personne
        
        Returns:
            True si la relation existe
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM relations 
                WHERE (person1 = ? AND person2 = ?)
                   OR (person1 = ? AND person2 = ?)
            """, (person1, person2, person2, person1))
            
            return cursor.fetchone()['count'] > 0
            
        finally:
            conn.close()
    
    def get_relation_type(self, person1: str, person2: str) -> Optional[int]:
        """
        Récupère le type de relation entre deux personnes
        
        Args:
            person1: Première personne
            person2: Deuxième personne
        
        Returns:
            Type de relation ou None si n'existe pas
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT relation_type FROM relations 
                WHERE person1 = ? AND person2 = ?
                LIMIT 1
            """, (person1, person2))
            
            row = cursor.fetchone()
            return row['relation_type'] if row else None
            
        finally:
            conn.close()
    
    def audit_symmetry(self) -> List[Tuple[str, str, int]]:
        """
        Audit de symétrie : trouve les relations asymétriques
        
        Returns:
            Liste de relations sans symétrique
        """
        return self.symmetry.audit_symmetry()
    
    def fix_asymmetric_relations(self) -> Tuple[int, List[str]]:
        """
        Corrige toutes les relations asymétriques
        
        Returns:
            (nombre_corrections, messages)
        """
        return self.symmetry.fix_asymmetric_relations()
    
    def get_stats(self) -> Dict[str, any]:
        """
        Statistiques sur les relations
        
        Returns:
            Dictionnaire de statistiques
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Total relations
            cursor.execute("SELECT COUNT(*) as count FROM relations")
            total = cursor.fetchone()['count']
            
            # Relations uniques (dédupliquées)
            unique = len(self.symmetry.get_deduplicated_relations())
            
            # Par type
            cursor.execute("""
                SELECT relation_type, COUNT(*) as count 
                FROM relations 
                GROUP BY relation_type
            """)
            by_type = {row['relation_type']: row['count'] 
                      for row in cursor.fetchall()}
            
            # Audit symétrie
            asymmetric = len(self.symmetry.audit_symmetry())
            
            return {
                'total': total,
                'unique': unique,
                'by_type': by_type,
                'asymmetric': asymmetric,
                'symmetry_ok': asymmetric == 0
            }
            
        finally:
            conn.close()


# Singleton instance
relation_repository = RelationRepository()
