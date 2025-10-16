"""Gestionnaire de base de données centralisé"""

import sqlite3
from pathlib import Path
from typing import Any, List, Tuple, Optional
from contextlib import contextmanager
import config


class DatabaseManager:
    """Gestionnaire de connexions et transactions SQLite"""
    
    def __init__(self, db_path: Path = config.DB_PATH):
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Crée la base de données si elle n'existe pas"""
        if not self.db_path.exists():
            print(f"📁 Création de la base de données: {self.db_path}")
            self._create_tables()
        else:
            print(f"✅ Base de données existante: {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Retourne une connexion à la base de données"""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=config.DB_TIMEOUT,
            check_same_thread=config.DB_CHECK_SAME_THREAD
        )
        conn.row_factory = sqlite3.Row
        return conn
    
    @contextmanager
    def transaction(self):
        """Context manager pour les transactions"""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Exécute une requête SELECT et retourne les résultats"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Exécute une requête INSERT/UPDATE/DELETE et retourne le nombre de lignes affectées"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Exécute une requête avec plusieurs ensembles de paramètres"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def _create_tables(self):
        """Crée toutes les tables nécessaires"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # Table persons (nouvelle structure enrichie)
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
            
            # Table relations (avec symétrie intégrée)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person1 TEXT NOT NULL,
                    person2 TEXT NOT NULL,
                    relation_type INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(person1, person2, relation_type)
                )
            """)
            
            # Table pending_relations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person1 TEXT NOT NULL,
                    person2 TEXT NOT NULL,
                    relation_type INTEGER DEFAULT 0,
                    submitted_by TEXT DEFAULT 'anonymous',
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    UNIQUE(person1, person2, relation_type)
                )
            """)
            
            # Table history (historique des actions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT NOT NULL,
                    person1 TEXT,
                    person2 TEXT,
                    relation_type INTEGER,
                    performed_by TEXT DEFAULT 'system',
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table admins
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ajouter admin par défaut si n'existe pas
            import hashlib
            password_hash = hashlib.sha256(config.ADMIN_PASSWORD.encode()).hexdigest()
            cursor.execute("""
                INSERT OR IGNORE INTO admins (username, password_hash)
                VALUES (?, ?)
            """, (config.ADMIN_USERNAME, password_hash))
            
            print("✅ Tables créées avec succès")
    
    def migrate_from_old_db(self):
        """Migre les données de l'ancienne structure si nécessaire"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # Vérifier si migration nécessaire
            cursor.execute("""
                SELECT COUNT(*) as count FROM relations
            """)
            relations_count = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT COUNT(*) as count FROM persons
            """)
            persons_count = cursor.fetchone()['count']
            
            # Si relations existe mais persons est vide, migrer
            if relations_count > 0 and persons_count == 0:
                print("🔄 Migration des données en cours...")
                
                # Extraire tous les noms uniques des relations
                cursor.execute("""
                    SELECT DISTINCT person1 as name FROM relations
                    UNION
                    SELECT DISTINCT person2 as name FROM relations
                """)
                
                unique_persons = cursor.fetchall()
                
                # Insérer dans la table persons
                for person in unique_persons:
                    cursor.execute("""
                        INSERT OR IGNORE INTO persons (name)
                        VALUES (?)
                    """, (person['name'],))
                
                print(f"✅ Migration terminée: {len(unique_persons)} personnes migrées")


# Instance globale
db_manager = DatabaseManager()
