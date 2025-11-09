#!/usr/bin/env python3
"""
Script pour vérifier le schéma actuel de la base de données Render PostgreSQL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Récupérer l'URL de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set. Please run:")
    print("   export DATABASE_URL='your_render_postgres_url'")
    exit(1)

print(f"🔍 Connecting to database...")

try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    print("\n" + "="*70)
    print("📊 CURRENT DATABASE SCHEMA")
    print("="*70 + "\n")
    
    # Liste des tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    
    tables = [row['table_name'] for row in cur.fetchall()]
    
    print(f"📋 Tables found: {len(tables)}")
    for table in tables:
        print(f"   - {table}")
    
    print("\n" + "="*70 + "\n")
    
    # Pour chaque table, afficher les colonnes
    for table in tables:
        print(f"📦 Table: {table}")
        print("-" * 70)
        
        cur.execute(f"""
            SELECT 
                column_name, 
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = '{table}'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        
        print(f"{'Column':<30} {'Type':<20} {'Nullable':<10} {'Default':<20}")
        print(f"{'-'*30} {'-'*20} {'-'*10} {'-'*20}")
        
        for col in columns:
            default = str(col['column_default'])[:20] if col['column_default'] else ''
            print(f"{col['column_name']:<30} {col['data_type']:<20} {col['is_nullable']:<10} {default:<20}")
        
        # Compter les enregistrements
        cur.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cur.fetchone()['count']
        print(f"\n📊 Records: {count}\n")
    
    print("="*70)
    print("✅ SCHEMA VERIFICATION COMPLETE")
    print("="*70)
    
    # Vérifications critiques
    print("\n🔍 CRITICAL CHECKS:\n")
    
    # Check 1: Table relations - person1/person2 vs person1_id/person2_id
    if 'relations' in tables:
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'relations' 
            AND column_name IN ('person1', 'person2', 'person1_id', 'person2_id')
        """)
        rel_cols = [row['column_name'] for row in cur.fetchall()]
        
        if 'person1' in rel_cols and 'person2' in rel_cols:
            print("✅ Table 'relations' uses TEXT columns (person1, person2) - CORRECT")
        elif 'person1_id' in rel_cols and 'person2_id' in rel_cols:
            print("❌ Table 'relations' uses INTEGER columns (person1_id, person2_id) - INCOMPATIBLE WITH CODE")
            print("   👉 Need to migrate to use TEXT columns")
        else:
            print("⚠️  Table 'relations' has unexpected column structure")
    
    # Check 2: Table pending_persons - name vs person_name
    if 'pending_persons' in tables:
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'pending_persons' 
            AND column_name IN ('name', 'person_name')
        """)
        pp_cols = [row['column_name'] for row in cur.fetchall()]
        
        if 'person_name' in pp_cols:
            print("✅ Table 'pending_persons' uses 'person_name' column - CORRECT (code adapted)")
        elif 'name' in pp_cols:
            print("⚠️  Table 'pending_persons' uses 'name' column - Code expects 'person_name'")
        else:
            print("❌ Table 'pending_persons' missing name column")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
