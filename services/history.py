#!/usr/bin/env python3
"""
HistoryService - Gestion de l'historique et fonctionnalité Undo/Redo
Enregistre toutes les actions importantes pour permettre annulation
"""

from typing import List, Dict, Optional, Tuple
import sqlite3
from datetime import datetime
from config import DB_PATH
from utils.constants import ACTION_TYPES, UNDOABLE_ACTIONS


class HistoryService:
    """Service de gestion de l'historique des actions"""
    
    def __init__(self, db_path: str = DB_PATH, max_history: int = 100):
        self.db_path = db_path
        self.max_history = max_history
    
    def _get_connection(self) -> sqlite3.Connection:
        """Connexion avec row_factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def record_action(self, 
                     action_type: str,
                     person1: Optional[str] = None,
                     person2: Optional[str] = None,
                     relation_type: Optional[int] = None,
                     performed_by: str = "system",
                     details: Optional[str] = None,
                     entity_type: Optional[str] = None,
                     entity_id: Optional[int] = None,
                     entity_name: Optional[str] = None,
                     old_value: Optional[str] = None,
                     new_value: Optional[str] = None) -> bool:
        """
        Enregistre une action dans l'historique
        
        Args:
            action_type: Type d'action (ex: "add_relation", "delete_person")
            person1: Première personne impliquée
            person2: Deuxième personne impliquée (pour relations)
            relation_type: Type de relation (si applicable)
            performed_by: Utilisateur ayant effectué l'action
            details: Détails supplémentaires en JSON
            entity_type: Type d'entité ('person', 'relation', 'user', 'account')
            entity_id: ID de l'entité modifiée
            entity_name: Nom de l'entité
            old_value: Ancienne valeur (pour UPDATE)
            new_value: Nouvelle valeur (pour UPDATE)
        
        Returns:
            True si enregistré avec succès
        """
        if action_type not in ACTION_TYPES:
            print(f"⚠️ Unknown action_type: {action_type}, recording anyway...")
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO history (
                    action_type, person1, person2, relation_type, performed_by, details,
                    status, entity_type, entity_id, entity_name, old_value, new_value
                )
                VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?)
            """, (action_type, person1, person2, relation_type, performed_by, details,
                  entity_type, entity_id, entity_name, old_value, new_value))
            
            conn.commit()
            
            # Nettoyer l'historique si trop long
            self._cleanup_old_history(conn)
            
            return True
            
        except Exception as e:
            print(f"Erreur enregistrement historique: {e}")
            return False
        finally:
            conn.close()
    
    def _cleanup_old_history(self, conn: sqlite3.Connection) -> None:
        """Garde seulement les N dernières entrées d'historique"""
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM history 
            WHERE id NOT IN (
                SELECT id FROM history 
                ORDER BY created_at DESC 
                LIMIT ?
            )
        """, (self.max_history,))
        
        conn.commit()
    
    def get_history(self, limit: int = 50, action_type: Optional[str] = None, status: str = 'active') -> List[Dict]:
        """
        Récupère l'historique des actions
        
        Args:
            limit: Nombre max d'entrées à retourner
            action_type: Filtrer par type d'action (optionnel)
            status: Filtrer par statut ('active', 'cancelled', 'all')
        
        Returns:
            Liste de dictionnaires représentant les actions
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Build query based on filters
            where_clauses = []
            params = []
            
            if action_type:
                where_clauses.append("action_type = ?")
                params.append(action_type)
            
            if status != 'all':
                where_clauses.append("(status = ? OR status IS NULL)")
                params.append(status)
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            params.append(limit)
            
            cursor.execute(f"""
                SELECT * FROM history 
                WHERE {where_sql}
                ORDER BY created_at DESC 
                LIMIT ?
            """, params)
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_last_action(self) -> Optional[Dict]:
        """Récupère la dernière action enregistrée"""
        history = self.get_history(limit=1)
        return history[0] if history else None
    
    def cancel_action(self, action_id: int, cancelled_by: str = "admin") -> Tuple[bool, str]:
        """
        Annule une action en la marquant comme cancelled (ne la supprime pas)
        
        Args:
            action_id: ID de l'action à annuler
            cancelled_by: Utilisateur qui annule l'action
        
        Returns:
            (success, message)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Get the action details first
            cursor.execute("SELECT * FROM history WHERE id = ?", (action_id,))
            action = cursor.fetchone()
            
            if not action:
                return False, f"Action {action_id} non trouvée"
            
            action_dict = dict(action)
            
            # Check if already cancelled
            if action_dict.get('status') == 'cancelled':
                return False, "Cette action a déjà été annulée"
            
            # Mark as cancelled
            cursor.execute("""
                UPDATE history 
                SET status = 'cancelled',
                    cancelled_at = CURRENT_TIMESTAMP,
                    cancelled_by = ?
                WHERE id = ?
            """, (cancelled_by, action_id))
            
            conn.commit()
            
            # Actually undo the action in the database
            success, msg = self._revert_action(action_dict, conn)
            
            if success:
                return True, f"✅ Action annulée: {msg}"
            else:
                # Rollback if revert failed
                conn.rollback()
                return False, f"❌ Erreur lors de l'annulation: {msg}"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur: {str(e)}"
        finally:
            conn.close()
    
    def _revert_action(self, action: Dict, conn: sqlite3.Connection) -> Tuple[bool, str]:
        """
        Revert the actual changes made by an action
        
        Args:
            action: The action dictionary
            conn: Active database connection
        
        Returns:
            (success, message)
        """
        action_type = action.get('action_type', '')
        cursor = conn.cursor()
        
        try:
            if action_type in ['ADD_RELATION', 'add_relation', 'UPDATE']:
                # Undo a relation addition - delete the relation
                cursor.execute("""
                    DELETE FROM relations 
                    WHERE (person1 = ? AND person2 = ?)
                       OR (person1 = ? AND person2 = ?)
                """, (action['person1'], action['person2'], 
                      action['person2'], action['person1']))
                
                conn.commit()
                return True, f"Relation supprimée: {action['person1']} ↔ {action['person2']}"
            
            elif action_type in ['DELETE_RELATION', 'delete_relation', 'DELETE']:
                # Undo a relation deletion - recreate the relation
                rel_type = action.get('relation_type', 0)
                
                cursor.execute("""
                    INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                    VALUES (?, ?, ?)
                """, (action['person1'], action['person2'], rel_type))
                
                cursor.execute("""
                    INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                    VALUES (?, ?, ?)
                """, (action['person2'], action['person1'], rel_type))
                
                conn.commit()
                return True, f"Relation restaurée: {action['person1']} ↔ {action['person2']}"
            
            elif action_type in ['UPDATE_PERSON', 'update_person']:
                # Undo person update - restore old value
                if action.get('old_value') and action.get('entity_id'):
                    cursor.execute("""
                        UPDATE persons 
                        SET name = ?
                        WHERE id = ?
                    """, (action['old_value'], action['entity_id']))
                    
                    conn.commit()
                    return True, f"Personne restaurée: {action['old_value']}"
                else:
                    return False, "Impossible de restaurer: données manquantes"
            
            elif action_type in ['ADD_PERSON', 'add_person', 'CREATE']:
                # Undo person creation - delete the person
                person_name = action.get('person1') or action.get('entity_name')
                
                # Delete all relations first
                cursor.execute("""
                    DELETE FROM relations 
                    WHERE person1 = ? OR person2 = ?
                """, (person_name, person_name))
                
                # Delete the person
                cursor.execute("DELETE FROM persons WHERE name = ?", (person_name,))
                
                conn.commit()
                return True, f"Personne supprimée: {person_name}"
            
            elif action_type in ['APPROVE', 'approve']:
                # For now, just mark as cancelled without reverting
                return True, "Action marquée comme annulée"
            
            else:
                # Unknown action type, just mark as cancelled
                return True, f"Action '{action_type}' marquée comme annulée (pas de revert automatique)"
            
        except Exception as e:
            return False, f"Erreur revert: {str(e)}"
    
    def can_undo(self) -> Tuple[bool, Optional[Dict]]:
        """
        Vérifie si la dernière action peut être annulée
        
        Returns:
            (can_undo, action_dict)
        """
        last_action = self.get_last_action()
        
        if not last_action:
            return False, None
        
        if last_action['action_type'] not in UNDOABLE_ACTIONS:
            return False, None
        
        return True, last_action
    
    def undo_last_action(self) -> Tuple[bool, str]:
        """
        Annule la dernière action enregistrée
        
        Returns:
            (success, message)
        """
        can_undo, action = self.can_undo()
        
        if not can_undo or not action:
            return False, "Aucune action à annuler"
        
        action_type = action['action_type']
        
        # Dispatcher vers la bonne méthode d'annulation
        if action_type == "add_relation":
            return self._undo_add_relation(action)
        elif action_type == "delete_relation":
            return self._undo_delete_relation(action)
        elif action_type == "add_person":
            return self._undo_add_person(action)
        elif action_type == "delete_person":
            return self._undo_delete_person(action)
        elif action_type == "edit_person":
            return self._undo_edit_person(action)
        elif action_type == "merge_persons":
            return self._undo_merge_persons(action)
        else:
            return False, f"Type d'action '{action_type}' non supporté pour undo"
    
    def _undo_add_relation(self, action: Dict) -> Tuple[bool, str]:
        """Annule l'ajout d'une relation"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Supprimer la relation dans les deux sens
            cursor.execute("""
                DELETE FROM relations 
                WHERE (person1 = ? AND person2 = ?)
                   OR (person1 = ? AND person2 = ?)
            """, (action['person1'], action['person2'], 
                  action['person2'], action['person1']))
            
            # Supprimer l'action de l'historique
            cursor.execute("DELETE FROM history WHERE id = ?", (action['id'],))
            
            conn.commit()
            return True, f"Relation annulée: {action['person1']} ↔ {action['person2']}"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur annulation: {str(e)}"
        finally:
            conn.close()
    
    def _undo_delete_relation(self, action: Dict) -> Tuple[bool, str]:
        """Annule la suppression d'une relation (la recrée)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Recréer la relation dans les deux sens
            rel_type = action.get('relation_type', 0)
            
            cursor.execute("""
                INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                VALUES (?, ?, ?)
            """, (action['person1'], action['person2'], rel_type))
            
            cursor.execute("""
                INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                VALUES (?, ?, ?)
            """, (action['person2'], action['person1'], rel_type))
            
            # Supprimer l'action de l'historique
            cursor.execute("DELETE FROM history WHERE id = ?", (action['id'],))
            
            conn.commit()
            return True, f"Suppression annulée: {action['person1']} ↔ {action['person2']}"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur annulation: {str(e)}"
        finally:
            conn.close()
    
    def _undo_add_person(self, action: Dict) -> Tuple[bool, str]:
        """Annule l'ajout d'une personne"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Supprimer toutes les relations de la personne
            cursor.execute("""
                DELETE FROM relations 
                WHERE person1 = ? OR person2 = ?
            """, (action['person1'], action['person1']))
            
            # Supprimer la personne (si table persons existe)
            try:
                cursor.execute("DELETE FROM persons WHERE name = ?", (action['person1'],))
            except:
                pass  # Table persons peut ne pas exister
            
            # Supprimer l'action de l'historique
            cursor.execute("DELETE FROM history WHERE id = ?", (action['id'],))
            
            conn.commit()
            return True, f"Ajout de personne annulé: {action['person1']}"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erreur annulation: {str(e)}"
        finally:
            conn.close()
    
    def _undo_delete_person(self, action: Dict) -> Tuple[bool, str]:
        """Annule la suppression d'une personne (nécessite détails)"""
        # Cette opération nécessite de stocker les détails de la personne dans action['details']
        # Pour l'instant, retourner non supporté
        return False, "Annulation suppression personne nécessite sauvegarde complète (TODO)"
    
    def _undo_edit_person(self, action: Dict) -> Tuple[bool, str]:
        """Annule la modification d'une personne"""
        # Nécessite de stocker l'état avant modification dans action['details']
        return False, "Annulation édition personne nécessite sauvegarde état (TODO)"
    
    def _undo_merge_persons(self, action: Dict) -> Tuple[bool, str]:
        """Annule la fusion de personnes"""
        # Opération complexe nécessitant sauvegarde complète
        return False, "Annulation fusion nécessite sauvegarde complète (TODO)"
    
    def clear_history(self) -> bool:
        """Vide tout l'historique"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history")
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, int]:
        """Statistiques sur l'historique"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Total actions
            cursor.execute("SELECT COUNT(*) as count FROM history")
            total = cursor.fetchone()['count']
            
            # Par type d'action
            cursor.execute("""
                SELECT action_type, COUNT(*) as count 
                FROM history 
                GROUP BY action_type
            """)
            
            by_type = {row['action_type']: row['count'] for row in cursor.fetchall()}
            
            return {
                'total': total,
                'by_type': by_type
            }
            
        finally:
            conn.close()


# Singleton instance
history_service = HistoryService()
