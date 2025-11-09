"""
Script pour convertir tous les accès par index row[N] en accès par nom de colonne row['name']
pour compatibilité avec psycopg2 RealDictCursor
"""
import re
from pathlib import Path

# Mapping des index vers les noms de colonnes pour chaque contexte
# Format: (query_pattern, {index: column_name})

# Pour users.py
USERS_MAPPINGS = [
    # get_user_by_id
    {
        'pattern': r'SELECT id, username, password_hash, is_admin, created_at, last_login, is_active\s+FROM users WHERE id',
        'mapping': {0: 'id', 1: 'username', 2: 'password_hash', 3: 'is_admin', 4: 'created_at', 5: 'last_login', 6: 'is_active'}
    },
    # get_all_users
    {
        'pattern': r'SELECT id, username, is_admin, created_at, last_login\s+FROM users WHERE is_active',
        'mapping': {0: 'id', 1: 'username', 2: 'is_admin', 3: 'created_at', 4: 'last_login'}
    },
    # get_pending_accounts (dans admin)
    {
        'pattern': r'SELECT id, username, requested_at\s+FROM pending_accounts',
        'mapping': {0: 'id', 1: 'username', 2: 'requested_at'}
    },
    # get_pending_requests
    {
        'pattern': r'SELECT id, username, requested_at, status\s+FROM pending_accounts',
        'mapping': {0: 'id', 1: 'username', 2: 'requested_at', 3: 'status'}
    }
]

def fix_row_access_in_file(filepath: Path):
    """Convertit les accès row[N] en row['column'] dans un fichier"""
    print(f"\n🔧 Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Convertir row[N] en row['column'] 
    # Cette regex capture row[digit] et on doit le remplacer contextuellement
    # Stratégie: identifier les blocs de code et mapper
    
    # Plus simple: remplacer tous les patterns row[0-9] par un placeholder
    # puis analyser le contexte
    
    # En fait, faisons simple: remplacer manuellement les patterns connus
    replacements = [
        # users.py - get_user_by_id (7 colonnes)
        (r"'id': row\[0\],\s+'username': row\[1\],\s+'password_hash': row\[2\],\s+'is_admin': bool\(row\[3\]\),\s+'created_at': row\[4\],\s+'last_login': row\[5\],\s+'is_active': bool\(row\[6\]\)",
         "'id': row['id'],\n                'username': row['username'],\n                'password_hash': row['password_hash'],\n                'is_admin': bool(row['is_admin']),\n                'created_at': row['created_at'],\n                'last_login': row['last_login'],\n                'is_active': bool(row['is_active'])"),
        
        # users.py - get_all_users (5 colonnes)
        (r"'id': row\[0\],\s+'username': row\[1\],\s+'is_admin': bool\(row\[2\]\),\s+'created_at': row\[3\],\s+'last_login': row\[4\]",
         "'id': row['id'],\n                'username': row['username'],\n                'is_admin': bool(row['is_admin']),\n                'created_at': row['created_at'],\n                'last_login': row['last_login']"),
        
        # Pending accounts (3 colonnes)
        (r"'id': row\[0\],\s+'username': row\[1\],\s+'requested_at': row\[2\]",
         "'id': row['id'],\n                    'username': row['username'],\n                    'requested_at': row['requested_at']"),
        
        # Pending requests (4 colonnes)
        (r"'id': row\[0\],\s+'username': row\[1\],\s+'requested_at': row\[2\],\s+'status': row\[3\]",
         "'id': row['id'],\n                'username': row['username'],\n                'requested_at': row['requested_at'],\n                'status': row['status']"),
        
        # RETURNING id - fetchone()[0]
        (r"user_id = cur\.fetchone\(\)\[0\]",
         "user_id = cur.fetchone()['id']"),
        (r"request_id = cur\.fetchone\(\)\[0\]",
         "request_id = cur.fetchone()['id']"),
        (r"submission_id = cur\.fetchone\(\)\[0\]",
         "submission_id = cur.fetchone()['id']"),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.MULTILINE)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {filepath}")
        return True
    else:
        print(f"⏭️  No changes needed: {filepath}")
        return False

if __name__ == '__main__':
    database_dir = Path('/Users/diegoclaes/Code/Relation/database')
    files_to_fix = [
        database_dir / 'users.py',
        database_dir / 'pending_submissions.py',
        database_dir / 'persons.py',
        database_dir / 'relations.py',
        database_dir / 'audit.py'
    ]
    
    fixed_count = 0
    for filepath in files_to_fix:
        if filepath.exists():
            if fix_row_access_in_file(filepath):
                fixed_count += 1
    
    print(f"\n✅ Done! Fixed {fixed_count} files")
