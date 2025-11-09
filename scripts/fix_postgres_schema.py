"""
Script pour corriger le schéma PostgreSQL (ajouter les colonnes manquantes à users)
Usage:
  export DATABASE_URL="postgresql://postgres:e8ZKjjzDvS5Ap48A@xaoectybwqoclobtiwvi.db.eu-central-1.nhost.run:5432/xaoectybwqoclobtiwvi?sslmode=require"
  python scripts/fix_postgres_schema.py
  
Ou avec les variables PG*:
  export PGHOST=xaoectybwqoclobtiwvi.db.eu-central-1.nhost.run
  export PGPORT=5432
  export PGUSER=postgres
  export PGPASSWORD=e8ZKjjzDvS5Ap48A
  export PGDATABASE=xaoectybwqoclobtiwvi
  python scripts/fix_postgres_schema.py
"""
import os
import sys
import urllib.parse

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 n'est pas installé. Installez-le avec: pip install psycopg2-binary")
    sys.exit(1)


def get_database_url():
    """Récupère DATABASE_URL ou construit-la à partir des variables PG*"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    
    # Construire depuis PG*
    host = os.getenv('PGHOST')
    port = os.getenv('PGPORT', '5432')
    user = os.getenv('PGUSER', 'postgres')
    password = os.getenv('PGPASSWORD')
    database = os.getenv('PGDATABASE')
    
    if not (host and database):
        return None
    
    user_enc = urllib.parse.quote_plus(user)
    password_enc = urllib.parse.quote_plus(password) if password else ''
    
    return f"postgresql://{user_enc}:{password_enc}@{host}:{port}/{database}?sslmode=require"


def connect_postgres(database_url):
    """Se connecte à PostgreSQL avec retry"""
    try:
        return psycopg2.connect(database_url)
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        raise


def fix_schema():
    """Corrige le schéma PostgreSQL"""
    database_url = get_database_url()
    if not database_url:
        print("❌ DATABASE_URL introuvable. Définissez DATABASE_URL ou PGHOST/PGDATABASE/etc.")
        sys.exit(1)
    
    print(f"📡 Connexion à PostgreSQL...")
    conn = connect_postgres(database_url)
    
    try:
        cur = conn.cursor()
        
        print("🔧 Création de la table users avec le bon schéma...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        print("🔄 Migration des données depuis la table admins...")
        # Vérifier si la table admins existe
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'admins'
            )
        """)
        admins_exists = cur.fetchone()[0]
        
        if admins_exists:
            cur.execute("""
                INSERT INTO users (username, password_hash, is_admin, created_at, is_active)
                SELECT username, password_hash, TRUE, created_at, TRUE
                FROM admins
                ON CONFLICT (username) DO NOTHING
            """)
            rows_migrated = cur.rowcount
            print(f"✅ {rows_migrated} admin(s) migré(s) vers users")
        else:
            print("ℹ️  Table admins introuvable (peut-être déjà migrée)")
        
        print("🔧 Création de la table pending_accounts...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pending_accounts (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        conn.commit()
        
        # Vérification
        print("\n📊 Vérification des tables:")
        tables = ['users', 'pending_accounts', 'persons', 'relations', 'history']
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"  ✅ {table}: {count} enregistrement(s)")
            except Exception as e:
                print(f"  ⚠️  {table}: {e}")
        
        # Vérifier les colonnes de users
        print("\n📋 Colonnes de la table users:")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        for row in cur.fetchall():
            print(f"  - {row[0]} ({row[1]}) {'NULL' if row[2] == 'YES' else 'NOT NULL'} {f'DEFAULT {row[3]}' if row[3] else ''}")
        
        print("\n✅ Schéma corrigé avec succès!")
        print("\n🚀 Vous pouvez maintenant redéployer l'application sur Render.")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de la correction du schéma: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    try:
        fix_schema()
    except Exception as e:
        print(f"\n💥 Échec: {e}")
        sys.exit(1)
