"""Gestionnaire de base de données centralisé

Prend en charge SQLite par défaut mais peut basculer sur Postgres si
`DATABASE_URL` est présent dans les variables d'environnement (utile pour
Supabase / Heroku / providers SQL managés).
"""

import sqlite3
from pathlib import Path
from typing import Any, List, Tuple, Optional
from contextlib import contextmanager
import config
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Debug: afficher si PostgreSQL est détecté
if DATABASE_URL:
    print(f"🔵 PostgreSQL détecté ! URL: {DATABASE_URL[:50]}...")
else:
    print("⚠️ DATABASE_URL non définie - utilisation de SQLite")

try:
    import psycopg2
    import psycopg2.extras
except Exception:
    psycopg2 = None


class DatabaseManager:
    """Gestionnaire de connexions et transactions pour SQLite ou Postgres"""
    
    def __init__(self, db_path: Path = config.DB_PATH):
        self.db_path = db_path
        self.use_postgres = bool(DATABASE_URL)
        if self.use_postgres and psycopg2 is None:
            raise RuntimeError("DATABASE_URL set but psycopg2 is not installed")
        if not self.use_postgres:
            self._ensure_database_exists()
    
    # ---------- Connections ----------
    def get_connection(self):
        """Retourne une connexion à la base de données (sqlite3 ou psycopg2)
        Note: pour psycopg2 on retourne une connexion avec RealDictCursor
        """
        if self.use_postgres:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
            return conn
        else:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=config.DB_TIMEOUT,
                check_same_thread=config.DB_CHECK_SAME_THREAD
            )
            conn.row_factory = sqlite3.Row
            return conn
    
    @contextmanager
    def transaction(self):
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ---------- Query helpers ----------
    def execute_query(self, query: str, params: Tuple = ()):  # -> List
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
            return rows

    def execute_update(self, query: str, params: Tuple = ()):  # -> int
        with self.transaction() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.rowcount

    def execute_many(self, query: str, params_list: List[Tuple]):
        with self.transaction() as conn:
            cur = conn.cursor()
            cur.executemany(query, params_list)
            return cur.rowcount

    # ---------- SQLite-only helpers ----------
    def _ensure_database_exists(self):
        """Crée la base de données SQLite si elle n'existe pas"""
        if not self.db_path.exists():
            print(f"📁 Création de la base de données: {self.db_path}")
            self._create_tables()
        else:
            print(f"✅ Base de données existante: {self.db_path}")

    def _create_tables(self):
        with self.transaction() as conn:
            cursor = conn.cursor()
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            import hashlib
            password_hash = hashlib.sha256(config.ADMIN_PASSWORD.encode()).hexdigest()
            cursor.execute("""
                INSERT OR IGNORE INTO admins (username, password_hash)
                VALUES (?, ?)
            """, (config.ADMIN_USERNAME, password_hash))
            print("✅ Tables créées avec succès")

    def migrate_from_old_db(self):
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM relations")
            relations_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) as count FROM persons")
            persons_count = cursor.fetchone()[0]
            if relations_count > 0 and persons_count == 0:
                print("🔄 Migration des données en cours...")
                cursor.execute("""
                    SELECT DISTINCT person1 as name FROM relations
                    UNION
                    SELECT DISTINCT person2 as name FROM relations
                """)
                unique_persons = cursor.fetchall()
                for person in unique_persons:
                    cursor.execute("INSERT OR IGNORE INTO persons (name) VALUES (?)", (person[0],))
                print(f"✅ Migration terminée: {len(unique_persons)} personnes migrées")


# Instance globale
db_manager = DatabaseManager()

