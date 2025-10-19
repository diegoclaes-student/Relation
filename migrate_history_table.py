#!/usr/bin/env python3
"""
Migration script to add status columns to history table
"""

import sqlite3
from config import DB_PATH

def migrate():
    """Add status, cancelled_at, cancelled_by columns to history table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"Colonnes actuelles: {columns}")
        
        # Add status column if not exists
        if 'status' not in columns:
            print("Ajout de la colonne 'status'...")
            cursor.execute("""
                ALTER TABLE history 
                ADD COLUMN status TEXT DEFAULT 'active'
            """)
            print("✅ Colonne 'status' ajoutée")
        
        # Add cancelled_at column if not exists
        if 'cancelled_at' not in columns:
            print("Ajout de la colonne 'cancelled_at'...")
            cursor.execute("""
                ALTER TABLE history 
                ADD COLUMN cancelled_at TIMESTAMP
            """)
            print("✅ Colonne 'cancelled_at' ajoutée")
        
        # Add cancelled_by column if not exists
        if 'cancelled_by' not in columns:
            print("Ajout de la colonne 'cancelled_by'...")
            cursor.execute("""
                ALTER TABLE history 
                ADD COLUMN cancelled_by TEXT
            """)
            print("✅ Colonne 'cancelled_by' ajoutée")
        
        # Add old_value and new_value for tracking changes
        if 'old_value' not in columns:
            print("Ajout de la colonne 'old_value'...")
            cursor.execute("""
                ALTER TABLE history 
                ADD COLUMN old_value TEXT
            """)
            print("✅ Colonne 'old_value' ajoutée")
        
        if 'new_value' not in columns:
            print("Ajout de la colonne 'new_value'...")
            cursor.execute("""
                ALTER TABLE history 
                ADD COLUMN new_value TEXT
            """)
            print("✅ Colonne 'new_value' ajoutée")
        
        # Add entity_type and entity_id for better tracking
        if 'entity_type' not in columns:
            print("Ajout de la colonne 'entity_type'...")
            cursor.execute("""
                ALTER TABLE history 
                ADD COLUMN entity_type TEXT
            """)
            print("✅ Colonne 'entity_type' ajoutée")
        
        if 'entity_id' not in columns:
            print("Ajout de la colonne 'entity_id'...")
            cursor.execute("""
                ALTER TABLE history 
                ADD COLUMN entity_id INTEGER
            """)
            print("✅ Colonne 'entity_id' ajoutée")
        
        if 'entity_name' not in columns:
            print("Ajout de la colonne 'entity_name'...")
            cursor.execute("""
                ALTER TABLE history 
                ADD COLUMN entity_name TEXT
            """)
            print("✅ Colonne 'entity_name' ajoutée")
        
        conn.commit()
        
        # Display final structure
        cursor.execute("PRAGMA table_info(history)")
        print("\n📋 Structure finale de la table history:")
        for row in cursor.fetchall():
            print(f"   {row[1]:20s} {row[2]:10s} {'' if row[3] else 'NULL':5s} {row[4] if row[4] else ''}")
        
        print("\n✅ Migration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
