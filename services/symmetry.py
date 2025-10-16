#!/usr/bin/env python3
"""
SymmetryManager - Garantit la symétrie bidirectionnelle des relations
Utilisé par tous les callbacks pour éviter les relations asymétriques
"""

from typing import List, Tuple, Set
import sqlite3
from config import DB_PATH


class SymmetryManager:
    """Gère la symétrie des relations de manière centralisée"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Connexion avec row_factory pour dict-like access"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def ensure_symmetric_relation(self, person1: str, person2: str, relation_type: int) -> Tuple[bool, str]:
        """
        Ajoute une relation ET sa symétrique en transaction atomique
        
        Args:
            person1: Première personne
            person2: Deuxième personne
            relation_type: Type de relation (0-5)
        
        Returns:
            (success, message)
        """
        if person1 == person2:
            return False, "Une personne ne peut pas avoir de relation avec elle-même"
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Vérifier si la relation existe déjà (dans un sens ou l'autre)
            cursor.execute("""
                SELECT COUNT(*) as count FROM relations 
                WHERE (person1 = ? AND person2 = ?) 
                   OR (person1 = ? AND person2 = ?)
            """, (person1, person2, person2, person1))
            
            if cursor.fetchone()['count'] > 0:
                return False, "Cette relation existe déjà"
            
            # Ajouter les deux directions en une seule transaction
            cursor.execute("""
                INSERT INTO relations (person1, person2, relation_type)
                VALUES (?, ?, ?)
            """, (person1, person2, relation_type))
            
            cursor.execute("""
                INSERT INTO relations (person1, person2, relation_type)
                VALUES (?, ?, ?)
            """, (person2, person1, relation_type))
            
            conn.commit()
            return True, f"Relation ajoutée avec symétrie garantie"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur: {str(e)}"
        finally:
            conn.close()
    
    def delete_symmetric_relation(self, person1: str, person2: str) -> Tuple[bool, str]:
        """
        Supprime une relation ET sa symétrique en transaction atomique
        
        Args:
            person1: Première personne
            person2: Deuxième personne
        
        Returns:
            (success, message)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Supprimer les deux directions
            cursor.execute("""
                DELETE FROM relations 
                WHERE (person1 = ? AND person2 = ?)
                   OR (person1 = ? AND person2 = ?)
            """, (person1, person2, person2, person1))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                return True, f"Relation supprimée ({deleted_count} entrées)"
            else:
                return False, "Aucune relation trouvée"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur: {str(e)}"
        finally:
            conn.close()
    
    def audit_symmetry(self) -> List[Tuple[str, str, int]]:
        """
        Trouve toutes les relations asymétriques dans la base
        
        Returns:
            Liste de relations sans symétrique: [(person1, person2, relation_type)]
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r1.person1, r1.person2, r1.relation_type
                FROM relations r1
                LEFT JOIN relations r2 
                    ON r1.person1 = r2.person2 
                    AND r1.person2 = r2.person1
                WHERE r2.id IS NULL
            """)
            
            asymmetric = [(row['person1'], row['person2'], row['relation_type']) 
                         for row in cursor.fetchall()]
            
            return asymmetric
            
        finally:
            conn.close()
    
    def fix_asymmetric_relations(self) -> Tuple[int, List[str]]:
        """
        Corrige automatiquement toutes les relations asymétriques
        en ajoutant les relations manquantes
        
        Returns:
            (nombre_corrections, liste_messages)
        """
        asymmetric = self.audit_symmetry()
        
        if not asymmetric:
            return 0, ["✅ Toutes les relations sont symétriques"]
        
        conn = self._get_connection()
        messages = []
        fixed_count = 0
        
        try:
            cursor = conn.cursor()
            
            for person1, person2, relation_type in asymmetric:
                try:
                    cursor.execute("""
                        INSERT INTO relations (person1, person2, relation_type)
                        VALUES (?, ?, ?)
                    """, (person2, person1, relation_type))
                    
                    fixed_count += 1
                    messages.append(f"✅ Symétrie ajoutée: {person2} → {person1}")
                    
                except sqlite3.IntegrityError:
                    # Relation inverse existe déjà (race condition)
                    messages.append(f"⚠️  Symétrie existe déjà: {person2} → {person1}")
            
            conn.commit()
            messages.insert(0, f"🔧 {fixed_count} relations corrigées sur {len(asymmetric)} asymétriques détectées")
            
        except Exception as e:
            conn.rollback()
            messages.append(f"❌ Erreur: {str(e)}")
        finally:
            conn.close()
        
        return fixed_count, messages
    
    def get_deduplicated_relations(self) -> List[Tuple[str, str, int]]:
        """
        Retourne les relations dédupliquées (une seule par paire)
        Pour affichage dans le graphe
        
        Returns:
            Liste de relations uniques: [(person1, person2, relation_type)]
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Récupérer toutes les relations
            cursor.execute("SELECT person1, person2, relation_type FROM relations")
            all_relations = cursor.fetchall()
            
            # Dédupliquer en gardant une seule direction par paire
            seen: Set[Tuple[str, str]] = set()
            unique_relations = []
            
            for row in all_relations:
                p1, p2, rel_type = row['person1'], row['person2'], row['relation_type']
                
                # Créer une paire normalisée (ordre alphabétique)
                pair = tuple(sorted([p1, p2]))
                
                if pair not in seen:
                    seen.add(pair)
                    unique_relations.append((p1, p2, rel_type))
            
            return unique_relations
            
        finally:
            conn.close()
    
    def update_relation_type(self, person1: str, person2: str, new_type: int) -> Tuple[bool, str]:
        """
        Met à jour le type de relation dans les DEUX directions
        
        Args:
            person1: Première personne
            person2: Deuxième personne
            new_type: Nouveau type de relation
        
        Returns:
            (success, message)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Mettre à jour les deux directions
            cursor.execute("""
                UPDATE relations 
                SET relation_type = ?
                WHERE (person1 = ? AND person2 = ?)
                   OR (person1 = ? AND person2 = ?)
            """, (new_type, person1, person2, person2, person1))
            
            updated_count = cursor.rowcount
            conn.commit()
            
            if updated_count >= 2:
                return True, f"Type de relation mis à jour (symétrie préservée)"
            elif updated_count == 1:
                # Une seule direction trouvée - ajouter la symétrique
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO relations (person1, person2, relation_type)
                    VALUES (?, ?, ?)
                """, (person2, person1, new_type))
                conn.commit()
                return True, f"Type mis à jour + symétrie corrigée"
            else:
                return False, "Relation non trouvée"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur: {str(e)}"
        finally:
            conn.close()


# Singleton instance
symmetry_manager = SymmetryManager()
