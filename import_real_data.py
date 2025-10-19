#!/usr/bin/env python3
"""
Import des vraies données depuis relations.csv avec symétrie garantie 100%
"""

import sqlite3
import csv
import os
from datetime import datetime
from pathlib import Path

DB_PATH = "/Users/diegoclaes/Code/Relation/social_network.db"
CSV_PATH = "/Users/diegoclaes/Code/Relation/relations.csv"

def clear_database():
    """Vider la DB de test"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Vider les tables
    cursor.execute("DELETE FROM relations")
    cursor.execute("DELETE FROM pending_relations")
    cursor.execute("DELETE FROM persons")
    cursor.execute("DELETE FROM history")
    
    conn.commit()
    conn.close()
    print("✅ Base de données vidée")

def extract_persons_from_csv():
    """Extraire tous les noms uniques du CSV"""
    persons = set()
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 2:
                persons.add(row[0].strip())
                persons.add(row[1].strip())
    
    return sorted(list(persons))

def import_persons(persons):
    """Insérer les personnes dans la DB"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for person in persons:
        try:
            cursor.execute(
                "INSERT INTO persons (name, gender, sexual_orientation, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (person, None, None, datetime.now(), datetime.now())
            )
        except sqlite3.IntegrityError:
            # Person already exists
            pass
    
    conn.commit()
    conn.close()
    print(f"✅ {len(persons)} personnes importées")

def import_relations_with_symmetry():
    """Importer les relations avec symétrie garantie"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    relations_set = set()  # Pour éviter les doublons
    count = 0
    skip_header = True
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            # Skip le header
            if skip_header:
                skip_header = False
                continue
                
            if len(row) < 3:
                continue
            
            try:
                person1 = row[0].strip()
                person2 = row[1].strip()
                relation_type = int(row[2].strip())
            except (ValueError, IndexError):
                continue
            
            # Normaliser la relation pour garantir l'unicité
            # On crée une paire ordonnée pour éviter (A->B, B->A)
            pair = tuple(sorted([person1, person2]))
            
            if pair not in relations_set:
                relations_set.add(pair)
                
                # Insérer dans les deux directions (symétrique)
                try:
                    cursor.execute(
                        "INSERT INTO relations (person1, person2, relation_type, created_at) VALUES (?, ?, ?, ?)",
                        (person1, person2, relation_type, datetime.now())
                    )
                    count += 1
                except sqlite3.IntegrityError:
                    pass
                
                try:
                    cursor.execute(
                        "INSERT INTO relations (person1, person2, relation_type, created_at) VALUES (?, ?, ?, ?)",
                        (person2, person1, relation_type, datetime.now())
                    )
                    count += 1
                except sqlite3.IntegrityError:
                    pass
    
    conn.commit()
    conn.close()
    print(f"✅ {count} relations symétrisées importées")

def verify_symmetry():
    """Vérifier que la symétrie est garantie"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as total_relations FROM relations
    """)
    total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) as asymmetric FROM relations r1
        WHERE NOT EXISTS (
            SELECT 1 FROM relations r2
            WHERE r1.person1 = r2.person2
            AND r1.person2 = r2.person1
            AND r1.relation_type = r2.relation_type
        )
    """)
    asymmetric = cursor.fetchone()[0]
    
    conn.close()
    
    if asymmetric == 0:
        print(f"✅ SYMÉTRIE GARANTIE 100%! {total} relations symétriques")
        return True
    else:
        print(f"❌ ATTENTION: {asymmetric} relations asymétriques détectées!")
        return False

def get_stats():
    """Afficher les statistiques"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM persons")
    persons_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) / 2 FROM relations")  # Divisé par 2 car symétrique
    relations_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 STATISTIQUES:")
    print(f"  👥 Personnes: {persons_count}")
    print(f"  🔗 Relations: {relations_count}")

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 IMPORT DES VRAIES DONNÉES AVEC SYMÉTRIE GARANTIE")
    print("=" * 70)
    
    # 1. Vider la DB
    clear_database()
    
    # 2. Extraire les personnes
    print("\n📥 Extraction des personnes...")
    persons = extract_persons_from_csv()
    print(f"   Trouvé {len(persons)} personnes uniques")
    
    # 3. Importer les personnes
    print("\n👥 Import des personnes...")
    import_persons(persons)
    
    # 4. Importer les relations avec symétrie
    print("\n🔗 Import des relations...")
    import_relations_with_symmetry()
    
    # 5. Vérifier la symétrie
    print("\n✔️  Vérification de la symétrie...")
    verify_symmetry()
    
    # 6. Stats
    get_stats()
    
    print("\n" + "=" * 70)
    print("✅ IMPORT TERMINÉ AVEC SUCCÈS!")
    print("=" * 70)
