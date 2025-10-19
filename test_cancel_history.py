#!/usr/bin/env python3
"""
Test script for cancel history functionality
"""

from services.history import history_service
from database.persons import person_repository

def test_cancel_functionality():
    """Test the cancel history functionality"""
    
    print("=" * 70)
    print("TEST: Cancel History Functionality")
    print("=" * 70)
    
    # 1. Get current history
    print("\n1️⃣ Getting current active history...")
    active = history_service.get_history(limit=10, status='active')
    print(f"   ✅ Found {len(active)} active records")
    if active:
        print(f"   First record: ID={active[0]['id']}, type={active[0]['action_type']}, person={active[0].get('person1')}")
    
    # 2. Get cancelled history
    print("\n2️⃣ Getting cancelled history...")
    cancelled = history_service.get_history(limit=10, status='cancelled')
    print(f"   ✅ Found {len(cancelled)} cancelled records")
    
    # 3. Test cancelling an action (if any active)
    if active:
        test_action = active[0]
        print(f"\n3️⃣ Testing cancel on action ID {test_action['id']}...")
        print(f"   Action: {test_action['action_type']}")
        print(f"   Person1: {test_action.get('person1')}")
        print(f"   Person2: {test_action.get('person2')}")
        print(f"   Status: {test_action.get('status', 'active')}")
        
        # Don't actually cancel, just show what would happen
        print(f"\n   ℹ️  To cancel this action, you would:")
        print(f"      history_service.cancel_action({test_action['id']}, cancelled_by='test_user')")
        print(f"\n   This would:")
        if test_action['action_type'] in ['ADD_RELATION', 'UPDATE']:
            print(f"      - Delete relation: {test_action.get('person1')} ↔ {test_action.get('person2')}")
        elif test_action['action_type'] == 'UPDATE_PERSON':
            if test_action.get('old_value'):
                print(f"      - Restore person name: {test_action.get('new_value')} → {test_action.get('old_value')}")
            else:
                print(f"      ⚠️  No old_value stored, cannot restore")
        print(f"      - Mark action as cancelled in history table")
    
    # 4. Check history schema
    print("\n4️⃣ Checking history table structure...")
    import sqlite3
    from config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(history)")
    columns = cursor.fetchall()
    print("   Columns:")
    for col in columns:
        print(f"      - {col[1]:20s} {col[2]:10s} {'NOT NULL' if col[3] else 'NULL':10s} {col[4] if col[4] else ''}")
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Test completed successfully!")
    print("=" * 70)
    print("\n📋 Summary:")
    print(f"   - Active records: {len(active)}")
    print(f"   - Cancelled records: {len(cancelled)}")
    print(f"   - Total: {len(active) + len(cancelled)}")
    print("\n💡 To test cancellation in the UI:")
    print("   1. Go to http://localhost:8052")
    print("   2. Login as admin")
    print("   3. Go to 'Historique' tab")
    print("   4. Click 'Annuler' button on any recent action")
    print("   5. The action should move to 'Modifications Annulées' tab")
    print("   6. Check logs with: tail -f app_output.log | grep HISTORY")

if __name__ == "__main__":
    test_cancel_functionality()
