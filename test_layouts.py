#!/usr/bin/env python3
"""
Test script to verify all layout modes work correctly with the real database
"""

import sys
from graph import build_graph, compute_layout, make_figure
from database.relations import RelationRepository
from database.persons import PersonRepository

def test_all_layouts():
    """Test each layout mode with real data"""
    
    # Initialize repositories
    person_repo = PersonRepository()
    relation_repo = RelationRepository()
    
    # Get real data
    relations = relation_repo.read_all(deduplicate=True)
    print(f"📊 Database: {len(relations)} relations loaded")
    
    if not relations:
        print("❌ No relations found!")
        return False
    
    # Convert to dict format
    relations_dict = {}
    for p1, p2, rel_type in relations:
        if p1 not in relations_dict:
            relations_dict[p1] = []
        relations_dict[p1].append((p2, rel_type))
    
    # Build graph
    G = build_graph(relations_dict)
    print(f"📈 Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Test each layout mode
    layout_modes = ['community', 'circular', 'hierarchical', 'radial', 'spring', 'kk', 'spectral']
    results = {}
    
    for mode in layout_modes:
        try:
            print(f"\n🔄 Testing layout: {mode}", end=" ... ")
            pos = compute_layout(G, mode=mode)
            
            # Verify position data
            if not pos:
                print("❌ No positions returned")
                results[mode] = False
                continue
            
            if len(pos) != G.number_of_nodes():
                print(f"❌ Position count mismatch: got {len(pos)}, expected {G.number_of_nodes()}")
                results[mode] = False
                continue
            
            # Try to create figure
            fig = make_figure(G, pos)
            print(f"✅ Success")
            results[mode] = True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results[mode] = False
    
    # Summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for mode, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {mode}")
    
    print(f"\n✨ Results: {passed}/{total} layouts working")
    return passed == total

if __name__ == '__main__':
    success = test_all_layouts()
    sys.exit(0 if success else 1)
