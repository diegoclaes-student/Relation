#!/usr/bin/env python3
"""
PersonRepository - CRUD complet pour la gestion des personnes
Encapsule toute la logique DB liée aux personnes
"""

from typing import List, Dict, Optional, Tuple
import sqlite3
from config import DB_PATH
from utils.validators import Validator, ValidationError


class PersonRepository:
    """Repository pour la gestion des personnes"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Connexion avec row_factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create(self, name: str, gender: Optional[str] = None, 
               sexual_orientation: Optional[str] = None) -> Tuple[bool, str]:
        """
        Crée une nouvelle personne
        
        Args:
            name: Nom de la personne (sera nettoyé et validé)
            gender: Genre (optionnel)
            sexual_orientation: Orientation sexuelle (optionnelle)
        
        Returns:
            (success, message)
        """
        try:
            # Validation et nettoyage
            clean_name = Validator.sanitize_name(name)
            Validator.validate_person_name(clean_name)
            
            if gender:
                Validator.validate_gender(gender)
            
            if sexual_orientation:
                Validator.validate_orientation(sexual_orientation)
            
        except ValidationError as e:
            return False, str(e)
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Vérifier si existe déjà
            cursor.execute("SELECT id FROM persons WHERE name = ?", (clean_name,))
            if cursor.fetchone():
                return False, f"La personne '{clean_name}' existe déjà"
            
            # Créer la personne
            cursor.execute("""
                INSERT INTO persons (name, gender, sexual_orientation)
                VALUES (?, ?, ?)
            """, (clean_name, gender, sexual_orientation))
            
            conn.commit()
            return True, f"Personne créée: {clean_name}"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur création: {str(e)}"
        finally:
            conn.close()
    
    def read(self, person_id: int) -> Optional[Dict]:
        """
        Récupère une personne par ID
        
        Args:
            person_id: ID de la personne
        
        Returns:
            Dictionnaire avec infos personne ou None
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons WHERE id = ?", (person_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def read_by_name(self, name: str) -> Optional[Dict]:
        """
        Récupère une personne par nom
        
        Args:
            name: Nom de la personne
        
        Returns:
            Dictionnaire avec infos personne ou None
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def read_all(self) -> List[Dict]:
        """
        Récupère toutes les personnes
        
        Returns:
            Liste de dictionnaires
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def update(self, person_id: int, **kwargs) -> Tuple[bool, str]:
        """
        Met à jour une personne
        
        Args:
            person_id: ID de la personne
            **kwargs: Champs à mettre à jour (name, gender, sexual_orientation)
        
        Returns:
            (success, message)
        """
        if not kwargs:
            return False, "Aucune modification spécifiée"
        
        # Validation
        try:
            if 'name' in kwargs:
                clean_name = Validator.sanitize_name(kwargs['name'])
                Validator.validate_person_name(clean_name)
                kwargs['name'] = clean_name
            
            if 'gender' in kwargs and kwargs['gender']:
                Validator.validate_gender(kwargs['gender'])
            
            if 'sexual_orientation' in kwargs and kwargs['sexual_orientation']:
                Validator.validate_orientation(kwargs['sexual_orientation'])
                
        except ValidationError as e:
            return False, str(e)
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Vérifier que la personne existe
            cursor.execute("SELECT name FROM persons WHERE id = ?", (person_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Personne non trouvée"
            
            old_name = row['name']
            
            # Construire la requête UPDATE
            set_clauses = []
            values = []
            
            for field, value in kwargs.items():
                if field in ['name', 'gender', 'sexual_orientation']:
                    set_clauses.append(f"{field} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False, "Aucun champ valide à mettre à jour"
            
            values.append(person_id)
            
            query = f"UPDATE persons SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            
            # Si le nom a changé, mettre à jour les relations
            if 'name' in kwargs and kwargs['name'] != old_name:
                new_name = kwargs['name']
                
                cursor.execute("""
                    UPDATE relations SET person1 = ? WHERE person1 = ?
                """, (new_name, old_name))
                
                cursor.execute("""
                    UPDATE relations SET person2 = ? WHERE person2 = ?
                """, (new_name, old_name))
            
            conn.commit()
            return True, f"Personne mise à jour: {kwargs.get('name', old_name)}"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur mise à jour: {str(e)}"
        finally:
            conn.close()
    
    def delete(self, person_id: int, cascade: bool = True) -> Tuple[bool, str]:
        """
        Supprime une personne
        
        Args:
            person_id: ID de la personne
            cascade: Si True, supprime aussi toutes les relations
        
        Returns:
            (success, message)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Récupérer le nom de la personne
            cursor.execute("SELECT name FROM persons WHERE id = ?", (person_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Personne non trouvée"
            
            person_name = row['name']
            
            if cascade:
                # Supprimer toutes les relations liées
                cursor.execute("""
                    DELETE FROM relations 
                    WHERE person1 = ? OR person2 = ?
                """, (person_name, person_name))
                
                relations_deleted = cursor.rowcount
            
            # Supprimer la personne
            cursor.execute("DELETE FROM persons WHERE id = ?", (person_id,))
            
            conn.commit()
            
            if cascade:
                return True, f"Personne supprimée: {person_name} ({relations_deleted} relations)"
            else:
                return True, f"Personne supprimée: {person_name}"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur suppression: {str(e)}"
        finally:
            conn.close()
    
    def merge(self, source_id: int, target_id: int) -> Tuple[bool, str]:
        """
        Fusionne deux personnes (toutes les relations de source → target)
        
        Args:
            source_id: ID de la personne à fusionner (sera supprimée)
            target_id: ID de la personne cible (sera conservée)
        
        Returns:
            (success, message)
        """
        if source_id == target_id:
            return False, "Impossible de fusionner une personne avec elle-même"
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Récupérer les noms
            cursor.execute("SELECT name FROM persons WHERE id = ?", (source_id,))
            source_row = cursor.fetchone()
            if not source_row:
                return False, "Personne source non trouvée"
            
            cursor.execute("SELECT name FROM persons WHERE id = ?", (target_id,))
            target_row = cursor.fetchone()
            if not target_row:
                return False, "Personne cible non trouvée"
            
            source_name = source_row['name']
            target_name = target_row['name']
            
            # Transférer toutes les relations de source vers target
            # Attention aux doublons : utiliser INSERT OR IGNORE
            
            # Relations où source est person1
            cursor.execute("""
                SELECT DISTINCT person2, relation_type FROM relations 
                WHERE person1 = ? AND person2 != ?
            """, (source_name, target_name))
            
            for row in cursor.fetchall():
                person2, rel_type = row['person2'], row['relation_type']
                
                # Ajouter relation target → person2 (si pas déjà existante)
                cursor.execute("""
                    INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                    VALUES (?, ?, ?)
                """, (target_name, person2, rel_type))
                
                # Symétrique
                cursor.execute("""
                    INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                    VALUES (?, ?, ?)
                """, (person2, target_name, rel_type))
            
            # Relations où source est person2
            cursor.execute("""
                SELECT DISTINCT person1, relation_type FROM relations 
                WHERE person2 = ? AND person1 != ?
            """, (source_name, target_name))
            
            for row in cursor.fetchall():
                person1, rel_type = row['person1'], row['relation_type']
                
                # Ajouter relation person1 → target
                cursor.execute("""
                    INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                    VALUES (?, ?, ?)
                """, (person1, target_name, rel_type))
                
                # Symétrique
                cursor.execute("""
                    INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                    VALUES (?, ?, ?)
                """, (target_name, person1, rel_type))
            
            # Supprimer toutes les relations de source
            cursor.execute("""
                DELETE FROM relations 
                WHERE person1 = ? OR person2 = ?
            """, (source_name, source_name))
            
            # Supprimer la personne source
            cursor.execute("DELETE FROM persons WHERE id = ?", (source_id,))
            
            conn.commit()
            return True, f"Fusion réussie: {source_name} → {target_name}"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur fusion: {str(e)}"
        finally:
            conn.close()
    
    def search(self, query: str) -> List[Dict]:
        """
        Recherche des personnes par nom (LIKE)
        
        Args:
            query: Terme de recherche
        
        Returns:
            Liste de personnes correspondantes
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM persons 
                WHERE name LIKE ?
                ORDER BY name
            """, (f"%{query}%",))
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_relation_count(self, person_id: int) -> int:
        """
        Compte le nombre de relations d'une personne
        
        Args:
            person_id: ID de la personne
        
        Returns:
            Nombre de relations
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Récupérer le nom
            cursor.execute("SELECT name FROM persons WHERE id = ?", (person_id,))
            row = cursor.fetchone()
            if not row:
                return 0
            
            person_name = row['name']
            
            # Compter les relations (dédupliquées)
            cursor.execute("""
                SELECT COUNT(DISTINCT person2) FROM relations 
                WHERE person1 = ?
            """, (person_name,))
            
            return cursor.fetchone()[0]
            
        finally:
            conn.close()


# Singleton instance
person_repository = PersonRepository()
