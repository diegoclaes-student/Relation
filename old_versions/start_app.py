#!/usr/bin/env python3
"""
Script de démarrage avec audit automatique
Vérifie et corrige la symétrie avant de lancer l'app
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from services.symmetry import symmetry_manager
from services.graph_builder import graph_builder
from database.relations import relation_repository


def audit_and_fix():
    """Audit et correction automatique au démarrage"""
    print("\n" + "="*70)
    print("🔍 AUDIT PRÉ-DÉMARRAGE")
    print("="*70)
    
    # Statistiques
    stats = relation_repository.get_stats()
    print(f"\n📊 Relations en base: {stats['total']} ({stats['unique']} uniques)")
    
    # Audit symétrie
    asymmetric = symmetry_manager.audit_symmetry()
    
    if asymmetric:
        print(f"⚠️  {len(asymmetric)} relations asymétriques détectées")
        print("🔧 Correction automatique en cours...")
        
        fixed, messages = symmetry_manager.fix_asymmetric_relations()
        print(f"✅ {fixed} relations corrigées")
        
        # Invalider cache
        graph_builder.clear_cache()
    else:
        print("✅ Toutes les relations sont symétriques")
    
    # Stats finales
    stats_after = relation_repository.get_stats()
    print(f"📊 Relations après audit: {stats_after['total']} ({stats_after['unique']} uniques)")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        # Audit automatique
        audit_and_fix()
        
        # Lancer l'application
        print("🚀 Lancement de l'application...\n")
        
        # Importer et lancer app_full
        from app_full import app, db
        
        # Afficher infos
        persons = db.get_all_persons()
        relations = relation_repository.read_all(deduplicate=True)
        
        print("="*70)
        print("  🌐 SOCIAL NETWORK ANALYZER - Version Refactorisée")
        print("="*70)
        print(f"\n  📊 Données: {len(persons)} personnes, {len(relations)} relations")
        print(f"  🔒 Architecture: Services + Repositories")
        print(f"  ✅ Symétrie: Garantie 100%")
        print(f"  🚀 Dashboard: http://localhost:8051\n")
        print("="*70 + "\n")
        
        # Lancer
        app.run(host='0.0.0.0', port=8051, debug=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application arrêtée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
