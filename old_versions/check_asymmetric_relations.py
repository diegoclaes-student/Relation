#!/usr/bin/env python3
"""
Script pour détecter les relations asymétriques dans la base de données.
Une relation asymétrique = A a pécho B mais B n'a pas pécho A (ou vice versa)

Cas d'usage: Si deux personnes se sont embrassées, les deux devraient avoir la relation.
"""

from database import RelationDB
from graph import detect_gender

def check_asymmetric_relations():
    """Détecte et affiche toutes les relations asymétriques"""
    db = RelationDB()
    relations = db.get_all_relations()
    
    # Créer un dictionnaire des relations
    relations_dict = {}
    for p1, p2, rel_type in relations:
        if p1 not in relations_dict:
            relations_dict[p1] = set()
        relations_dict[p1].add(p2)
    
    print("\n" + "="*80)
    print("🔍 DÉTECTION DES RELATIONS ASYMÉTRIQUES")
    print("="*80)
    print("\nRecherche de cas où A → B existe mais B → A n'existe pas...\n")
    
    asymmetric_relations = []
    
    # Vérifier chaque relation
    for person1, targets in relations_dict.items():
        for person2 in targets:
            # Vérifier si la relation inverse existe
            if person2 not in relations_dict or person1 not in relations_dict[person2]:
                # Relation asymétrique détectée
                gender1 = detect_gender(person1)
                gender2 = detect_gender(person2)
                emoji1 = '👨' if gender1 == 'M' else '👩' if gender1 == 'F' else '👤'
                emoji2 = '👨' if gender2 == 'M' else '👩' if gender2 == 'F' else '👤'
                
                asymmetric_relations.append({
                    'from': person1,
                    'to': person2,
                    'from_gender': gender1,
                    'to_gender': gender2,
                    'from_emoji': emoji1,
                    'to_emoji': emoji2
                })
    
    if not asymmetric_relations:
        print("✅ Aucune relation asymétrique détectée !")
        print("   Toutes les relations sont bidirectionnelles.\n")
    else:
        print(f"⚠️  {len(asymmetric_relations)} relation(s) asymétrique(s) détectée(s):\n")
        
        for i, rel in enumerate(asymmetric_relations, 1):
            print(f"{i}. {rel['from_emoji']} {rel['from']} → {rel['to_emoji']} {rel['to']}")
            print(f"   └─ Manque: {rel['to_emoji']} {rel['to']} → {rel['from_emoji']} {rel['from']}\n")
        
        print("="*80)
        print("💡 RECOMMANDATION:")
        print("   Si ces personnes se sont vraiment embrassées/pécho,")
        print("   ajoutez la relation inverse dans la base de données.")
        print("="*80)
    
    # Statistiques
    total_relations = len(relations)
    total_persons = len(set(p for p, _, _ in relations).union(set(p for _, p, _ in relations)))
    
    print(f"\n📊 STATISTIQUES:")
    print(f"   • Total personnes: {total_persons}")
    print(f"   • Total relations: {total_relations}")
    print(f"   • Relations asymétriques: {len(asymmetric_relations)}")
    print(f"   • Taux de symétrie: {((total_relations - len(asymmetric_relations)) / total_relations * 100):.1f}%")
    print()

if __name__ == '__main__':
    check_asymmetric_relations()
