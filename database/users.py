"""
User Management Repository
Gère les utilisateurs et l'authentification
"""

from typing import Optional, List, Dict
import sqlite3
from datetime import datetime
import hashlib
import secrets
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "social_network.db"


class UserRepository:
    """Repository pour gérer les utilisateurs"""
    
    @staticmethod
    def init_tables():
        """Initialise les tables users"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Table des utilisateurs
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Table des demandes de compte en attente
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pending_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                requested_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash un mot de passe avec SHA-256 + salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Vérifie un mot de passe"""
        try:
            salt, pwd_hash = password_hash.split('$')
            return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
        except:
            return False
    
    @staticmethod
    def create_user(username: str, password: str, is_admin: bool = False) -> Optional[int]:
        """Crée un nouvel utilisateur"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            password_hash = UserRepository.hash_password(password)
            now = datetime.now().isoformat()
            
            cur.execute("""
                INSERT INTO users (username, password_hash, is_admin, created_at, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (username, password_hash, 1 if is_admin else 0, now))
            
            user_id = cur.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:
        """Récupère un utilisateur par username"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, username, password_hash, is_admin, created_at, last_login, is_active
            FROM users WHERE username = ? AND is_active = 1
        """, (username,))
        
        row = cur.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'password_hash': row[2],
                'is_admin': bool(row[3]),
                'created_at': row[4],
                'last_login': row[5],
                'is_active': bool(row[6])
            }
        return None
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict]:
        """Authentifie un utilisateur"""
        user = UserRepository.get_user_by_username(username)
        if user and UserRepository.verify_password(password, user['password_hash']):
            # Update last login
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE users SET last_login = ? WHERE id = ?
            """, (datetime.now().isoformat(), user['id']))
            conn.commit()
            conn.close()
            
            return user
        return None
    
    @staticmethod
    def get_all_users() -> List[Dict]:
        """Récupère tous les utilisateurs actifs"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, username, is_admin, created_at, last_login
            FROM users WHERE is_active = 1
            ORDER BY created_at DESC
        """)
        
        users = []
        for row in cur.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'is_admin': bool(row[2]),
                'created_at': row[3],
                'last_login': row[4]
            })
        
        conn.close()
        return users
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Désactive un utilisateur (soft delete)"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False


class PendingAccountRepository:
    """Repository pour gérer les demandes de compte en attente"""
    
    @staticmethod
    def create_request(username: str, password: str) -> Optional[int]:
        """Crée une demande de compte"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            password_hash = UserRepository.hash_password(password)
            now = datetime.now().isoformat()
            
            cur.execute("""
                INSERT INTO pending_accounts (username, password_hash, requested_at, status)
                VALUES (?, ?, ?, 'pending')
            """, (username, password_hash, now))
            
            request_id = cur.lastrowid
            conn.commit()
            conn.close()
            return request_id
        except sqlite3.IntegrityError:
            return None
    
    @staticmethod
    def get_pending_requests() -> List[Dict]:
        """Récupère toutes les demandes en attente"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, username, requested_at, status
            FROM pending_accounts WHERE status = 'pending'
            ORDER BY requested_at DESC
        """)
        
        requests = []
        for row in cur.fetchall():
            requests.append({
                'id': row[0],
                'username': row[1],
                'requested_at': row[2],
                'status': row[3]
            })
        
        conn.close()
        return requests
    
    @staticmethod
    def approve_request(request_id: int) -> bool:
        """Approuve une demande et crée l'utilisateur"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Récupérer la demande
            cur.execute("""
                SELECT username, password_hash FROM pending_accounts 
                WHERE id = ? AND status = 'pending'
            """, (request_id,))
            
            row = cur.fetchone()
            if not row:
                conn.close()
                return False
            
            username, password_hash = row
            now = datetime.now().isoformat()
            
            # Créer l'utilisateur
            cur.execute("""
                INSERT INTO users (username, password_hash, is_admin, created_at, is_active)
                VALUES (?, ?, 0, ?, 1)
            """, (username, password_hash, now))
            
            # Marquer la demande comme approuvée
            cur.execute("""
                UPDATE pending_accounts SET status = 'approved' WHERE id = ?
            """, (request_id,))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    @staticmethod
    def reject_request(request_id: int) -> bool:
        """Rejette une demande"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE pending_accounts SET status = 'rejected' WHERE id = ?
            """, (request_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False


# Initialiser les tables au chargement du module
UserRepository.init_tables()

# Créer un admin par défaut si aucun utilisateur n'existe
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM users")
if cur.fetchone()[0] == 0:
    # Créer admin par défaut : admin / admin123
    UserRepository.create_user("admin", "admin123", is_admin=True)
    print("✅ Admin par défaut créé : admin / admin123")
conn.close()


# Export
user_repository = UserRepository()
pending_account_repository = PendingAccountRepository()
