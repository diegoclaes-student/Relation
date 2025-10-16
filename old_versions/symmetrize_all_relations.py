#!/usr/bin/env python3
"""
Script automatique pour symétriser TOUTES les relations asymétriques.
Ajoute automatiquement les relations inverses manquantes dans la base de données.

ATTENTION: Ce script modifie la base de données !
"""

from database import RelationDB
from graph import detect_gender
import sqlite3

def symmetrize_all_relations(dry_run=True):
    """
    Symétriser automatiquement toutes les relations.
    
    Args:
        dry_run (bool): Si True, affiche ce qui serait fait sans modifier la DB.
                       Si False, applique réellement les modifications.
    """
    db = RelationDB()
    relations = db.get_all_relations()
    
    # Créer un dictionnaire des relations existantes
    existing_relations = set()
    relations_dict = {}
    
    for p1, p2, rel_type in relations:
        existing_relations.add((p1, p2))
        if p1 not in relations_dict:
            relations_dict[p1] = []
        relations_dict[p1].append((p2, rel_type))
    
    print("\n" + "="*80)
    print("🔄 SYMÉTRISATION AUTOMATIQUE DES RELATIONS")
    print("="*80)
    
    if dry_run:
        print("\n⚠️  MODE SIMULATION (DRY RUN) - Aucune modification ne sera appliquée")
        print("   Pour appliquer les changements, relancez avec --apply\n")
    else:
        print("\n✅ MODE APPLICATION - Les relations vont être ajoutées à la base de données\n")
    
    # Détecter les relations asymétriques et préparer les ajouts
    relations_to_add = []
    
    for person1, targets in relations_dict.items():
        for person2, rel_type in targets:
            # Vérifier si la relation inverse existe
            if (person2, person1) not in existing_relations:
                # Relation asymétrique détectée
                gender1 = detect_gender(person1)
                gender2 = detect_gender(person2)
                emoji1 = '👨' if gender1 == 'M' else '👩' if gender1 == 'F' else '👤'
                emoji2 = '👨' if gender2 == 'M' else '👩' if gender2 == 'F' else '👤'
                
                relations_to_add.append({
                    'from': person2,
                    'to': person1,
                    'type': rel_type,
                    'emoji_from': emoji2,
                    'emoji_to': emoji1
                })
    
    if not relations_to_add:
        print("✅ Aucune relation asymétrique détectée !")
        print("   Toutes les relations sont déjà bidirectionnelles.\n")
        return
    
    print(f"📋 {len(relations_to_add)} relation(s) inverse(s) à ajouter:\n")
    
    # Afficher ce qui va être ajouté
    for i, rel in enumerate(relations_to_add[:10], 1):  # Afficher les 10 premières
        print(f"{i}. {rel['emoji_from']} {rel['from']} → {rel['emoji_to']} {rel['to']} (type: {rel['type']})")
    
    if len(relations_to_add) > 10:
        print(f"   ... et {len(relations_to_add) - 10} autres relations\n")
    else:
        print()
    
    if dry_run:
        print("="*80)
        print("💡 Pour appliquer ces changements, exécutez:")
        print("   python symmetrize_all_relations.py --apply")
        print("="*80 + "\n")
        return
    
    # Appliquer les modifications
    print("="*80)
    print("⏳ Application des modifications...\n")
    
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    try:
        added_count = 0
        for rel in relations_to_add:
            # Insérer la relation inverse
            cursor.execute(
                "INSERT INTO relations (person1, person2, relation_type) VALUES (?, ?, ?)",
                (rel['from'], rel['to'], rel['type'])
            )
            added_count += 1
            
            if added_count % 10 == 0:
                print(f"   ✓ {added_count}/{len(relations_to_add)} relations ajoutées...")
        
        conn.commit()
        print(f"\n✅ {added_count} relation(s) inverse(s) ajoutée(s) avec succès !")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de l'ajout des relations: {e}")
        return
    
    finally:
        conn.close()
    
    # Vérification finale
    print("\n🔍 Vérification finale...")
    db_new = RelationDB()
    new_relations = db_new.get_all_relations()
    
    print(f"\n📊 STATISTIQUES FINALES:")
    print(f"   • Relations AVANT: {len(relations)}")
    print(f"   • Relations APRÈS: {len(new_relations)}")
    print(f"   • Relations ajoutées: {len(new_relations) - len(relations)}")
    
    # Revérifier les asymétries
    new_existing = set()
    new_dict = {}
    for p1, p2, rt in new_relations:
        new_existing.add((p1, p2))
        if p1 not in new_dict:
            new_dict[p1] = set()
        new_dict[p1].add(p2)
    
    asymmetric_count = 0
    for p1, targets in new_dict.items():
        for p2 in targets:
            if (p2, p1) not in new_existing:
                asymmetric_count += 1
    
    if asymmetric_count == 0:
        print(f"   ✅ Taux de symétrie: 100% (toutes les relations sont bidirectionnelles)")
    else:
        print(f"   ⚠️  Il reste encore {asymmetric_count} relation(s) asymétrique(s)")
    
    print("\n" + "="*80)
    print("✨ Symétrisation terminée avec succès !")
    print("="*80 + "\n")


if __name__ == '__main__':
    import sys
    
    # Vérifier si --apply est passé en argument
    apply_changes = '--apply' in sys.argv
    
    if not apply_changes:
        print("\n" + "⚠️ "*20)
        print("   ATTENTION: Ce script va afficher les modifications sans les appliquer.")
        print("   Pour appliquer les changements, utilisez: --apply")
        print("⚠️ "*20 + "\n")
    
    symmetrize_all_relations(dry_run=not apply_changes)
