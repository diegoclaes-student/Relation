"""
Module de gestion de la base de données SQLite pour le graphe social.
"""

from __future__ import annotations
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import hashlib


# Types de relations globaux
RELATION_TYPES = {
    0: "Bisous",
    1: "Dodo ensemble",
    2: "Baise",
    3: "Couple"
}


class RelationDB:
    """Gestionnaire de base de données pour les relations sociales."""
    
    def __init__(self, db_path: Path | str = "relations.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Crée une connexion à la base de données."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Accès par nom de colonne
        return conn
    
    def init_database(self):
        """Initialise les tables de la base de données."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des relations approuvées
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person1 TEXT NOT NULL,
                person2 TEXT NOT NULL,
                relation_type INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_by TEXT,
                UNIQUE(person1, person2, relation_type)
            )
        """)
        
        # Table des relations en attente d'approbation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person1 TEXT NOT NULL,
                person2 TEXT NOT NULL,
                relation_type INTEGER NOT NULL DEFAULT 0,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                submitted_by TEXT,
                notes TEXT,
                UNIQUE(person1, person2, relation_type)
            )
        """)
        
        # Table des utilisateurs admin
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table d'historique des actions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                person1 TEXT,
                person2 TEXT,
                relation_type INTEGER,
                performed_by TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index pour améliorer les performances
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_person1 ON relations(person1)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_person2 ON relations(person2)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_date ON history(created_at DESC)")
        
        conn.commit()
        conn.close()
    
    def add_relation(self, person1: str, person2: str, relation_type: int = 0, 
                     approved_by: str = "system") -> bool:
        """Ajoute une relation approuvée."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO relations (person1, person2, relation_type, approved_by)
                VALUES (?, ?, ?, ?)
            """, (person1, person2, relation_type, approved_by))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Relation déjà existante
            return False
        finally:
            conn.close()
    
    def submit_pending_relation(self, person1: str, person2: str, relation_type: int = 0,
                               submitted_by: str = "anonymous", notes: str = "") -> bool:
        """Soumet une nouvelle relation en attente d'approbation."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO pending_relations (person1, person2, relation_type, submitted_by, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (person1, person2, relation_type, submitted_by, notes))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Relation déjà en attente
            return False
        finally:
            conn.close()
    
    def get_pending_relations(self) -> List[Dict]:
        """Récupère toutes les relations en attente."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, person1, person2, relation_type, submitted_at, submitted_by, notes
            FROM pending_relations
            ORDER BY submitted_at DESC
        """)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def approve_relation(self, pending_id: int, approved_by: str) -> bool:
        """Approuve une relation en attente et la déplace vers les relations actives."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Récupérer la relation en attente
            cursor.execute("""
                SELECT person1, person2, relation_type
                FROM pending_relations
                WHERE id = ?
            """, (pending_id,))
            
            row = cursor.fetchone()
            if not row:
                return False
            
            person1, person2, relation_type = row
            
            # Ajouter aux relations approuvées
            cursor.execute("""
                INSERT INTO relations (person1, person2, relation_type, approved_by)
                VALUES (?, ?, ?, ?)
            """, (person1, person2, relation_type, approved_by))
            
            # Supprimer de la liste d'attente
            cursor.execute("DELETE FROM pending_relations WHERE id = ?", (pending_id,))
            
            conn.commit()
            
            # Logger l'action
            self.log_action("APPROVE", person1, person2, relation_type, approved_by, 
                          "Relation approuvée depuis pending")
            
            return True
        except sqlite3.IntegrityError:
            # Relation déjà existante
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def reject_relation(self, pending_id: int, rejected_by: str = "admin") -> bool:
        """Rejette une relation en attente."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer les infos avant de supprimer
        cursor.execute("""
            SELECT person1, person2, relation_type
            FROM pending_relations
            WHERE id = ?
        """, (pending_id,))
        
        row = cursor.fetchone()
        if row:
            person1, person2, relation_type = row
            cursor.execute("DELETE FROM pending_relations WHERE id = ?", (pending_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            
            if deleted:
                self.log_action("REJECT", person1, person2, relation_type, rejected_by, 
                              "Relation rejetée depuis pending")
            
            conn.close()
            return deleted
        
        conn.close()
        return False
    
    def get_all_relations(self) -> List[Tuple[str, str, int]]:
        """Récupère toutes les relations approuvées."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT person1, person2, relation_type FROM relations")
        results = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_all_persons(self) -> List[str]:
        """Récupère la liste de toutes les personnes uniques."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT person1 FROM relations
            UNION
            SELECT DISTINCT person2 FROM relations
            ORDER BY person1
        """)
        
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results
    
    def add_admin(self, username: str, password: str) -> bool:
        """Ajoute un administrateur."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Hash du mot de passe (simple SHA256 pour démo, utiliser bcrypt en prod)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute("""
                INSERT INTO admins (username, password_hash)
                VALUES (?, ?)
            """, (username, password_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def verify_admin(self, username: str, password: str) -> bool:
        """Vérifie les identifiants d'un admin."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute("""
            SELECT id FROM admins
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    def log_action(self, action_type: str, person1: str = None, person2: str = None, 
                   relation_type: int = None, performed_by: str = "system", details: str = ""):
        """Enregistre une action dans l'historique."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO history (action_type, person1, person2, relation_type, performed_by, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (action_type, person1, person2, relation_type, performed_by, details))
        
        conn.commit()
        conn.close()
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Récupère l'historique des actions."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, action_type, person1, person2, relation_type, performed_by, details, created_at
            FROM history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def delete_relation(self, person1: str, person2: str, relation_type: int, deleted_by: str = "admin") -> bool:
        """Supprime une relation et enregistre dans l'historique."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM relations
            WHERE person1 = ? AND person2 = ? AND relation_type = ?
        """, (person1, person2, relation_type))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        
        if deleted:
            self.log_action("DELETE", person1, person2, relation_type, deleted_by, 
                          f"Relation supprimée")
        
        conn.close()
        return deleted
    
    def update_relation_type(self, person1: str, person2: str, old_type: int, new_type: int, 
                            updated_by: str = "admin") -> bool:
        """Modifie le type d'une relation."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE relations
            SET relation_type = ?
            WHERE person1 = ? AND person2 = ? AND relation_type = ?
        """, (new_type, person1, person2, old_type))
        
        updated = cursor.rowcount > 0
        conn.commit()
        
        if updated:
            self.log_action("UPDATE", person1, person2, new_type, updated_by, 
                          f"Type changé: {old_type} → {new_type}")
        
        conn.close()
        return updated


def migrate_csv_to_db(csv_path: Path, db: RelationDB):
    """Migre les données du CSV vers la base de données."""
    imported_count = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(';')
            if len(parts) < 3:
                continue
            
            person1 = parts[0].strip()
            person2 = parts[1].strip()
            try:
                relation_type = int(parts[2].strip())
            except ValueError:
                relation_type = 0
            
            if db.add_relation(person1, person2, relation_type, "migration"):
                imported_count += 1
    
    return imported_count


if __name__ == "__main__":
    # Test et migration
    db = RelationDB()
    
    # Créer un admin par défaut
    db.add_admin("admin", "admin123")
    print("✅ Admin créé: admin / admin123")
    
    # Migrer le CSV
    csv_path = Path("relations.csv")
    if csv_path.exists():
        count = migrate_csv_to_db(csv_path, db)
        print(f"✅ {count} relations importées depuis {csv_path}")
    
    print(f"\n📊 Total personnes: {len(db.get_all_persons())}")
    print(f"📊 Total relations: {len(db.get_all_relations())}")
