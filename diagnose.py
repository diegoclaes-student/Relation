#!/usr/bin/env python3
"""
Script de diagnostic intelligent pour vérifier l'état de l'application
Peut fonctionner SANS accès direct à la base de données Render
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("🔍 DIAGNOSTIC DE L'APPLICATION")
print("=" * 70)
print()

# =============================================================================
# 1. VÉRIFICATION DE L'ENVIRONNEMENT LOCAL
# =============================================================================
print("📋 1. ENVIRONNEMENT LOCAL")
print("-" * 70)

# Python version
import platform
print(f"✅ Python: {platform.python_version()}")

# Vérifier les dépendances critiques
try:
    import dash
    print(f"✅ Dash: {dash.__version__}")
except ImportError:
    print("❌ Dash: NON INSTALLÉ")

try:
    import psycopg2
    print(f"✅ psycopg2: {psycopg2.__version__}")
except ImportError:
    print("❌ psycopg2: NON INSTALLÉ - CRITIQUE pour PostgreSQL")

try:
    import plotly
    print(f"✅ Plotly: {plotly.__version__}")
except ImportError:
    print("❌ Plotly: NON INSTALLÉ")

try:
    import networkx
    print(f"✅ NetworkX: {networkx.__version__}")
except ImportError:
    print("❌ NetworkX: NON INSTALLÉ")

print()

# =============================================================================
# 2. VÉRIFICATION DE LA STRUCTURE DES FICHIERS
# =============================================================================
print("📁 2. STRUCTURE DES FICHIERS")
print("-" * 70)

critical_files = [
    "app_v2.py",
    "config.py",
    "requirements.txt",
    "database/base.py",
    "database/persons.py",
    "database/relations.py",
    "database/users.py",
    "database/pending_submissions.py",
]

all_good = True
for file_path in critical_files:
    if Path(file_path).exists():
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path} - MANQUANT")
        all_good = False

print()

# =============================================================================
# 3. VÉRIFICATION DES REQUÊTES SQL DANS LE CODE
# =============================================================================
print("🔍 3. ANALYSE DES REQUÊTES SQL")
print("-" * 70)

# Vérifier que le code utilise bien les bonnes colonnes
import re

issues = []

# Vérifier pending_submissions.py
pending_file = Path("database/pending_submissions.py")
if pending_file.exists():
    content = pending_file.read_text()
    
    # Check si le code détecte automatiquement person_name vs name
    if "person_name" in content and "use_postgres" in content:
        print("✅ pending_submissions.py: Détection automatique person_name/name")
    elif "person_name" in content:
        print("⚠️  pending_submissions.py: Utilise person_name (vérifier compatibilité)")
    else:
        print("❌ pending_submissions.py: Utilise 'name' sans détection PostgreSQL")
        issues.append("pending_submissions.py doit utiliser person_name pour PostgreSQL")

# Vérifier relations.py
relations_file = Path("database/relations.py")
if relations_file.exists():
    content = relations_file.read_text()
    
    # Check si utilise person1/person2 ou person1_id/person2_id
    if "person1_id" in content or "person2_id" in content:
        print("❌ relations.py: Utilise person1_id/person2_id (INCOMPATIBLE avec schéma attendu)")
        issues.append("relations.py utilise IDs au lieu de noms TEXT")
    elif "person1" in content and "person2" in content:
        print("✅ relations.py: Utilise person1/person2 (TEXT)")
    else:
        print("⚠️  relations.py: Structure de requête inconnue")

print()

# =============================================================================
# 4. VÉRIFICATION DU SCHÉMA POSTGRESQL DÉFINI
# =============================================================================
print("📄 4. FICHIERS DE SCHÉMA POSTGRESQL")
print("-" * 70)

schema_files = [
    ("postgres_schema_compatible.sql", "✅ RECOMMANDÉ"),
    ("supabase_schema.sql", "⚠️  ANCIEN (incompatible)"),
]

for schema_file, status in schema_files:
    if Path(schema_file).exists():
        print(f"{status} - {schema_file}")
        
        # Analyser le contenu
        content = Path(schema_file).read_text()
        
        if schema_file == "postgres_schema_compatible.sql":
            # Vérifier qu'il utilise bien person1/person2
            if "person1 TEXT" in content and "person2 TEXT" in content:
                print(f"   ✅ Utilise person1/person2 (TEXT)")
            else:
                print(f"   ❌ N'utilise pas le bon schéma")
        
        if schema_file == "supabase_schema.sql":
            # Vérifier s'il utilise les IDs
            if "person1_id" in content and "person2_id" in content:
                print(f"   ⚠️  Utilise person1_id/person2_id (INCOMPATIBLE)")
    else:
        print(f"❌ {schema_file} - MANQUANT")

print()

# =============================================================================
# 5. VÉRIFICATION DE LA CONNEXION DATABASE
# =============================================================================
print("🔌 5. CONNEXION BASE DE DONNÉES")
print("-" * 70)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("⚠️  DATABASE_URL non définie dans l'environnement local")
    print("   → Normal si tu testes en local avec SQLite")
    print("   → Pour tester avec PostgreSQL Render, définis-la:")
    print("      export DATABASE_URL='postgresql://...'")
    print()
    print("🔍 Pour obtenir l'URL:")
    print("   1. Va sur https://dashboard.render.com")
    print("   2. Clique sur ton service PostgreSQL")
    print("   3. Onglet 'Connect' → copie 'Internal Database URL'")
else:
    print(f"✅ DATABASE_URL définie: {DATABASE_URL[:30]}...")
    
    # Essayer de se connecter
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("✅ Connexion réussie à PostgreSQL")
        
        # Vérifier les tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        
        print(f"\n📊 Tables trouvées ({len(tables)}):")
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"   - {table}: {count} enregistrements")
        
        # Vérification critique: structure de la table relations
        if 'relations' in tables:
            print("\n🔍 Vérification structure table 'relations':")
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'relations' 
                AND column_name IN ('person1', 'person2', 'person1_id', 'person2_id')
                ORDER BY column_name
            """)
            
            rel_cols = cur.fetchall()
            
            if any('person1' in col[0] and col[1] == 'text' for col in rel_cols):
                print("   ✅ Utilise person1/person2 (TEXT) - CORRECT")
            elif any('person1_id' in col[0] for col in rel_cols):
                print("   ❌ Utilise person1_id/person2_id (INTEGER) - INCOMPATIBLE")
                issues.append("Table relations utilise IDs au lieu de TEXT")
            else:
                print("   ⚠️  Structure inconnue")
        
        # Vérification: structure de la table pending_persons
        if 'pending_persons' in tables:
            print("\n🔍 Vérification structure table 'pending_persons':")
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'pending_persons' 
                AND column_name IN ('name', 'person_name')
                ORDER BY column_name
            """)
            
            pp_cols = cur.fetchall()
            
            if any('person_name' in col[0] for col in pp_cols):
                print("   ✅ Utilise 'person_name' - CORRECT (code adapté)")
            elif any(col[0] == 'name' for col in pp_cols):
                print("   ⚠️  Utilise 'name' - Code doit détecter automatiquement")
            else:
                print("   ⚠️  Colonne nom manquante")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        issues.append(f"Impossible de se connecter à PostgreSQL: {e}")

print()

# =============================================================================
# 6. RÉSUMÉ ET RECOMMANDATIONS
# =============================================================================
print("=" * 70)
print("📊 RÉSUMÉ DU DIAGNOSTIC")
print("=" * 70)
print()

if issues:
    print("❌ PROBLÈMES DÉTECTÉS:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    print()
    print("🔧 ACTIONS RECOMMANDÉES:")
    print("   1. Lis SCHEMA_VERIFICATION_SUMMARY.md pour le plan d'action")
    print("   2. Lance check_render_schema.py avec DATABASE_URL définie")
    print("   3. Applique les migrations si nécessaire")
else:
    if DATABASE_URL:
        print("✅ TOUT EST BON ! Aucun problème détecté.")
        print()
        print("🚀 L'application devrait fonctionner correctement.")
    else:
        print("✅ CODE LOCAL OK")
        print()
        print("⚠️  Pour vérifier la base de données Render:")
        print("   export DATABASE_URL='ton_url_render'")
        print("   python3 check_render_schema.py")

print()
print("=" * 70)
print("📚 DOCUMENTATION DISPONIBLE:")
print("   - SCHEMA_VERIFICATION_SUMMARY.md (⭐ Lis ça en premier)")
print("   - QUICK_SCHEMA_GUIDE.md (Guide détaillé)")
print("   - SCHEMA_VERIFICATION_REPORT.md (Analyse technique)")
print("=" * 70)
