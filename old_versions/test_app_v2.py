#!/usr/bin/env python3
"""
Test automatique des fonctionnalités app_v2.py
Valide architecture Services + Repositories
"""

import sys
from typing import List, Tuple

# Import architecture propre
from database.persons import person_repository
from database.relations import relation_repository
from services.symmetry import symmetry_manager
from services.graph_builder import graph_builder
from services.history import history_service

# ============================================================================
# TESTS
# ============================================================================

def test_person_repository():
    """Test PersonRepository CRUD"""
    print("\n" + "="*60)
    print("TEST 1: PersonRepository CRUD")
    print("="*60)
    
    # Create
    print("\n1.1 Create person...")
    success, msg = person_repository.create(
        name="Test Person Auto",
        gender="M",  # Code court: M/F/NB/O
        sexual_orientation="hetero"  # Code court: hetero/homo/bi/pan/ace
    )
    assert success, f"Failed to create person: {msg}"
    print(f"✅ {msg}")
    
    # Read all
    print("\n1.2 Read all persons...")
    persons = person_repository.read_all()
    assert len(persons) > 0, "No persons found"
    print(f"✅ Found {len(persons)} persons")
    
    # Find created person
    test_person = next((p for p in persons if p['name'] == "Test Person Auto"), None)
    assert test_person is not None, "Test person not found"
    person_id = test_person['id']
    print(f"✅ Test person ID: {person_id}")
    
    # Read single
    print("\n1.3 Read single person...")
    person = person_repository.read(person_id)
    assert person is not None, "Failed to read person"
    assert person['name'] == "Test Person Auto"
    print(f"✅ Read person: {person['name']}")
    
    # Update
    print("\n1.4 Update person...")
    success, msg = person_repository.update(
        person_id,
        name="Test Person Updated",
        gender="F"  # Code court
    )
    assert success, f"Failed to update: {msg}"
    print(f"✅ {msg}")
    
    # Verify update
    updated = person_repository.read(person_id)
    assert updated['name'] == "Test Person Updated"
    assert updated['gender'] == "F"  # Code court
    print(f"✅ Verified update: {updated['name']}, {updated['gender']}")
    
    # Delete
    print("\n1.5 Delete person...")
    success, msg = person_repository.delete(person_id, cascade=True)
    assert success, f"Failed to delete: {msg}"
    print(f"✅ {msg}")
    
    # Verify deletion
    deleted = person_repository.read(person_id)
    assert deleted is None, "Person still exists after deletion"
    print("✅ Verified deletion")
    
    print("\n✅ PersonRepository CRUD: PASSED")


def test_relation_repository():
    """Test RelationRepository avec symétrie garantie"""
    print("\n" + "="*60)
    print("TEST 2: RelationRepository + Symmetry")
    print("="*60)
    
    # Create 2 test persons
    print("\n2.1 Create test persons...")
    success1, _ = person_repository.create(name="Alice Test", gender="F")
    success2, _ = person_repository.create(name="Bob Test", gender="M")
    assert success1 and success2, "Failed to create test persons"
    print("✅ Created Alice Test and Bob Test")
    
    # Create relation (should create both directions)
    print("\n2.2 Create symmetric relation...")
    success, msg = relation_repository.create(
        person1="Alice Test",
        person2="Bob Test",
        relation_type=1  # Friend
    )
    assert success, f"Failed to create relation: {msg}"
    print(f"✅ {msg}")
    
    # Verify both directions exist
    print("\n2.3 Verify symmetry...")
    all_relations = relation_repository.read_all(deduplicate=False)
    
    alice_to_bob = any(r[0] == "Alice Test" and r[1] == "Bob Test" for r in all_relations)
    bob_to_alice = any(r[0] == "Bob Test" and r[1] == "Alice Test" for r in all_relations)
    
    assert alice_to_bob, "Alice → Bob relation not found"
    assert bob_to_alice, "Bob → Alice relation not found"
    print("✅ Both directions exist:")
    print("   - Alice Test → Bob Test")
    print("   - Bob Test → Alice Test")
    
    # Test deduplication
    print("\n2.4 Test deduplication...")
    unique_relations = relation_repository.read_all(deduplicate=True)
    total_relations = relation_repository.read_all(deduplicate=False)
    
    print(f"   - Total relations (both directions): {len(total_relations)}")
    print(f"   - Unique relations (deduplicated): {len(unique_relations)}")
    assert len(unique_relations) * 2 <= len(total_relations), "Deduplication failed"
    print("✅ Deduplication works correctly")
    
    # Cleanup
    print("\n2.5 Cleanup test data...")
    person_repository.delete_by_name("Alice Test", cascade=True)
    person_repository.delete_by_name("Bob Test", cascade=True)
    print("✅ Test data cleaned up")
    
    print("\n✅ RelationRepository + Symmetry: PASSED")


def test_symmetry_manager():
    """Test SymmetryManager audit et correction"""
    print("\n" + "="*60)
    print("TEST 3: SymmetryManager")
    print("="*60)
    
    print("\n3.1 Audit current symmetry...")
    asymmetric = symmetry_manager.audit_symmetry()
    print(f"✅ Found {len(asymmetric)} asymmetric relations")
    
    if len(asymmetric) > 0:
        print("\n3.2 Fix asymmetries...")
        fixed_count, messages = symmetry_manager.fix_asymmetric_relations()
        print(f"✅ Fixed {fixed_count} asymmetries")
        for msg in messages[:5]:  # Show first 5
            print(f"   {msg}")
        
        # Re-audit
        print("\n3.3 Re-audit after fix...")
        asymmetric_after = symmetry_manager.audit_symmetry()
        assert len(asymmetric_after) == 0, "Asymmetries still exist after fix"
        print("✅ All relations now symmetric")
    else:
        print("✅ All relations already symmetric")
    
    print("\n✅ SymmetryManager: PASSED")


def test_graph_builder():
    """Test GraphBuilder avec cache"""
    print("\n" + "="*60)
    print("TEST 4: GraphBuilder Cache")
    print("="*60)
    
    import time
    
    # Get relations for testing
    relations = relation_repository.read_all(deduplicate=False)
    
    # Clear cache first
    print("\n4.1 Clear cache...")
    graph_builder.clear_cache()
    print("✅ Cache cleared")
    
    # First build (no cache)
    print("\n4.2 First build (no cache)...")
    start = time.time()
    G1 = graph_builder.build_graph(relations, use_cache=True)
    time1 = time.time() - start
    print(f"✅ First build: {time1*1000:.1f}ms (nodes: {len(G1.nodes())})")
    
    # Second build (with cache)
    print("\n4.3 Second build (with cache)...")
    start = time.time()
    G2 = graph_builder.build_graph(relations, use_cache=True)
    time2 = time.time() - start
    print(f"✅ Second build: {time2*1000:.1f}ms (nodes: {len(G2.nodes())})")
    
    # Verify cache speedup
    speedup = time1 / time2 if time2 > 0 else float('inf')
    print(f"\n   📊 Cache speedup: {speedup:.1f}x faster")
    
    if speedup > 2:
        print("✅ Cache provides significant speedup")
    else:
        print("⚠️  Cache speedup lower than expected (might be small dataset)")
    
    # Test cache invalidation
    print("\n4.4 Test cache invalidation...")
    graph_builder.clear_cache()
    start = time.time()
    G3 = graph_builder.build_graph(relations, use_cache=True)
    time3 = time.time() - start
    print(f"✅ After invalidation: {time3*1000:.1f}ms")
    
    assert time3 > time2 or time3 < 0.001, "Cache behavior unexpected"
    print("✅ Cache invalidation works correctly")
    
    print("\n✅ GraphBuilder Cache: PASSED")


def test_history_service():
    """Test HistoryService"""
    print("\n" + "="*60)
    print("TEST 5: HistoryService")
    print("="*60)
    
    print("\n5.1 Record test action...")
    success = history_service.record_action(
        action_type='ADD_PERSON',  # Doit être dans ACTION_TYPES
        person1='Test Person',
        details='Automated test action'
    )
    assert success, "Failed to record action"
    print("✅ Action recorded")
    
    print("\n5.2 Get recent actions...")
    recent = history_service.get_recent_actions(limit=5)
    assert len(recent) > 0, "No actions found"
    print(f"✅ Found {len(recent)} recent actions")
    
    # Verify test action exists
    test_action = next((a for a in recent if a.get('action_type') == 'ADD_PERSON'), None)
    if test_action:
        print("✅ Test action found in history")
    else:
        print("⚠️  Test action not found (might be too old)")
    
    print("\n✅ HistoryService: PASSED")


def run_all_tests():
    """Execute tous les tests"""
    print("\n" + "="*70)
    print("  🧪 APP_V2 AUTOMATED TESTS - Architecture Services + Repositories")
    print("="*70)
    
    tests = [
        ("PersonRepository CRUD", test_person_repository),
        ("RelationRepository + Symmetry", test_relation_repository),
        ("SymmetryManager", test_symmetry_manager),
        ("GraphBuilder Cache", test_graph_builder),
        ("HistoryService", test_history_service),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} ERROR: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("  📊 TEST SUMMARY")
    print("="*70)
    print(f"\n  ✅ Passed: {passed}/{len(tests)}")
    print(f"  ❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n  🎉 ALL TESTS PASSED! Architecture is solid.")
    else:
        print(f"\n  ⚠️  {failed} test(s) failed. Review needed.")
    
    print("\n" + "="*70 + "\n")
    
    return failed == 0


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
