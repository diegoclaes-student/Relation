"""
Audit/History Management Repository
Gère l'historique des modifications
"""

from typing import List, Dict, Optional
import sqlite3
from datetime import datetime
from pathlib import Path
from database.base import db_manager

DB_PATH = Path(__file__).parent.parent / "social_network.db"


class AuditRepository:
    """Repository pour gérer l'historique des modifications"""
    
    @staticmethod
    def init_tables():
        """Initialise les tables audit"""
        conn = db_manager.get_connection()
        cur = conn.cursor()
        
        if getattr(db_manager, "use_postgres", False):
            conn.close()
            return
        
        # Table d'historique des modifications
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER,
                entity_name TEXT,
                performed_by TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                status TEXT DEFAULT 'completed',
                created_at TEXT NOT NULL,
                cancelled_by TEXT,
                cancelled_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def log_action(action_type: str, entity_type: str, entity_id: int, entity_name: str, 
                   performed_by: str, old_value: str = None, new_value: str = None) -> bool:
        """
        Enregistre une action dans l'historique
        
        Args:
            action_type: 'create', 'update', 'delete', etc.
            entity_type: 'person', 'relation', 'user', etc.
            entity_id: ID de l'entité
            entity_name: Nom/label de l'entité
            performed_by: Username de l'utilisateur
            old_value: Ancienne valeur (pour update)
            new_value: Nouvelle valeur (pour update)
        """
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO audit_log 
                (action_type, entity_type, entity_id, entity_name, performed_by, old_value, new_value, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (action_type, entity_type, entity_id, entity_name, performed_by, old_value, new_value, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging action: {e}")
            return False
    
    @staticmethod
    def get_recent_history(limit: int = 50, entity_type: str = None) -> List[Dict]:
        """Récupère l'historique récent"""
        try:
            conn = db_manager.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            if entity_type:
                cur.execute("""
                    SELECT * FROM audit_log 
                    WHERE entity_type = ? AND status = 'completed'
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (entity_type, limit))
            else:
                cur.execute("""
                    SELECT * FROM audit_log 
                    WHERE status = 'completed'
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cur.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error retrieving history: {e}")
            return []
    
    @staticmethod
    def get_cancelled_history(limit: int = 50) -> List[Dict]:
        """Récupère l'historique des modifications annulées"""
        try:
            conn = db_manager.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute("""
                SELECT * FROM audit_log 
                WHERE status = 'cancelled'
                ORDER BY cancelled_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cur.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error retrieving cancelled history: {e}")
            return []
    
    @staticmethod
    def cancel_action(audit_id: int, cancelled_by: str) -> bool:
        """Annule une action (mark as cancelled)"""
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE audit_log 
                SET status = 'cancelled', cancelled_by = ?, cancelled_at = ?
                WHERE id = ?
            """, (cancelled_by, datetime.now().isoformat(), audit_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error cancelling action: {e}")
            return False


# Auto-initialize on import
AuditRepository.init_tables()
