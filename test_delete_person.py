#!/usr/bin/env python3
"""
Test script: Create a person with relations, then delete and verify cleanup
"""

from database.persons import person_repository
from database.relations import relation_repository
from services.history import history_service
from services.graph_builder import graph_builder

print("=" * 70)
print("TEST: Delete Person with Relations")
print("=" * 70)

# 1. Create a test person
print("\n1️⃣ Creating test person 'Test Delete User'...")
success, msg = person_repository.create(name="Test Delete User")
print(f"   Result: {msg}")

if not success:
    print("   ℹ️  Person might already exist, trying to continue...")
    test_person = person_repository.read_by_name("Test Delete User")
else:
    test_person = person_repository.read_by_name("Test Delete User")

if not test_person:
    print("   ❌ ERROR: Could not create/find test person!")
    exit(1)

print(f"   ✅ Person created with ID: {test_person['id']}")

# 2. Get an existing person to create relations with
print("\n2️⃣ Getting existing persons...")
persons = person_repository.read_all()
other_persons = [p for p in persons if p['id'] != test_person['id']][:3]
print(f"   Found {len(persons)} persons, will use {len(other_persons)} for relations")

# 3. Create some relations
print("\n3️⃣ Creating relations...")
relations_created = 0
for other in other_persons:
    success, msg = relation_repository.create(
        person1=test_person['name'],
        person2=other['name'],
        relation_type=0  # Bisou
    )
    if success:
        relations_created += 1
        print(f"   ✅ Relation: {test_person['name']} ↔ {other['name']}")

print(f"   Total relations created: {relations_created}")

# 4. Verify relations exist
print("\n4️⃣ Verifying relations in database...")
all_relations = relation_repository.read_all()
test_relations = [r for r in all_relations if r[0] == test_person['name'] or r[1] == test_person['name']]
print(f"   ✅ Found {len(test_relations)} relations for {test_person['name']}")

# 5. Delete the person (with cascade)
print(f"\n5️⃣ Deleting person '{test_person['name']}' (with cascade)...")
success, msg = person_repository.delete(test_person['id'], cascade=True)
print(f"   Result: {msg}")

if not success:
    print("   ❌ ERROR: Deletion failed!")
    exit(1)

# 6. Verify person is gone
print("\n6️⃣ Verifying person was deleted...")
check_person = person_repository.read_by_name("Test Delete User")
if check_person:
    print(f"   ❌ ERROR: Person still exists: {check_person}")
else:
    print(f"   ✅ Person successfully deleted from database")

# 7. Verify relations are gone
print("\n7️⃣ Verifying relations were deleted...")
all_relations = relation_repository.read_all()
check_relations = [r for r in all_relations if r[0] == "Test Delete User" or r[1] == "Test Delete User"]
if check_relations:
    print(f"   ❌ ERROR: {len(check_relations)} relations still exist:")
    for rel in check_relations:
        print(f"      - {rel}")
else:
    print(f"   ✅ All relations successfully deleted")

# 8. Clear graph cache
print("\n8️⃣ Clearing graph cache...")
graph_builder.clear_cache()
print(f"   ✅ Cache cleared")

# 9. Final verification
print("\n9️⃣ Final database state:")
final_persons = person_repository.read_all()
final_relations = relation_repository.read_all(deduplicate=True)
print(f"   Total persons: {len(final_persons)}")
print(f"   Total relations: {len(final_relations)}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETED!")
print("=" * 70)

print("\n📝 Summary:")
print(f"   - Person created: Test Delete User (ID {test_person['id']})")
print(f"   - Relations created: {relations_created}")
print(f"   - Person deleted: {'✅ Yes' if not check_person else '❌ No'}")
print(f"   - Relations cleaned: {'✅ Yes' if not check_relations else '❌ No'}")

if not check_person and not check_relations:
    print("\n✨ All good! Person and relations deleted successfully.")
    print("\n💡 In the web UI:")
    print("   1. The person should be removed from the graph")
    print("   2. All edges connected to that person should disappear")
    print("   3. The graph should re-layout automatically")
else:
    print("\n⚠️  Something went wrong, check the errors above.")
