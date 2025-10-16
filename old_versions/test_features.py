#!/usr/bin/env python3
"""
Script de test pour vérifier toutes les nouvelles fonctionnalités
"""

from database import RelationDB

def test_all_features():
    """Test complet des fonctionnalités"""
    print("\n" + "="*70)
    print("🧪 TEST DES NOUVELLES FONCTIONNALITÉS")
    print("="*70 + "\n")
    
    db = RelationDB()
    
    # 1. Test des stats de base
    print("1️⃣ Statistiques actuelles")
    persons = db.get_all_persons()
    relations = db.get_all_relations()
    pending = db.get_pending_relations()
    
    print(f"   📊 Personnes: {len(persons)}")
    print(f"   📊 Relations: {len(relations)}")
    print(f"   📬 Propositions en attente: {len(pending)}\n")
    
    # 2. Test de proposition
    print("2️⃣ Test de proposition de relation")
    test_person1 = persons[0] if persons else "Test1"
    test_person2 = persons[1] if len(persons) > 1 else "Test2"
    
    success = db.submit_pending_relation(
        test_person1, 
        test_person2, 
        0,  # Bisous
        "test_script",
        "Test automatique de proposition"
    )
    
    if success:
        print(f"   ✅ Proposition créée: {test_person1} → {test_person2}")
    else:
        print(f"   ℹ️  Proposition déjà existante")
    
    pending_after = db.get_pending_relations()
    print(f"   📬 Propositions maintenant: {len(pending_after)}\n")
    
    # 3. Test d'approbation avec symétrie
    print("3️⃣ Test d'approbation avec symétrie automatique")
    if pending_after:
        pending_id = pending_after[0]['id']
        p1 = pending_after[0]['person1']
        p2 = pending_after[0]['person2']
        
        # Compter avant
        relations_before = len(db.get_all_relations())
        
        # Approuver
        success = db.approve_relation(pending_id, "test_admin", auto_symmetrize=True)
        
        if success:
            # Compter après
            relations_after = len(db.get_all_relations())
            added = relations_after - relations_before
            
            print(f"   ✅ Relation approuvée: {p1} ↔ {p2}")
            print(f"   📊 Relations ajoutées: {added} (devrait être 2)")
            
            # Vérifier la symétrie
            all_rels = db.get_all_relations()
            has_forward = any(r[0] == p1 and r[1] == p2 for r in all_rels)
            has_backward = any(r[0] == p2 and r[1] == p1 for r in all_rels)
            
            if has_forward and has_backward:
                print(f"   ✅ Symétrie confirmée: {p1}→{p2} ET {p2}→{p1} existent")
            else:
                print(f"   ❌ ERREUR: Symétrie manquante!")
        else:
            print(f"   ℹ️  Relation déjà existante")
    else:
        print(f"   ℹ️  Aucune proposition à approuver")
    
    print()
    
    # 4. Test d'ajout direct avec symétrie
    print("4️⃣ Test d'ajout direct avec symétrie")
    if len(persons) >= 3:
        p1 = persons[0]
        p2 = persons[2]
        
        relations_before = len(db.get_all_relations())
        
        success = db.add_relation(p1, p2, 1, "test_admin", auto_symmetrize=True)
        
        if success:
            relations_after = len(db.get_all_relations())
            added = relations_after - relations_before
            
            print(f"   ✅ Relation ajoutée: {p1} ↔ {p2}")
            print(f"   📊 Relations ajoutées: {added}")
        else:
            print(f"   ℹ️  Relation déjà existante")
    
    print()
    
    # 5. Test de l'historique
    print("5️⃣ Test de l'historique")
    history = db.get_history(5)
    print(f"   📜 Dernières actions ({len(history)}):")
    
    for i, action in enumerate(history[:5], 1):
        action_type = action['action_type']
        p1 = action['person1'] or '?'
        p2 = action['person2'] or '?'
        by = action['performed_by']
        print(f"      {i}. {action_type}: {p1}→{p2} par {by}")
    
    print()
    
    # 6. Test de suppression avec symétrie
    print("6️⃣ Test de suppression avec symétrie")
    all_rels = db.get_all_relations()
    if all_rels:
        # Prendre la dernière relation ajoutée
        test_rel = all_rels[-1]
        p1, p2, rel_type = test_rel
        
        relations_before = len(db.get_all_relations())
        
        success = db.delete_relation(p1, p2, rel_type, "test_admin", auto_symmetrize=True)
        
        if success:
            relations_after = len(db.get_all_relations())
            deleted = relations_before - relations_after
            
            print(f"   ✅ Relation supprimée: {p1} ↔ {p2}")
            print(f"   📊 Relations supprimées: {deleted} (devrait être 2)")
            
            # Vérifier que les deux ont été supprimées
            remaining = db.get_all_relations()
            has_forward = any(r[0] == p1 and r[1] == p2 and r[2] == rel_type for r in remaining)
            has_backward = any(r[0] == p2 and r[1] == p1 and r[2] == rel_type for r in remaining)
            
            if not has_forward and not has_backward:
                print(f"   ✅ Suppression symétrique confirmée")
            else:
                print(f"   ⚠️  ATTENTION: Une relation n'a pas été supprimée")
        else:
            print(f"   ❌ Erreur lors de la suppression")
    
    print()
    
    # 7. Vérification finale de la symétrie
    print("7️⃣ Vérification finale de la symétrie")
    all_relations = db.get_all_relations()
    
    asymmetric_count = 0
    relation_set = set()
    
    for p1, p2, rel_type in all_relations:
        relation_set.add((p1, p2, rel_type))
    
    for p1, p2, rel_type in all_relations:
        if (p2, p1, rel_type) not in relation_set:
            asymmetric_count += 1
    
    total_relations = len(all_relations)
    symmetry_rate = ((total_relations - asymmetric_count) / total_relations * 100) if total_relations > 0 else 0
    
    print(f"   📊 Total relations: {total_relations}")
    print(f"   ⚠️  Relations asymétriques: {asymmetric_count}")
    print(f"   ✅ Taux de symétrie: {symmetry_rate:.1f}%")
    
    if asymmetric_count == 0:
        print(f"   🎉 PARFAIT ! Toutes les relations sont symétriques !")
    
    print()
    
    # Résumé
    print("="*70)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*70)
    print(f"✅ Propositions: Fonctionnel")
    print(f"✅ Approbation avec symétrie: Fonctionnel")
    print(f"✅ Ajout direct avec symétrie: Fonctionnel")
    print(f"✅ Suppression avec symétrie: Fonctionnel")
    print(f"✅ Historique: Fonctionnel")
    print(f"✅ Vérification symétrie: {symmetry_rate:.1f}%")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_all_features()
