"""
Pending Submissions Repository
Gère les soumissions en attente (relations et personnes proposées par les utilisateurs)
"""

from typing import Optional, List, Dict
import sqlite3
from datetime import datetime
from pathlib import Path
from database.base import db_manager

DB_PATH = Path(__file__).parent.parent / "social_network.db"


class PendingSubmissionRepository:
    """Repository pour gérer les soumissions en attente"""
    
    @staticmethod
    def init_tables():
        """Initialise les tables de soumissions"""
        conn = db_manager.get_connection()
        cur = conn.cursor()

        if getattr(db_manager, "use_postgres", False):
            conn.close()
            return
        
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
            print(f"📝 [DB] Submitting person: name='{name}', submitted_by='{submitted_by}'")
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cur.execute("""
                INSERT INTO pending_persons (name, submitted_by, submitted_at, status)
                VALUES (%s, %s, %s, 'pending')
            """, (name, submitted_by, now))
            
            submission_id = cur.lastrowid
            print(f"✅ [DB] Person inserted with ID: {submission_id}")
            conn.commit()
            conn.close()
            return submission_id
        except Exception as e:
            print(f"❌ [DB] Error inserting person: {str(e)}")
            return None
    
    @staticmethod
    def submit_relation(person1: str, person2: str, relation_type: int, submitted_by: str) -> Optional[int]:
        """Soumet une nouvelle relation pour approbation"""
        try:
            print(f"📝 [DB] Submitting relation: person1='{person1}', person2='{person2}', type={relation_type}, by='{submitted_by}'")
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cur.execute("""
                INSERT INTO pending_relations 
                (person1, person2, relation_type, submitted_by, submitted_at, status)
                VALUES (%s, %s, %s, %s, %s, 'pending')
            """, (person1, person2, relation_type, submitted_by, now))
            
            submission_id = cur.lastrowid
            print(f"✅ [DB] Relation inserted with ID: {submission_id}")
            conn.commit()
            conn.close()
            return submission_id
        except Exception as e:
            print(f"❌ [DB] Error inserting relation: {str(e)}")
            return None
    
    @staticmethod
    def get_pending_persons() -> List[Dict]:
        """Récupère toutes les personnes en attente"""
        print(f"🔍 [DB] Getting pending persons...")
        conn = db_manager.get_connection()
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
        
        print(f"✅ [DB] Found {len(submissions)} pending persons: {submissions}")
        conn.close()
        return submissions
    
    @staticmethod
    def get_pending_relations() -> List[Dict]:
        """Récupère toutes les relations en attente"""
        print(f"🔍 [DB] Getting pending relations...")
        conn = db_manager.get_connection()
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
        
        print(f"✅ [DB] Found {len(submissions)} pending relations: {submissions}")
        conn.close()
        return submissions
    
    @staticmethod
    def approve_person(submission_id: int) -> bool:
        """Approuve une personne et l'ajoute à la base"""
        try:
            print(f"🔍 [DB] Approving person with ID: {submission_id}")
            from database.persons import person_repository
            
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            # Récupérer la soumission
            cur.execute("""
                SELECT name FROM pending_persons 
                WHERE id = %s AND status = 'pending'
            """, (submission_id,))
            
            row = cur.fetchone()
            if not row:
                print(f"❌ [DB] No pending person found with ID: {submission_id}")
                conn.close()
                return False
            
            name = row[0]
            print(f"✅ [DB] Found person: {name}")
            
            # Ajouter la personne
            person_repository.create(name)
            print(f"✅ [DB] Person added to main database")
            
            # Marquer comme approuvée
            cur.execute("""
                UPDATE pending_persons SET status = 'approved' WHERE id = %s
            """, (submission_id,))
            
            conn.commit()
            conn.close()
            print(f"✅ [DB] Person approved successfully")
            return True
        except Exception as e:
            print(f"❌ [DB] Error approving person: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def approve_relation(submission_id: int) -> bool:
        """Approuve une relation et l'ajoute à la base"""
        try:
            import traceback
            print(f"🔍 [DB] Approving relation with ID: {submission_id}")
            
            from database.relations import relation_repository
            from database.persons import person_repository
            
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            # Récupérer la soumission
            cur.execute("""
                SELECT person1, person2, relation_type FROM pending_relations 
                WHERE id = %s AND status = 'pending'
            """, (submission_id,))
            
            row = cur.fetchone()
            if not row:
                print(f"❌ [DB] No pending relation found with ID: {submission_id}")
                conn.close()
                return False
            
            person1, person2, relation_type = row
            print(f"✅ [DB] Found relation: {person1} <-> {person2} (type={relation_type})")
            
            # IMPORTANT: Créer les personnes s'il y a un __CREATE__ prefix
            if str(person1).startswith("__CREATE__"):
                p1_name = str(person1).replace("__CREATE__", "").strip()
                print(f"   → Creating new person 1: {p1_name}")
                person_repository.create(p1_name, gender=None, sexual_orientation=None)
                person1 = p1_name
            
            if str(person2).startswith("__CREATE__"):
                p2_name = str(person2).replace("__CREATE__", "").strip()
                print(f"   → Creating new person 2: {p2_name}")
                person_repository.create(p2_name, gender=None, sexual_orientation=None)
                person2 = p2_name
            
            print(f"   ✅ Final names: person1={person1}, person2={person2}")
            
            # Ajouter la relation
            relation_repository.create(person1, person2, relation_type)
            print(f"✅ [DB] Relation added to main database")
            
            # Marquer comme approuvée
            cur.execute("""
                UPDATE pending_relations SET status = 'approved' WHERE id = %s
            """, (submission_id,))
            
            conn.commit()
            conn.close()
            print(f"✅ [DB] Relation approved successfully")
            return True
        except Exception as e:
            print(f"❌ [DB] Error approving relation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def reject_person(submission_id: int) -> bool:
        """Rejette une soumission de personne"""
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE pending_persons SET status = 'rejected' WHERE id = %s
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
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE pending_relations SET status = 'rejected' WHERE id = %s
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
