#!/usr/bin/env python3
"""
Script de migration du format TXT vers CSV avec types de relations.

Types de relations:
- 0: Bisous (par défaut)
- 1: Dodo ensemble
- 2: Baise
- 3: Couple
"""

from pathlib import Path
import unicodedata


def normalize_name(name: str) -> str:
    """Normalise un nom pour la comparaison."""
    name = name.strip()
    # Enlever les accents pour la clé canonique
    normalized = unicodedata.normalize('NFD', name)
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return normalized.lower()


def parse_old_format(filepath: Path) -> dict:
    """Parse l'ancien format relations.txt."""
    relations = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if ':' not in line:
                continue
            
            person, connections = line.split(':', 1)
            person = person.strip()
            
            # Parser les connexions
            conn_list = [c.strip() for c in connections.split(',') if c.strip()]
            
            for conn in conn_list:
                # Créer une clé normalisée pour éviter les doublons
                key = tuple(sorted([normalize_name(person), normalize_name(conn)]))
                
                if key not in relations:
                    relations[key] = {
                        'person1': person,
                        'person2': conn,
                        'type': 0  # Type par défaut: Bisous
                    }
    
    return relations


def write_csv_format(relations: dict, output_path: Path):
    """Écrit le nouveau format CSV."""
    
    # En-tête avec la légende
    header = """# Format: Person1;Person2;RelationType
# Types de relations:
# 0 = Bisous
# 1 = Dodo ensemble
# 2 = Baise
# 3 = Couple
#
# Person1;Person2;Type
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        
        # Trier par nom de la première personne
        sorted_relations = sorted(relations.values(), key=lambda x: normalize_name(x['person1']))
        
        for rel in sorted_relations:
            f.write(f"{rel['person1']};{rel['person2']};{rel['type']}\n")
    
    print(f"✅ {len(relations)} relations écrites dans {output_path}")


def main():
    """Fonction principale."""
    input_file = Path("relations.txt")
    output_file = Path("relations.csv")
    
    if not input_file.exists():
        print(f"❌ Fichier {input_file} introuvable")
        return
    
    print(f"📖 Lecture de {input_file}...")
    relations = parse_old_format(input_file)
    
    print(f"📝 {len(relations)} relations uniques trouvées")
    print(f"   Type par défaut: 0 (Bisous)")
    
    # Sauvegarder l'ancien format
    backup_file = Path("relations.txt.backup")
    if not backup_file.exists():
        import shutil
        shutil.copy(input_file, backup_file)
        print(f"💾 Backup créé: {backup_file}")
    
    # Écrire le nouveau format
    write_csv_format(relations, output_file)
    
    print("\n" + "="*60)
    print("✨ Migration terminée !")
    print("="*60)
    print(f"\n📄 Fichier créé: {output_file}")
    print(f"📄 Backup: {backup_file}")
    print("\n💡 Tu peux maintenant éditer relations.csv pour changer les types:")
    print("   - 0 = Bisous (défaut)")
    print("   - 1 = Dodo ensemble")
    print("   - 2 = Baise")
    print("   - 3 = Couple")


if __name__ == "__main__":
    main()
