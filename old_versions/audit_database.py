#!/usr/bin/env python3
"""
Script d'audit et correction automatique de la base de données
- Vérifie la symétrie des relations
- Corrige les relations asymétriques
- Affiche des statistiques détaillées
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from database.relations import relation_repository
from services.symmetry import symmetry_manager


def main():
    print("\n" + "="*70)
    print("🔍 AUDIT ET CORRECTION BASE DE DONNÉES")
    print("="*70)
    
    # 1. Statistiques générales
    print("\n📊 STATISTIQUES ACTUELLES")
    print("-" * 70)
    
    stats = relation_repository.get_stats()
    print(f"   Total relations en base: {stats['total']}")
    print(f"   Relations uniques (dédupliquées): {stats['unique']}")
    print(f"   Relations asymétriques: {stats['asymmetric']}")
    
    if stats['by_type']:
        print(f"\n   Par type de relation:")
        for rel_type, count in sorted(stats['by_type'].items()):
            print(f"      Type {rel_type}: {count} relations")
    
    # 2. Audit symétrie
    print("\n🔍 AUDIT SYMÉTRIE")
    print("-" * 70)
    
    asymmetric = symmetry_manager.audit_symmetry()
    
    if not asymmetric:
        print("   ✅ Toutes les relations sont symétriques !")
        print("   ✅ La base de données est saine.")
        return
    
    # Afficher les relations asymétriques
    print(f"   ⚠️  {len(asymmetric)} relations asymétriques détectées\n")
    
    if len(asymmetric) <= 10:
        print("   Relations sans symétrique:")
        for p1, p2, rel_type in asymmetric:
            print(f"      {p1} → {p2} (type {rel_type})")
    else:
        print(f"   Exemples de relations asymétriques (10 premiers):")
        for p1, p2, rel_type in asymmetric[:10]:
            print(f"      {p1} → {p2} (type {rel_type})")
        print(f"   ... et {len(asymmetric) - 10} autres")
    
    # 3. Proposition de correction
    print("\n🔧 CORRECTION AUTOMATIQUE")
    print("-" * 70)
    
    response = input("\n   Voulez-vous corriger automatiquement ces asymétries? (o/n): ")
    
    if response.lower() != 'o':
        print("\n   ❌ Correction annulée.")
        return
    
    # Correction
    print("\n   🔄 Correction en cours...")
    fixed_count, messages = symmetry_manager.fix_asymmetric_relations()
    
    print(f"\n   ✅ Correction terminée !")
    print(f"   ✅ {fixed_count} relations corrigées")
    
    # Afficher quelques messages
    if len(messages) <= 5:
        for msg in messages:
            print(f"   {msg}")
    else:
        for msg in messages[:5]:
            print(f"   {msg}")
        print(f"   ... et {len(messages) - 5} autres opérations")
    
    # 4. Vérification post-correction
    print("\n📊 STATISTIQUES APRÈS CORRECTION")
    print("-" * 70)
    
    stats_after = relation_repository.get_stats()
    print(f"   Total relations en base: {stats_after['total']}")
    print(f"   Relations uniques: {stats_after['unique']}")
    print(f"   Relations asymétriques: {stats_after['asymmetric']}")
    
    if stats_after['asymmetric'] == 0:
        print("\n   ✅ Base de données 100% symétrique !")
    else:
        print(f"\n   ⚠️  {stats_after['asymmetric']} asymétries restantes (erreur!)")
    
    # 5. Résumé
    print("\n" + "="*70)
    print("📝 RÉSUMÉ")
    print("="*70)
    print(f"   Relations avant: {stats['total']}")
    print(f"   Relations après: {stats_after['total']}")
    print(f"   Relations ajoutées: {stats_after['total'] - stats['total']}")
    print(f"   Symétrie garantie: {'✅ OUI' if stats_after['symmetry_ok'] else '❌ NON'}")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Audit annulé par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
