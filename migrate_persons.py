#!/usr/bin/env python3
"""
Script de migration pour peupler la table persons avec toutes les personnes 
existantes dans les relations.
"""

from database import RelationDB
from pathlib import Path

def migrate_persons_to_table():
    """Migre toutes les personnes des relations vers la table persons."""
    db = RelationDB()
    
    # Récupérer toutes les personnes uniques des relations
    persons = db.get_all_persons()
    
    print(f"🔍 {len(persons)} personnes trouvées dans les relations")
    
    added_count = 0
    for person_name in persons:
        if db.add_person(person_name):
            added_count += 1
            print(f"  ✅ {person_name}")
        else:
            print(f"  ⏭️  {person_name} (déjà existant)")
    
    print(f"\n✨ {added_count} personnes ajoutées à la table persons")
    
    # Vérification
    detailed_persons = db.get_all_persons_detailed()
    print(f"📊 Total dans la table persons: {len(detailed_persons)}")
    
    return added_count

if __name__ == "__main__":
    migrate_persons_to_table()
