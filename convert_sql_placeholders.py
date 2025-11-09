#!/usr/bin/env python3
"""
Script pour convertir tous les placeholders SQL de ? (SQLite) vers %s (Postgres/psycopg2)
dans le dossier database/
"""
import os
import re
from pathlib import Path

def convert_sql_placeholders(file_path):
    """Convertit les ? en %s dans les chaînes SQL d'un fichier Python."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remplacer ? par %s dans les chaînes SQL (entre guillemets triples ou simples/doubles)
    # Pattern: chercher ? dans des contextes SQL typiques
    content = re.sub(r'\?', '%s', content)
    
    # Cas spécial: "INSERT OR IGNORE" n'existe pas en Postgres, remplacer par "INSERT ... ON CONFLICT DO NOTHING"
    # Note: ce pattern est simplifié; pour une vraie migration il faudrait parser le SQL proprement
    # Ici on fait un remplacement naïf
    content = re.sub(r'INSERT OR IGNORE INTO (\w+) \((\w+)\) VALUES \(%s\)',
                     r'INSERT INTO \1 (\2) VALUES (%s) ON CONFLICT (\2) DO NOTHING', content)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Converti: {file_path}")
        return True
    return False

def main():
    database_dir = Path(__file__).parent / 'database'
    if not database_dir.exists():
        print(f"❌ Dossier {database_dir} introuvable")
        return
    
    converted = 0
    for py_file in database_dir.glob('*.py'):
        if py_file.name == '__pycache__':
            continue
        if convert_sql_placeholders(py_file):
            converted += 1
    
    print(f"\n✅ Conversion terminée: {converted} fichiers modifiés")

if __name__ == '__main__':
    main()
