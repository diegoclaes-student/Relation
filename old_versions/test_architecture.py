#!/usr/bin/env python3
"""
Test et Démo de la nouvelle architecture
Teste Services + Repositories
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from database.base import db_manager
from database.persons import person_repository
from database.relations import relation_repository
from services.symmetry import symmetry_manager
from services.graph_builder import graph_builder
from services.history import history_service


def test_database_setup():
    """Test 1: Création et migration de la base"""
    print("\n" + "="*70)
    print("TEST 1: Initialisation Database")
    print("="*70)
    
    # Créer les tables
    db_manager._create_tables()
    print("✅ Tables créées")
    
    # Migrer depuis l'ancien format si nécessaire
    migrated = db_manager.migrate_from_old_db()
    print(f"✅ Migration: {migrated} personnes migrées")


def test_person_crud():
    """Test 2: CRUD Personnes"""
    print("\n" + "="*70)
    print("TEST 2: CRUD Personnes")
    print("="*70)
    
    # CREATE (avec les bonnes clés de genre/orientation)
    success, msg = person_repository.create("Alice Test", "F", "hetero")
    print(f"Create: {msg}")
    
    success, msg = person_repository.create("Bob Test", "M", "hetero")
    print(f"Create: {msg}")
    
    # READ
    all_persons = person_repository.read_all()
    print(f"\n✅ {len(all_persons)} personnes en base")
    
    alice = person_repository.read_by_name("Alice Test")
    if alice:
        print(f"✅ Alice trouvée: {alice}")
    
    # UPDATE
    if alice:
        success, msg = person_repository.update(alice['id'], gender="NB")
        print(f"Update: {msg}")
    
    # SEARCH
    results = person_repository.search("Test")
    print(f"\n✅ Recherche 'Test': {len(results)} résultats")


def test_relation_crud():
    """Test 3: CRUD Relations avec symétrie"""
    print("\n" + "="*70)
    print("TEST 3: CRUD Relations (Symétrie Garantie)")
    print("="*70)
    
    # CREATE (avec symétrie automatique)
    success, msg = relation_repository.create("Alice Test", "Bob Test", 0)
    print(f"Create relation: {msg}")
    
    # Vérifier que les DEUX directions existent
    all_relations = relation_repository.read_all(deduplicate=False)
    print(f"\n📊 Total relations (avec doublons): {len(all_relations)}")
    
    unique_relations = relation_repository.read_all(deduplicate=True)
    print(f"📊 Relations uniques (dédupliquées): {len(unique_relations)}")
    
    # EXISTS
    exists = relation_repository.exists("Alice Test", "Bob Test")
    print(f"\n✅ Relation Alice↔Bob existe: {exists}")
    
    exists_reverse = relation_repository.exists("Bob Test", "Alice Test")
    print(f"✅ Relation Bob↔Alice existe: {exists_reverse}")


def test_symmetry_audit():
    """Test 4: Audit et correction symétrie"""
    print("\n" + "="*70)
    print("TEST 4: Audit Symétrie")
    print("="*70)
    
    # Audit
    asymmetric = symmetry_manager.audit_symmetry()
    print(f"\n📊 Relations asymétriques détectées: {len(asymmetric)}")
    
    if asymmetric:
        print("\n⚠️  Relations sans symétrique:")
        for p1, p2, rel_type in asymmetric[:5]:  # Montrer 5 premiers
            print(f"   - {p1} → {p2} (type {rel_type})")
        
        # Correction automatique
        fixed, messages = symmetry_manager.fix_asymmetric_relations()
        print(f"\n🔧 {fixed} relations corrigées")
        for msg in messages[:3]:
            print(f"   {msg}")
    else:
        print("✅ Toutes les relations sont symétriques !")


def test_graph_builder():
    """Test 5: Construction du graphe"""
    print("\n" + "="*70)
    print("TEST 5: GraphBuilder (Cache & Déduplication)")
    print("="*70)
    
    relations = relation_repository.read_all(deduplicate=False)
    
    # Build avec déduplication
    G = graph_builder.build_graph(relations, deduplicate=True, use_cache=True)
    
    print(f"\n📊 Graphe construit:")
    print(f"   Nœuds: {G.number_of_nodes()}")
    print(f"   Arêtes: {G.number_of_edges()}")
    
    # Stats
    stats = graph_builder.get_graph_stats(G)
    print(f"\n📈 Statistiques:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Communities
    communities = graph_builder.detect_communities(G)
    num_communities = len(set(communities.values()))
    print(f"\n🎯 {num_communities} communautés détectées")


def test_history_service():
    """Test 6: Service d'historique"""
    print("\n" + "="*70)
    print("TEST 6: HistoryService (Undo/Redo)")
    print("="*70)
    
    # Enregistrer une action
    history_service.record_action(
        action_type="add_relation",
        person1="Alice Test",
        person2="Bob Test",
        relation_type=0,
        performed_by="test_script"
    )
    
    # Récupérer l'historique
    history = history_service.get_history(limit=5)
    print(f"\n📜 Dernières actions ({len(history)}):")
    for action in history:
        print(f"   [{action['action_type']}] {action['person1']} ↔ {action['person2']}")
    
    # Test undo
    can_undo, action = history_service.can_undo()
    print(f"\n🔄 Peut annuler: {can_undo}")
    if can_undo:
        print(f"   Action à annuler: {action['action_type']}")


def test_relation_stats():
    """Test 7: Statistiques relations"""
    print("\n" + "="*70)
    print("TEST 7: Statistiques Relations")
    print("="*70)
    
    stats = relation_repository.get_stats()
    
    print(f"\n📊 Statistiques:")
    print(f"   Total relations: {stats['total']}")
    print(f"   Relations uniques: {stats['unique']}")
    print(f"   Asymétriques: {stats['asymmetric']}")
    print(f"   Symétrie OK: {'✅' if stats['symmetry_ok'] else '❌'}")
    
    if stats['by_type']:
        print(f"\n📈 Par type:")
        for rel_type, count in stats['by_type'].items():
            print(f"   Type {rel_type}: {count}")


def cleanup_test_data():
    """Nettoyage des données de test"""
    print("\n" + "="*70)
    print("CLEANUP: Suppression données de test")
    print("="*70)
    
    # Supprimer Alice et Bob Test
    alice = person_repository.read_by_name("Alice Test")
    bob = person_repository.read_by_name("Bob Test")
    
    if alice:
        success, msg = person_repository.delete(alice['id'], cascade=True)
        print(f"Delete Alice: {msg}")
    
    if bob:
        success, msg = person_repository.delete(bob['id'], cascade=True)
        print(f"Delete Bob: {msg}")


def main():
    """Exécute tous les tests"""
    print("\n" + "🚀"*35)
    print("TESTS ARCHITECTURE REFACTORISÉE")
    print("🚀"*35)
    
    try:
        test_database_setup()
        test_person_crud()
        test_relation_crud()
        test_symmetry_audit()
        test_graph_builder()
        test_history_service()
        test_relation_stats()
        
        print("\n" + "="*70)
        print("✅ TOUS LES TESTS RÉUSSIS !")
        print("="*70)
        
        # Proposer nettoyage
        response = input("\n🗑️  Supprimer les données de test? (o/n): ")
        if response.lower() == 'o':
            cleanup_test_data()
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
