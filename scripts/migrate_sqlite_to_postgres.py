"""
Script minimal pour migrer les données principales de SQLite vers Postgres (Nhost)
Usage:
  export PGHOST=... PGPORT=... PGUSER=... PGPASSWORD=... PGDATABASE=...
  python scripts/migrate_sqlite_to_postgres.py --sqlite-db ./social_network.db

ATTENTION: Ce script est un point de départ. Testez sur une DB de staging d'abord.
"""
import argparse
import sqlite3
import os
import sys
import urllib.parse

try:
    import psycopg2
except ImportError:
    print("psycopg2 n'est pas installé. Installez psycopg2-binary dans votre env.")
    sys.exit(1)


def _build_database_url_from_env():
    """Construit une DATABASE_URL à partir de variables PG* si présentes."""
    user = os.getenv('PGUSER') or os.getenv('PG_USER')
    password = os.getenv('PGPASSWORD') or os.getenv('PG_PASS')
    host = os.getenv('PGHOST') or os.getenv('PG_HOST')
    port = os.getenv('PGPORT') or os.getenv('PG_PORT')
    db = os.getenv('PGDATABASE') or os.getenv('PG_DB')
    if not (host and db):
        return None
    user = user or 'postgres'
    user_enc = urllib.parse.quote_plus(user)
    password_enc = urllib.parse.quote_plus(password) if password else ''
    netloc = f"{user_enc}:{password_enc}@{host}"
    if port:
        netloc += f":{port}"
    return f"postgresql://{netloc}/{db}"


def _connect_with_retry(database_url):
    """Tente plusieurs stratégies de connexion pour contourner problèmes d'encoding / SSL."""
    # 1) Essai direct
    try:
        return psycopg2.connect(database_url)
    except Exception as e:
        # 2) Essayer avec sslmode=require si absent
        try:
            if database_url and 'sslmode' not in database_url:
                sep = '&' if '?' in database_url else '?'
                url_ssl = database_url + sep + 'sslmode=require'
                print('Première tentative échouée, ré-essai avec sslmode=require...')
                return psycopg2.connect(url_ssl)
        except Exception:
            pass

        # 3) Essayer d'encoder userinfo (si mot de passe contient des caractères spéciaux)
        try:
            if database_url and '@' in database_url:
                userinfo, hostpart = database_url.split('@', 1)
                if '//' in userinfo:
                    userinfo = userinfo.split('//', 1)[1]
                if ':' in userinfo:
                    user, password = userinfo.split(':', 1)
                else:
                    user, password = userinfo, None
                user_enc = urllib.parse.quote_plus(user)
                password_enc = urllib.parse.quote_plus(password) if password else ''
                rebuilt = f"postgresql://{user_enc}:{password_enc}@{hostpart}"
                print('Ré-essai de connexion en encodant userinfo...')
                # ajouter sslmode si nécessaire
                if 'sslmode' not in rebuilt:
                    sep = '&' if '?' in rebuilt else '?'
                    rebuilt = rebuilt + sep + 'sslmode=require'
                return psycopg2.connect(rebuilt)
        except Exception:
            pass

        # 4) Dernier recours: connexion via variables PG* séparées (host, user, password, dbname)
        try:
            host = os.getenv('PGHOST') or os.getenv('PG_HOST')
            port = int(os.getenv('PGPORT') or os.getenv('PG_PORT') or 5432)
            user = os.getenv('PGUSER') or os.getenv('PG_USER') or 'postgres'
            password = os.getenv('PGPASSWORD') or os.getenv('PG_PASS')
            dbname = os.getenv('PGDATABASE') or os.getenv('PG_DB')
            if host and dbname:
                print('Dernier essai: connexion directe avec PGHOST/PGUSER/PGPASSWORD (sslmode=require)...')
                return psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname, sslmode='require')
        except Exception:
            pass

        # re-raise original error
        raise e


def migrer(sqlite_path, database_url=None):
    print(f"Connexion SQLite: {sqlite_path}")
    if not database_url:
        database_url = os.getenv('DATABASE_URL') or _build_database_url_from_env()
    if not database_url:
        raise RuntimeError('DATABASE_URL introuvable. Définissez DATABASE_URL ou PGHOST/PGDATABASE etc.')
    print(f"Connexion Postgres: {database_url}")

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    try:
        pg_conn = _connect_with_retry(database_url)
    except Exception as e:
        print(f"ERREUR: impossible de se connecter à Postgres: {e}")
        raise

    with sqlite_conn, pg_conn:
        s_cur = sqlite_conn.cursor()
        p_cur = pg_conn.cursor()

        # Persons
        s_cur.execute("SELECT id, name, gender, sexual_orientation, created_at, updated_at FROM persons")
        persons = s_cur.fetchall()
        print(f"{len(persons)} personnes à migrer")

        p_cur.execute("CREATE TABLE IF NOT EXISTS persons (id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL, gender TEXT, sexual_orientation TEXT, created_at TIMESTAMP, updated_at TIMESTAMP)")
        for row in persons:
            p_cur.execute("INSERT INTO persons (name, gender, sexual_orientation, created_at, updated_at) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (name) DO NOTHING",
                          (row['name'], row['gender'], row['sexual_orientation'], row['created_at'], row['updated_at']))

        # Relations
        s_cur.execute("SELECT id, person1, person2, relation_type, created_at FROM relations")
        relations = s_cur.fetchall()
        print(f"{len(relations)} relations à migrer")
        p_cur.execute("CREATE TABLE IF NOT EXISTS relations (id SERIAL PRIMARY KEY, person1 TEXT NOT NULL, person2 TEXT NOT NULL, relation_type INTEGER, created_at TIMESTAMP)")
        for row in relations:
            p_cur.execute("INSERT INTO relations (person1, person2, relation_type, created_at) VALUES (%s,%s,%s,%s)", (row['person1'], row['person2'], row['relation_type'], row['created_at']))

        # History
        s_cur.execute("SELECT id, action_type, person1, person2, relation_type, performed_by, details, created_at FROM history")
        history = s_cur.fetchall()
        print(f"{len(history)} historiques à migrer")
        p_cur.execute("CREATE TABLE IF NOT EXISTS history (id SERIAL PRIMARY KEY, action_type TEXT, person1 TEXT, person2 TEXT, relation_type INTEGER, performed_by TEXT, details TEXT, created_at TIMESTAMP)")
        for row in history:
            p_cur.execute("INSERT INTO history (action_type, person1, person2, relation_type, performed_by, details, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                          (row['action_type'], row['person1'], row['person2'], row['relation_type'], row['performed_by'], row['details'], row['created_at']))

        # Admins (si présents)
        try:
            s_cur.execute("SELECT id, username, password_hash, created_at FROM admins")
            admins = s_cur.fetchall()
            if admins:
                print(f"{len(admins)} admins à migrer")
                p_cur.execute("CREATE TABLE IF NOT EXISTS admins (id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TIMESTAMP)")
                for row in admins:
                    p_cur.execute("INSERT INTO admins (username, password_hash, created_at) VALUES (%s,%s,%s) ON CONFLICT (username) DO NOTHING",
                                  (row['username'], row['password_hash'], row['created_at']))
        except sqlite3.OperationalError:
            # table admins may not exist in older dbs
            pass

        pg_conn.commit()
        print("✅ Migration terminée")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sqlite-db', default='./social_network.db')
    args = parser.parse_args()

    try:
        migrer(args.sqlite_db, os.getenv('DATABASE_URL'))
    except Exception as e:
        print(f"Migration échouée: {e}")
        sys.exit(1)
