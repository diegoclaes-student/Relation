"""
Script minimal pour migrer les données principales de SQLite vers Postgres (Supabase)
Usage:
  export DATABASE_URL='postgres://user:pass@host:5432/dbname'
  python scripts/migrate_sqlite_to_postgres.py --sqlite-db ./social_network.db

ATTENTION: Ce script est un point de départ. Testez sur une DB de staging d'abord.
"""
import argparse
import sqlite3
import os
import sys

try:
    import psycopg2
except ImportError:
    print("psycopg2 n'est pas installé. Installez psycopg2-binary dans votre env.")
    sys.exit(1)


def migrer(sqlite_path, database_url):
    print(f"Connexion SQLite: {sqlite_path}")
    print(f"Connexion Postgres: {database_url}")

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = psycopg2.connect(database_url)

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

        pg_conn.commit()
        print("✅ Migration terminée")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sqlite-db', default='./social_network.db')
    args = parser.parse_args()

    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print('ERREUR: Définissez la variable d\'environnement DATABASE_URL (ex: postgres://user:pass@host:5432/db)')
        sys.exit(1)

    migrer(args.sqlite_db, DATABASE_URL)
