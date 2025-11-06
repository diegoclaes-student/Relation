#!/usr/bin/env python3
"""
Génère un fichier SQL pour importer toutes les données dans Supabase
"""

import sqlite3

# Connexion à la base SQLite
conn = sqlite3.connect('social_network.db')
cursor = conn.cursor()

with open('supabase_import_data.sql', 'w', encoding='utf-8') as f:
    f.write('-- ============================================================================\n')
    f.write('-- CENTRALE POTINS MAPS - Import des données SQLite\n')
    f.write('-- ============================================================================\n')
    f.write('-- Copie-colle ce fichier dans Supabase SQL Editor et exécute\n')
    f.write('-- ============================================================================\n\n')

    # 1. Personnes
    f.write('-- 1. INSERTION DES PERSONNES\n')
    f.write('-- ============================================================================\n')
    cursor.execute('SELECT id, name FROM persons ORDER BY id')
    persons = cursor.fetchall()
    if persons:
        f.write('INSERT INTO persons (id, name) VALUES\n')
        for i, (pid, name) in enumerate(persons):
            name_escaped = name.replace("'", "''")
            comma = ',' if i < len(persons) - 1 else ';'
            f.write(f"    ({pid}, '{name_escaped}'){comma}\n")
        f.write('\n-- Reset sequence\n')
        f.write(f"SELECT setval('persons_id_seq', {len(persons)});\n\n")

    # 2. Relations (conversion des noms en IDs)
    f.write('-- 2. INSERTION DES RELATIONS\n')
    f.write('-- ============================================================================\n')
    cursor.execute('''
        SELECT r.id, p1.id as person1_id, p2.id as person2_id, r.relation_type
        FROM relations r
        JOIN persons p1 ON r.person1 = p1.name
        JOIN persons p2 ON r.person2 = p2.name
        ORDER BY r.id
    ''')
    relations = cursor.fetchall()
    if relations:
        f.write('INSERT INTO relations (id, person1_id, person2_id, relation_type) VALUES\n')
        for i, (rid, p1, p2, rtype) in enumerate(relations):
            comma = ',' if i < len(relations) - 1 else ';'
            f.write(f'    ({rid}, {p1}, {p2}, {rtype}){comma}\n')
        f.write('\n-- Reset sequence\n')
        f.write(f"SELECT setval('relations_id_seq', {len(relations)});\n\n")

    # 3. Users (conversion is_admin -> role)
    f.write('-- 3. INSERTION DES UTILISATEURS\n')
    f.write('-- ============================================================================\n')
    cursor.execute('SELECT id, username, password_hash, is_admin FROM users ORDER BY id')
    users = cursor.fetchall()
    if users:
        f.write('INSERT INTO users (id, username, password_hash, role) VALUES\n')
        for i, (uid, username, password_hash, is_admin) in enumerate(users):
            username_escaped = username.replace("'", "''")
            password_escaped = password_hash.replace("'", "''")
            role = 'admin' if is_admin == 1 else 'user'
            comma = ',' if i < len(users) - 1 else ';'
            f.write(f"    ({uid}, '{username_escaped}', '{password_escaped}', '{role}'){comma}\n")
        f.write('\n-- Reset sequence\n')
        f.write(f"SELECT setval('users_id_seq', {len(users)});\n\n")

    # 4. Pending Accounts
    f.write('-- 4. INSERTION DES DEMANDES DE COMPTE\n')
    f.write('-- ============================================================================\n')
    cursor.execute('SELECT id, username, password_hash FROM pending_accounts ORDER BY id')
    pending_accounts = cursor.fetchall()
    if pending_accounts:
        f.write('INSERT INTO pending_accounts (id, username, password_hash, status) VALUES\n')
        for i, (pid, username, password_hash) in enumerate(pending_accounts):
            username_escaped = username.replace("'", "''")
            password_escaped = password_hash.replace("'", "''")
            comma = ',' if i < len(pending_accounts) - 1 else ';'
            f.write(f"    ({pid}, '{username_escaped}', '{password_escaped}', 'pending'){comma}\n")
        f.write('\n-- Reset sequence\n')
        f.write(f"SELECT setval('pending_accounts_id_seq', {len(pending_accounts)});\n\n")
    else:
        f.write('-- Aucune demande de compte en attente\n\n')

    # 5. Pending Persons
    f.write('-- 5. INSERTION DES PROPOSITIONS DE PERSONNES\n')
    f.write('-- ============================================================================\n')
    cursor.execute('SELECT id, name, submitted_by FROM pending_persons ORDER BY id')
    pending_persons = cursor.fetchall()
    if pending_persons:
        f.write('INSERT INTO pending_persons (id, person_name, submitted_by, status) VALUES\n')
        for i, (pid, person_name, submitted_by) in enumerate(pending_persons):
            person_name_escaped = person_name.replace("'", "''")
            submitted_by_escaped = submitted_by.replace("'", "''")
            comma = ',' if i < len(pending_persons) - 1 else ';'
            f.write(f"    ({pid}, '{person_name_escaped}', '{submitted_by_escaped}', 'pending'){comma}\n")
        f.write('\n-- Reset sequence\n')
        f.write(f"SELECT setval('pending_persons_id_seq', {len(pending_persons)});\n\n")
    else:
        f.write('-- Aucune proposition de personne en attente\n\n')

    # 6. Pending Relations
    f.write('-- 6. INSERTION DES PROPOSITIONS DE RELATIONS\n')
    f.write('-- ============================================================================\n')
    cursor.execute('SELECT id, person1, person2, relation_type, submitted_by FROM pending_relations ORDER BY id')
    pending_relations = cursor.fetchall()
    if pending_relations:
        f.write('INSERT INTO pending_relations (id, person1, person2, relation_type, submitted_by, status) VALUES\n')
        for i, (pid, person1, person2, relation_type, submitted_by) in enumerate(pending_relations):
            person1_escaped = person1.replace("'", "''")
            person2_escaped = person2.replace("'", "''")
            submitted_by_escaped = submitted_by.replace("'", "''")
            comma = ',' if i < len(pending_relations) - 1 else ';'
            f.write(f"    ({pid}, '{person1_escaped}', '{person2_escaped}', {relation_type}, '{submitted_by_escaped}', 'pending'){comma}\n")
        f.write('\n-- Reset sequence\n')
        f.write(f"SELECT setval('pending_relations_id_seq', {len(pending_relations)});\n\n")
    else:
        f.write('-- Aucune proposition de relation en attente\n\n')

    f.write('-- ============================================================================\n')
    f.write('-- IMPORT TERMINE\n')
    f.write('-- ============================================================================\n')
    f.write('-- Verification :\n')
    f.write('SELECT\n')
    f.write("    'persons' as table_name,\n")
    f.write('    COUNT(*) as count\n')
    f.write('FROM persons\n')
    f.write('UNION ALL\n')
    f.write('SELECT\n')
    f.write("    'relations' as table_name,\n")
    f.write('    COUNT(*) as count\n')
    f.write('FROM relations\n')
    f.write('UNION ALL\n')
    f.write('SELECT\n')
    f.write("    'users' as table_name,\n")
    f.write('    COUNT(*) as count\n')
    f.write('FROM users;\n')
    f.write('-- ============================================================================\n')

print(f'Fichier cree : supabase_import_data.sql')
print(f'   - {len(persons)} personnes')
print(f'   - {len(relations)} relations')
print(f'   - {len(users)} utilisateurs')

conn.close()
