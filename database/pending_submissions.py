"""
Pending Submissions Repository
Gère les soumissions en attente (relations et personnes proposées par les utilisateurs)
"""

from typing import Optional, List, Dict
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "social_network.db"


class PendingSubmissionRepository:
    """Repository pour gérer les soumissions en attente"""
    
    @staticmethod
    def init_tables():
        """Initialise les tables de soumissions"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Table des personnes proposées
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pending_persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                submitted_by TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        # Table des relations proposées
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pending_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person1 TEXT NOT NULL,
                person2 TEXT NOT NULL,
                relation_type INTEGER NOT NULL,
                submitted_by TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def submit_person(name: str, submitted_by: str) -> Optional[int]:
        """Soumet une nouvelle personne pour approbation"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cur.execute("""
                INSERT INTO pending_persons (name, submitted_by, submitted_at, status)
                VALUES (?, ?, ?, 'pending')
            """, (name, submitted_by, now))
            
            submission_id = cur.lastrowid
            conn.commit()
            conn.close()
            return submission_id
        except:
            return None
    
    @staticmethod
    def submit_relation(person1: str, person2: str, relation_type: int, submitted_by: str) -> Optional[int]:
        """Soumet une nouvelle relation pour approbation"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cur.execute("""
                INSERT INTO pending_relations 
                (person1, person2, relation_type, submitted_by, submitted_at, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """, (person1, person2, relation_type, submitted_by, now))
            
            submission_id = cur.lastrowid
            conn.commit()
            conn.close()
            return submission_id
        except:
            return None
    
    @staticmethod
    def get_pending_persons() -> List[Dict]:
        """Récupère toutes les personnes en attente"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, name, submitted_by, submitted_at, status
            FROM pending_persons WHERE status = 'pending'
            ORDER BY submitted_at DESC
        """)
        
        submissions = []
        for row in cur.fetchall():
            submissions.append({
                'id': row[0],
                'name': row[1],
                'submitted_by': row[2],
                'submitted_at': row[3],
                'status': row[4]
            })
        
        conn.close()
        return submissions
    
    @staticmethod
    def get_pending_relations() -> List[Dict]:
        """Récupère toutes les relations en attente"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, person1, person2, relation_type, submitted_by, submitted_at, status
            FROM pending_relations WHERE status = 'pending'
            ORDER BY submitted_at DESC
        """)
        
        submissions = []
        for row in cur.fetchall():
            submissions.append({
                'id': row[0],
                'person1': row[1],
                'person2': row[2],
                'relation_type': row[3],
                'submitted_by': row[4],
                'submitted_at': row[5],
                'status': row[6]
            })
        
        conn.close()
        return submissions
    
    @staticmethod
    def approve_person(submission_id: int) -> bool:
        """Approuve une personne et l'ajoute à la base"""
        try:
            from database.persons import person_repository
            
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Récupérer la soumission
            cur.execute("""
                SELECT name FROM pending_persons 
                WHERE id = ? AND status = 'pending'
            """, (submission_id,))
            
            row = cur.fetchone()
            if not row:
                conn.close()
                return False
            
            name = row[0]
            
            # Ajouter la personne
            person_repository.add_person(name)
            
            # Marquer comme approuvée
            cur.execute("""
                UPDATE pending_persons SET status = 'approved' WHERE id = ?
            """, (submission_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error approving person: {e}")
            return False
    
    @staticmethod
    def approve_relation(submission_id: int) -> bool:
        """Approuve une relation et l'ajoute à la base"""
        try:
            from database.relations import relation_repository
            
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Récupérer la soumission
            cur.execute("""
                SELECT person1, person2, relation_type FROM pending_relations 
                WHERE id = ? AND status = 'pending'
            """, (submission_id,))
            
            row = cur.fetchone()
            if not row:
                conn.close()
                return False
            
            person1, person2, relation_type = row
            
            # Ajouter la relation
            relation_repository.add_relation(person1, person2, relation_type)
            
            # Marquer comme approuvée
            cur.execute("""
                UPDATE pending_relations SET status = 'approved' WHERE id = ?
            """, (submission_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error approving relation: {e}")
            return False
    
    @staticmethod
    def reject_person(submission_id: int) -> bool:
        """Rejette une soumission de personne"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE pending_persons SET status = 'rejected' WHERE id = ?
            """, (submission_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    @staticmethod
    def reject_relation(submission_id: int) -> bool:
        """Rejette une soumission de relation"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE pending_relations SET status = 'rejected' WHERE id = ?
            """, (submission_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False


# Initialiser les tables
PendingSubmissionRepository.init_tables()

# Export
pending_submission_repository = PendingSubmissionRepository()
