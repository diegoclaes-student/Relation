#!/usr/bin/env python3
"""
Script pour vérifier la connexion à Supabase et afficher l'IP locale
"""

import os
import socket
import sys

print("=" * 70)
print("🔍 VÉRIFICATION CONNEXION SUPABASE")
print("=" * 70)

# 1. Afficher l'IP locale
print("\n1️⃣  TON IP LOCALE :")
try:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"   Hostname: {hostname}")
    print(f"   IP: {local_ip}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 2. Vérifier la variable DATABASE_URL
print("\n2️⃣  VARIABLE DATABASE_URL :")
db_url = os.getenv('DATABASE_URL')
if db_url:
    # Afficher masqué pour sécurité
    parts = db_url.split('@')
    if len(parts) > 1:
        print(f"   ✅ Définie: postgresql://postgres:***@{parts[1]}")
    else:
        print(f"   ✅ Définie: {db_url[:50]}...")
else:
    print(f"   ❌ NON DÉFINIE")

# 3. Tester la connexion
print("\n3️⃣  TEST CONNEXION POSTGRESQL :")
try:
    import psycopg2
    print("   ✅ Module psycopg2 installé")
    
    if db_url:
        print("   🔄 Tentative de connexion...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM persons;")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"   ✅ CONNEXION RÉUSSIE ! ({count} personnes dans persons)")
    else:
        print("   ❌ DATABASE_URL non définie")
        
except psycopg2.OperationalError as e:
    print(f"   ❌ ERREUR CONNEXION: {str(e)[:100]}")
    print("\n   💡 SOLUTIONS:")
    print("      1. Va dans Supabase → Settings → Network")
    print("      2. Ajoute cette IP à la whitelist: ", end="")
    try:
        print(socket.gethostbyname(socket.gethostname()))
    except:
        print("[IP locale]")
    print("      3. Ou mets 'Allow all' temporairement (⚠️ non sécurisé)")
except Exception as e:
    print(f"   ❌ ERREUR: {e}")

print("\n" + "=" * 70)
