"""
Script de migration SQLite → PostgreSQL pour Supabase

Ce script exporte toutes les données de SQLite vers PostgreSQL
"""

import sqlite3
import os
import psycopg2
from datetime import datetime

# Configuration
SQLITE_DB = 'social_network.db'
POSTGRES_URL = os.environ.get('DATABASE_URL')  # À configurer avec ton URL Supabase

def export_sqlite_data():
    """Exporter toutes les données de SQLite"""
    print("📊 Lecture des données SQLite...")
    
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    data = {}
    
    # Personnes
    cur.execute("SELECT * FROM persons")
    data['persons'] = [dict(row) for row in cur.fetchall()]
    print(f"✅ {len(data['persons'])} personnes exportées")
    
    # Relations
    cur.execute("SELECT * FROM relations")
    data['relations'] = [dict(row) for row in cur.fetchall()]
    print(f"✅ {len(data['relations'])} relations exportées")
    
    # Utilisateurs
    cur.execute("SELECT * FROM users")
    data['users'] = [dict(row) for row in cur.fetchall()]
    print(f"✅ {len(data['users'])} utilisateurs exportés")
    
    # Comptes en attente
    cur.execute("SELECT * FROM pending_accounts")
    data['pending_accounts'] = [dict(row) for row in cur.fetchall()]
    print(f"✅ {len(data['pending_accounts'])} comptes en attente exportés")
    
    # Personnes en attente
    cur.execute("SELECT * FROM pending_persons")
    data['pending_persons'] = [dict(row) for row in cur.fetchall()]
    print(f"✅ {len(data['pending_persons'])} personnes en attente exportées")
    
    # Relations en attente
    cur.execute("SELECT * FROM pending_relations")
    data['pending_relations'] = [dict(row) for row in cur.fetchall()]
    print(f"✅ {len(data['pending_relations'])} relations en attente exportées")
    
    conn.close()
    return data

def import_to_postgres(data):
    """Importer les données dans PostgreSQL"""
    if not POSTGRES_URL:
        print("❌ ERREUR: DATABASE_URL non configuré")
        print("👉 Exporte-le : export DATABASE_URL='postgresql://...'")
        return
    
    print("\n🚀 Import dans PostgreSQL...")
    
    # Connexion
    conn = psycopg2.connect(POSTGRES_URL)
    cur = conn.cursor()
    
    try:
        # 1. Personnes
        print("📝 Import des personnes...")
        for person in data['persons']:
            cur.execute(
                "INSERT INTO persons (id, name, created_at) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (person['id'], person['name'], person.get('created_at', datetime.now()))
            )
        conn.commit()
        print(f"✅ {len(data['persons'])} personnes importées")
        
        # 2. Relations
        print("📝 Import des relations...")
        for relation in data['relations']:
            cur.execute(
                "INSERT INTO relations (id, person1_id, person2_id, relation_type, created_at) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (relation['id'], relation['person1_id'], relation['person2_id'], 
                 relation['relation_type'], relation.get('created_at', datetime.now()))
            )
        conn.commit()
        print(f"✅ {len(data['relations'])} relations importées")
        
        # 3. Utilisateurs
        print("📝 Import des utilisateurs...")
        for user in data['users']:
            cur.execute(
                "INSERT INTO users (id, username, password_hash, role, created_at) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
                (user['id'], user['username'], user['password_hash'], 
                 user['role'], user.get('created_at', datetime.now()))
            )
        conn.commit()
        print(f"✅ {len(data['users'])} utilisateurs importés")
        
        # 4. Comptes en attente
        print("📝 Import des comptes en attente...")
        for acc in data['pending_accounts']:
            cur.execute(
                "INSERT INTO pending_accounts (id, username, password_hash, submitted_at, status) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (acc['id'], acc['username'], acc['password_hash'], 
                 acc.get('submitted_at', datetime.now()), acc.get('status', 'pending'))
            )
        conn.commit()
        print(f"✅ {len(data['pending_accounts'])} comptes en attente importés")
        
        # 5. Personnes en attente
        print("📝 Import des personnes en attente...")
        for person in data['pending_persons']:
            cur.execute(
                "INSERT INTO pending_persons (id, person_name, submitted_by, submitted_at, status) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (person['id'], person['person_name'], person['submitted_by'],
                 person.get('submitted_at', datetime.now()), person.get('status', 'pending'))
            )
        conn.commit()
        print(f"✅ {len(data['pending_persons'])} personnes en attente importées")
        
        # 6. Relations en attente
        print("📝 Import des relations en attente...")
        for rel in data['pending_relations']:
            cur.execute(
                "INSERT INTO pending_relations (id, person1, person2, relation_type, submitted_by, submitted_at, status) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (rel['id'], rel['person1'], rel['person2'], rel['relation_type'],
                 rel['submitted_by'], rel.get('submitted_at', datetime.now()), rel.get('status', 'pending'))
            )
        conn.commit()
        print(f"✅ {len(data['pending_relations'])} relations en attente importées")
        
        # Réinitialiser les séquences PostgreSQL
        print("\n🔄 Réinitialisation des séquences...")
        cur.execute("SELECT setval('persons_id_seq', (SELECT MAX(id) FROM persons))")
        cur.execute("SELECT setval('relations_id_seq', (SELECT MAX(id) FROM relations))")
        cur.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))")
        cur.execute("SELECT setval('pending_accounts_id_seq', (SELECT MAX(id) FROM pending_accounts))")
        cur.execute("SELECT setval('pending_persons_id_seq', (SELECT MAX(id) FROM pending_persons))")
        cur.execute("SELECT setval('pending_relations_id_seq', (SELECT MAX(id) FROM pending_relations))")
        conn.commit()
        print("✅ Séquences réinitialisées")
        
        print("\n🎉 Migration réussie !")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'import: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("🔄 MIGRATION SQLITE → POSTGRESQL")
    print("=" * 60)
    print()
    
    # Vérifier que SQLite existe
    if not os.path.exists(SQLITE_DB):
        print(f"❌ ERREUR: {SQLITE_DB} introuvable")
        exit(1)
    
    # Exporter
    data = export_sqlite_data()
    
    # Importer
    import_to_postgres(data)
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION TERMINÉE")
    print("=" * 60)
    print("\nProchaines étapes:")
    print("1. Vérifie les données sur Supabase Dashboard")
    print("2. Teste l'application avec DATABASE_URL configuré")
    print("3. Déploie sur Vercel")
