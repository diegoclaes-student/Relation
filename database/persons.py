#!/usr/bin/env python3
"""
PersonRepository - CRUD complet pour la gestion des personnes
Encapsule toute la logique DB liée aux personnes
"""

from typing import List, Dict, Optional, Tuple
from database.base import db_manager
from utils.validators import Validator, ValidationError


class PersonRepository:
    """Repository pour la gestion des personnes"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def _get_connection(self):
        """Connexion via DatabaseManager (SQLite ou PostgreSQL)"""
        return self.db_manager.get_connection()
    
    def _normalize(self, query: str) -> str:
        """Normalise les placeholders SQL selon la base de données"""
        return self.db_manager.normalize_query(query)
    
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
            cursor.execute(self._normalize("SELECT id FROM persons WHERE name = %s"), (clean_name,))
            if cursor.fetchone():
                return False, f"La personne '{clean_name}' existe déjà"
            
            # Créer la personne
            cursor.execute(self._normalize("""
                INSERT INTO persons (name, gender, sexual_orientation)
                VALUES (%s, %s, %s)
            """), (clean_name, gender, sexual_orientation))
            
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
            cursor.execute(self._normalize("SELECT * FROM persons WHERE id = %s"), (person_id,))
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
            cursor.execute(self._normalize("SELECT * FROM persons WHERE name = %s"), (name,))
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
            cursor.execute(self._normalize("SELECT name FROM persons WHERE id = %s"), (person_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Personne non trouvée"
            
            old_name = row['name']
            
            # Construire la requête UPDATE
            set_clauses = []
            values = []
            
            for field, value in kwargs.items():
                if field in ['name', 'gender', 'sexual_orientation']:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                return False, "Aucun champ valide à mettre à jour"
            
            values.append(person_id)
            
            query = self._normalize(f"UPDATE persons SET {', '.join(set_clauses)} WHERE id = %s")
            cursor.execute(query, values)
            
            # Si le nom a changé, mettre à jour les relations
            if 'name' in kwargs and kwargs['name'] != old_name:
                new_name = kwargs['name']
                
                cursor.execute(self._normalize("""
                    UPDATE relations SET person1 = %s WHERE person1 = %s
                """), (new_name, old_name))
                
                cursor.execute(self._normalize("""
                    UPDATE relations SET person2 = %s WHERE person2 = %s
                """), (new_name, old_name))
            
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
            cursor.execute(self._normalize("SELECT name FROM persons WHERE id = %s"), (person_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Personne non trouvée"
            
            person_name = row['name']
            
            if cascade:
                # Supprimer toutes les relations liées
                cursor.execute(self._normalize("""
                    DELETE FROM relations 
                    WHERE person1 = %s OR person2 = %s
                """), (person_name, person_name))
                
                relations_deleted = cursor.rowcount
            
            # Supprimer la personne
            cursor.execute(self._normalize("DELETE FROM persons WHERE id = %s"), (person_id,))
            
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
            cursor.execute(self._normalize("SELECT name FROM persons WHERE id = %s"), (source_id,))
            source_row = cursor.fetchone()
            if not source_row:
                conn.close()
                return False, "Personne source non trouvée"
            
            cursor.execute(self._normalize("SELECT name FROM persons WHERE id = %s"), (target_id,))
            target_row = cursor.fetchone()
            if not target_row:
                conn.close()
                return False, "Personne cible non trouvée"
            
            source_name = source_row['name']
            target_name = target_row['name']
            
            # Transférer toutes les relations de source vers target
            # Relations où source est person1
            cursor.execute(self._normalize("""
                SELECT DISTINCT person2, relation_type FROM relations 
                WHERE person1 = %s AND person2 != %s
            """), (source_name, target_name))
            
            relations_p1 = cursor.fetchall()
            for row in relations_p1:
                person2, rel_type = row['person2'], row['relation_type']
                
                # Vérifier si la relation existe déjà
                cursor.execute(self._normalize("""
                    SELECT COUNT(*) as cnt FROM relations 
                    WHERE person1 = %s AND person2 = %s AND relation_type = %s
                """), (target_name, person2, rel_type))
                
                if cursor.fetchone()['cnt'] == 0:
                    cursor.execute(self._normalize("""
                        INSERT INTO relations (person1, person2, relation_type)
                        VALUES (%s, %s, %s)
                    """), (target_name, person2, rel_type))
                
                # Symétrique
                cursor.execute(self._normalize("""
                    SELECT COUNT(*) as cnt FROM relations 
                    WHERE person1 = %s AND person2 = %s AND relation_type = %s
                """), (person2, target_name, rel_type))
                
                if cursor.fetchone()['cnt'] == 0:
                    cursor.execute(self._normalize("""
                        INSERT INTO relations (person1, person2, relation_type)
                        VALUES (%s, %s, %s)
                    """), (person2, target_name, rel_type))
            
            # Relations où source est person2
            cursor.execute(self._normalize("""
                SELECT DISTINCT person1, relation_type FROM relations 
                WHERE person2 = %s AND person1 != %s
            """), (source_name, target_name))
            
            relations_p2 = cursor.fetchall()
            for row in relations_p2:
                person1, rel_type = row['person1'], row['relation_type']
                
                # Vérifier si la relation existe déjà
                cursor.execute(self._normalize("""
                    SELECT COUNT(*) as cnt FROM relations 
                    WHERE person1 = %s AND person2 = %s AND relation_type = %s
                """), (person1, target_name, rel_type))
                
                if cursor.fetchone()['cnt'] == 0:
                    cursor.execute(self._normalize("""
                        INSERT INTO relations (person1, person2, relation_type)
                        VALUES (%s, %s, %s)
                    """), (person1, target_name, rel_type))
                
                # Symétrique
                cursor.execute(self._normalize("""
                    SELECT COUNT(*) as cnt FROM relations 
                    WHERE person1 = %s AND person2 = %s AND relation_type = %s
                """), (target_name, person1, rel_type))
                
                if cursor.fetchone()['cnt'] == 0:
                    cursor.execute(self._normalize("""
                        INSERT INTO relations (person1, person2, relation_type)
                        VALUES (%s, %s, %s)
                    """), (target_name, person1, rel_type))
            
            # Supprimer toutes les relations de source
            cursor.execute(self._normalize("""
                DELETE FROM relations 
                WHERE person1 = %s OR person2 = %s
            """), (source_name, source_name))
            
            # Supprimer la personne source
            cursor.execute(self._normalize("DELETE FROM persons WHERE id = %s"), (source_id,))
            
            conn.commit()
            return True, f"Fusion réussie: {source_name} → {target_name}"
            
        except Exception as e:
            conn.rollback()
            import traceback
            traceback.print_exc()
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
                WHERE name LIKE %s
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
            cursor.execute(self._normalize("SELECT name FROM persons WHERE id = %s"), (person_id,))
            row = cursor.fetchone()
            if not row:
                return 0
            
            person_name = row['name']
            
            # Compter les relations (dédupliquées)
            cursor.execute(self._normalize("""
                SELECT COUNT(DISTINCT person2) FROM relations 
                WHERE person1 = %s
            """), (person_name,))
            
            return cursor.fetchone()[0]
            
        finally:
            conn.close()


# Singleton instance
person_repository = PersonRepository()
