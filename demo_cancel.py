#!/usr/bin/env python3
"""
Demo: Add a test person, then cancel the action
"""

from services.history import history_service
from database.persons import person_repository
import time

print("=" * 70)
print("DEMO: Add Person + Cancel Action")
print("=" * 70)

# 1. Create a test person
print("\n1️⃣ Creating test person 'Test User'...")
success, msg = person_repository.create(
    name="Test User Demo"
)
print(f"   Result: {success}, {msg}")

if success:
    # Get the person
    person = person_repository.read_by_name("Test User Demo")
    print(f"   ✅ Person created with ID: {person['id']}")
    
    # Record in history
    history_service.record_action(
        action_type='ADD_PERSON',
        person1='Test User Demo',
        entity_type='person',
        entity_id=person['id'],
        entity_name='Test User Demo'
    )
    print(f"   ✅ Action recorded in history")
    
    # Wait a bit
    time.sleep(1)
    
    # 2. Get the history record
    print("\n2️⃣ Getting history records...")
    recent = history_service.get_history(limit=5, status='active')
    test_record = None
    for rec in recent:
        if rec.get('person1') == 'Test User Demo':
            test_record = rec
            break
    
    if test_record:
        print(f"   ✅ Found history record: ID={test_record['id']}")
        
        # 3. Cancel the action
        print(f"\n3️⃣ Cancelling action {test_record['id']}...")
        success, msg = history_service.cancel_action(test_record['id'], cancelled_by='demo_script')
        print(f"   Result: {msg}")
        
        if success:
            # 4. Verify person was deleted
            print("\n4️⃣ Verifying person was deleted...")
            person_check = person_repository.read_by_name("Test User Demo")
            if person_check:
                print(f"   ❌ ERROR: Person still exists!")
            else:
                print(f"   ✅ Person was successfully deleted")
            
            # 5. Check cancelled history
            print("\n5️⃣ Checking cancelled history...")
            cancelled = history_service.get_history(limit=5, status='cancelled')
            found_cancelled = False
            for rec in cancelled:
                if rec['id'] == test_record['id']:
                    found_cancelled = True
                    print(f"   ✅ Action is now marked as cancelled")
                    print(f"      - Cancelled at: {rec.get('cancelled_at')}")
                    print(f"      - Cancelled by: {rec.get('cancelled_by')}")
                    break
            
            if not found_cancelled:
                print(f"   ❌ ERROR: Action not found in cancelled history!")
        else:
            print(f"   ❌ Cancel failed: {msg}")
    else:
        print("   ❌ ERROR: History record not found!")

print("\n" + "=" * 70)
print("✅ Demo completed!")
print("=" * 70)
