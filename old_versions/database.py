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
        
        # Table des personnes avec informations détaillées
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                gender TEXT,
                sexual_orientation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_person_name ON persons(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_person1 ON relations(person1)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_person2 ON relations(person2)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_date ON history(created_at DESC)")
        
        conn.commit()
        conn.close()
    
    def add_relation(self, person1: str, person2: str, relation_type: int = 0, 
                     approved_by: str = "system", auto_symmetrize: bool = True) -> bool:
        """Ajoute une relation approuvée avec symétrie automatique."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Ajouter la relation principale
            cursor.execute("""
                INSERT INTO relations (person1, person2, relation_type, approved_by)
                VALUES (?, ?, ?, ?)
            """, (person1, person2, relation_type, approved_by))
            
            # Ajouter automatiquement la relation inverse si demandé
            if auto_symmetrize:
                try:
                    cursor.execute("""
                        INSERT INTO relations (person1, person2, relation_type, approved_by)
                        VALUES (?, ?, ?, ?)
                    """, (person2, person1, relation_type, approved_by))
                except sqlite3.IntegrityError:
                    # Relation inverse déjà existante, c'est OK
                    pass
            
            conn.commit()
            
            # Logger l'action
            self.log_action("ADD", person1, person2, relation_type, approved_by, 
                          "Relation ajoutée" + (" (avec symétrie)" if auto_symmetrize else ""))
            
            return True
        except sqlite3.IntegrityError:
            # Relation déjà existante
            conn.rollback()
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
    
    def approve_relation(self, pending_id: int, approved_by: str, auto_symmetrize: bool = True) -> bool:
        """Approuve une relation en attente avec symétrie automatique."""
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
            
            # Ajouter la relation inverse si auto_symmetrize
            if auto_symmetrize:
                try:
                    cursor.execute("""
                        INSERT INTO relations (person1, person2, relation_type, approved_by)
                        VALUES (?, ?, ?, ?)
                    """, (person2, person1, relation_type, approved_by))
                except sqlite3.IntegrityError:
                    # Relation inverse déjà existante
                    pass
            
            # Supprimer de la liste d'attente
            cursor.execute("DELETE FROM pending_relations WHERE id = ?", (pending_id,))
            
            conn.commit()
            
            # Logger l'action
            self.log_action("APPROVE", person1, person2, relation_type, approved_by, 
                          "Relation approuvée depuis pending" + (" (avec symétrie)" if auto_symmetrize else ""))
            
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
    
    def undo_action(self, history_id: int, performed_by: str = "admin") -> bool:
        """Annule une action de l'historique avec gestion automatique de la symétrie."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer l'action de l'historique
        cursor.execute("""
            SELECT action_type, person1, person2, relation_type
            FROM history
            WHERE id = ?
        """, (history_id,))
        
        action = cursor.fetchone()
        conn.close()
        
        if not action:
            return False
        
        action_type = action['action_type']
        person1 = action['person1']
        person2 = action['person2']
        relation_type = action['relation_type']
        
        success = False
        
        try:
            if action_type == 'ADD':
                # Annuler un ajout = supprimer avec symétrie automatique
                success = self.delete_relation(person1, person2, relation_type, 
                                              performed_by, auto_symmetrize=True)
                details = f"Annulation ajout: {person1} ↔ {person2} (avec symétrie)"
                
            elif action_type == 'DELETE':
                # Annuler une suppression = recréer avec symétrie automatique
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Ajouter relation directe
                cursor.execute("""
                    INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                    VALUES (?, ?, ?)
                """, (person1, person2, relation_type))
                
                # Ajouter relation inverse (symétrie)
                cursor.execute("""
                    INSERT OR IGNORE INTO relations (person1, person2, relation_type)
                    VALUES (?, ?, ?)
                """, (person2, person1, relation_type))
                
                conn.commit()
                conn.close()
                success = True
                details = f"Annulation suppression: {person1} ↔ {person2} (avec symétrie)"
                
            elif action_type == 'APPROVE':
                # Annuler une approbation = supprimer et remettre en pending
                self.delete_relation(person1, person2, relation_type, 
                                   performed_by, auto_symmetrize=True)
                
                # Remettre en pending
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO pending_relations (person1, person2, relation_type, submitted_by, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (person1, person2, relation_type, "system", "Annulation approbation"))
                conn.commit()
                conn.close()
                success = True
                details = f"Annulation approbation: {person1} → {person2} remis en attente"
            
            if success:
                # Logger l'annulation
                self.log_action("UNDO", person1, person2, relation_type, performed_by, details)
                
        except Exception as e:
            print(f"❌ Erreur lors de l'annulation: {e}")
            success = False
        
        return success
    
    def delete_relation(self, person1: str, person2: str, relation_type: int, 
                       deleted_by: str = "admin", auto_symmetrize: bool = True) -> bool:
        """Supprime une relation avec option de symétrie."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM relations
            WHERE person1 = ? AND person2 = ? AND relation_type = ?
        """, (person1, person2, relation_type))
        
        deleted = cursor.rowcount > 0
        
        # Supprimer aussi la relation inverse si auto_symmetrize
        if deleted and auto_symmetrize:
            cursor.execute("""
                DELETE FROM relations
                WHERE person1 = ? AND person2 = ? AND relation_type = ?
            """, (person2, person1, relation_type))
        
        conn.commit()
        
        if deleted:
            self.log_action("DELETE", person1, person2, relation_type, deleted_by, 
                          f"Relation supprimée" + (" (avec symétrie)" if auto_symmetrize else ""))
        
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
    
    # ===== GESTION DES PERSONNES =====
    
    def add_person(self, name: str, gender: str = None, sexual_orientation: str = None) -> bool:
        """Ajoute une personne dans la table persons."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO persons (name, gender, sexual_orientation)
                VALUES (?, ?, ?)
            """, (name, gender, sexual_orientation))
            conn.commit()
            self.log_action("ADD_PERSON", person1=name, details=f"Genre: {gender}, Orientation: {sexual_orientation}")
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_persons_detailed(self) -> List[Dict]:
        """Récupère toutes les personnes avec leurs informations."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, gender, sexual_orientation, created_at, updated_at
            FROM persons
            ORDER BY name
        """)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def update_person_info(self, name: str, gender: str = None, sexual_orientation: str = None, 
                          updated_by: str = "admin") -> bool:
        """Met à jour les informations d'une personne."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Vérifier si la personne existe
        cursor.execute("SELECT id FROM persons WHERE name = ?", (name,))
        if not cursor.fetchone():
            # Créer la personne si elle n'existe pas
            cursor.execute("""
                INSERT INTO persons (name, gender, sexual_orientation)
                VALUES (?, ?, ?)
            """, (name, gender, sexual_orientation))
        else:
            # Mettre à jour
            updates = []
            params = []
            
            if gender is not None:
                updates.append("gender = ?")
                params.append(gender)
            
            if sexual_orientation is not None:
                updates.append("sexual_orientation = ?")
                params.append(sexual_orientation)
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(name)
            
            if updates:
                cursor.execute(f"""
                    UPDATE persons
                    SET {', '.join(updates)}
                    WHERE name = ?
                """, params)
        
        conn.commit()
        self.log_action("UPDATE_PERSON", person1=name, performed_by=updated_by,
                       details=f"Genre: {gender}, Orientation: {sexual_orientation}")
        conn.close()
        return True
    
    def rename_person(self, old_name: str, new_name: str, updated_by: str = "admin") -> bool:
        """Renomme une personne avec cascade sur toutes les relations."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Vérifier que le nouveau nom n'existe pas déjà
            cursor.execute("SELECT id FROM persons WHERE name = ?", (new_name,))
            if cursor.fetchone():
                conn.close()
                return False
            
            # Mettre à jour la table persons
            cursor.execute("""
                UPDATE persons
                SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            """, (new_name, old_name))
            
            # Mettre à jour person1 dans relations
            cursor.execute("""
                UPDATE relations
                SET person1 = ?
                WHERE person1 = ?
            """, (new_name, old_name))
            
            # Mettre à jour person2 dans relations
            cursor.execute("""
                UPDATE relations
                SET person2 = ?
                WHERE person2 = ?
            """, (new_name, old_name))
            
            # Mettre à jour person1 dans pending_relations
            cursor.execute("""
                UPDATE pending_relations
                SET person1 = ?
                WHERE person1 = ?
            """, (new_name, old_name))
            
            # Mettre à jour person2 dans pending_relations
            cursor.execute("""
                UPDATE pending_relations
                SET person2 = ?
                WHERE person2 = ?
            """, (new_name, old_name))
            
            conn.commit()
            self.log_action("RENAME_PERSON", person1=old_name, person2=new_name, 
                          performed_by=updated_by, details=f"Renommé: {old_name} → {new_name}")
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Erreur lors du renommage: {e}")
            return False
    
    def merge_persons(self, primary_name: str, duplicate_name: str, updated_by: str = "admin") -> bool:
        """Fusionne deux personnes (transfère toutes les relations du doublon vers le principal)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Transférer toutes les relations où duplicate_name est person1
            cursor.execute("""
                SELECT person2, relation_type
                FROM relations
                WHERE person1 = ?
            """, (duplicate_name,))
            
            for person2, rel_type in cursor.fetchall():
                # Essayer d'ajouter la relation avec primary_name
                try:
                    cursor.execute("""
                        INSERT INTO relations (person1, person2, relation_type, approved_by)
                        VALUES (?, ?, ?, ?)
                    """, (primary_name, person2, rel_type, updated_by))
                except sqlite3.IntegrityError:
                    # Relation déjà existante, skip
                    pass
            
            # 2. Transférer toutes les relations où duplicate_name est person2
            cursor.execute("""
                SELECT person1, relation_type
                FROM relations
                WHERE person2 = ?
            """, (duplicate_name,))
            
            for person1, rel_type in cursor.fetchall():
                # Essayer d'ajouter la relation avec primary_name
                try:
                    cursor.execute("""
                        INSERT INTO relations (person1, person2, relation_type, approved_by)
                        VALUES (?, ?, ?, ?)
                    """, (person1, primary_name, rel_type, updated_by))
                except sqlite3.IntegrityError:
                    # Relation déjà existante, skip
                    pass
            
            # 3. Supprimer toutes les anciennes relations du doublon
            cursor.execute("DELETE FROM relations WHERE person1 = ? OR person2 = ?", 
                         (duplicate_name, duplicate_name))
            
            # 4. Supprimer de pending_relations
            cursor.execute("DELETE FROM pending_relations WHERE person1 = ? OR person2 = ?", 
                         (duplicate_name, duplicate_name))
            
            # 5. Supprimer de persons
            cursor.execute("DELETE FROM persons WHERE name = ?", (duplicate_name,))
            
            conn.commit()
            self.log_action("MERGE_PERSONS", person1=primary_name, person2=duplicate_name,
                          performed_by=updated_by, 
                          details=f"Fusion: {duplicate_name} fusionné dans {primary_name}")
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Erreur lors de la fusion: {e}")
            return False
    
    def delete_person(self, name: str, deleted_by: str = "admin") -> bool:
        """Supprime une personne et toutes ses relations."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Supprimer toutes les relations
            cursor.execute("DELETE FROM relations WHERE person1 = ? OR person2 = ?", (name, name))
            
            # Supprimer de pending_relations
            cursor.execute("DELETE FROM pending_relations WHERE person1 = ? OR person2 = ?", (name, name))
            
            # Supprimer de persons
            cursor.execute("DELETE FROM persons WHERE name = ?", (name,))
            
            conn.commit()
            self.log_action("DELETE_PERSON", person1=name, performed_by=deleted_by,
                          details=f"Personne supprimée avec toutes ses relations")
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Erreur lors de la suppression: {e}")
            return False


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
