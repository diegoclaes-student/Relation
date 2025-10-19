# 🧪 STEP-BY-STEP TESTING GUIDE

## 🎯 Start Here

The app is fully fixed and ready to test. Follow this guide to verify everything works.

---

## ✅ PART 1: PRE-TEST CHECKS (2 minutes)

### 1.1 Verify App is Running
```bash
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8052
# Expected: Status: 200
```

### 1.2 Verify Database
```bash
sqlite3 /Users/diegoclaes/Code/Relation/social_network.db ".tables"
# Should show tables: users, pending_accounts, persons, relations, audit_log, etc.
```

### 1.3 Clear Browser Cache
```
Chrome/Firefox: Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
Safari: Preferences → Privacy → Manage Website Data → Remove All
```

### 1.4 Open Browser
```
http://localhost:8052
```

---

## 👤 PART 2: LOGIN (1 minute)

### 2.1 Login
Username: `admin`  
Password: `admin123`

### 2.2 Verify You're Logged In
- Should see "👑 Admin Panel" tab available
- Should see "👥 Utilisateurs" tab available
- Should see "📋 Historique" tab available

---

## 📊 PART 3: TEST USER MANAGEMENT (5 minutes)

### Test 3.1: View User List
1. Click **"👥 Utilisateurs"** tab (5th tab)
2. Should see:
   - "👥 Utilisateurs actifs" section with list of users
   - Each user has name, creation date
   - Some users have 👑 Admin badge
   - Buttons: yellow (promote/demote) and red (delete)

**Expected Result:** ✅ List displays with 8 users

### Test 3.2: Filter Users
1. In user list, click **"👑 Admins"** filter button
2. Should only show admin users (currently just 1: "admin")
3. Click **"👤 Utilisateurs"** filter button  
4. Should show only non-admin users (7 users)
5. Click **"Tous"** to reset

**Expected Result:** ✅ Filters work and list updates

### Test 3.3: Promote User to Admin
1. Find user "Diego_admin" (2nd user in list)
2. Click **yellow button** next to it: "Promouvoir admin"
3. **Check logs:**
   ```bash
   tail /tmp/app.log | grep "\[USER-MGMT\]"
   # Expected: ✅ [USER-MGMT] Triggered: {'type': 'toggle-admin', 'index': 7}
   #          ✅ Promoted Diego_admin
   ```
4. **Verify in UI:**
   - Button changes to "Retirer admin"
   - User gets 👑 Admin badge
   - List updates immediately

**Expected Result:** ✅ User promoted, UI updates, logs show action

### Test 3.4: Demote Admin to User
1. Click the **yellow button** again next to "Diego_admin"
2. Button should now say "Promouvoir admin" again
3. 👑 badge disappears
4. **Check logs:**
   ```bash
   tail /tmp/app.log | grep "Demoted"
   # Expected: ✅ Demoted Diego_admin
   ```

**Expected Result:** ✅ Admin status removed, UI reflects change

### Test 3.5: Delete User
1. Find any non-critical user (not "admin")
2. Click **red trash button**
3. **Verify:**
   - User disappears from list
   - Logs show action triggered
   - User still exists in database but `is_active=0`

**Check database:**
```bash
sqlite3 social_network.db "SELECT username, is_active FROM users WHERE username='[username_you_deleted]';"
# Expected: [username]|0  (0 means is_active = false/deleted)
```

**Expected Result:** ✅ Soft delete works, user hidden but data preserved

### Test 3.6: Refresh Button
1. Click **"🔄 Actualiser"** button
2. List should refresh and show current state
3. Any changes should be reflected

**Expected Result:** ✅ Refresh updates list

---

## 🔐 PART 4: TEST PENDING USER APPROVAL (3 minutes)

### Test 4.1: Check Pending Section
1. In **"👥 Utilisateurs"** tab, scroll down
2. Look for **"⏳ En attente d'approbation"** section
3. Currently shows "Aucun utilisateur en attente" (no pending users)

**Expected Result:** ✅ Section exists and is visible

### Test 4.2: Create Test Pending User (Optional)
If you want to test approval:
```python
from database.users import PendingAccountRepository
PendingAccountRepository.create_request("test_pending_user", "password123")
```

Then refresh the page to see the pending user.

### Test 4.3: Approve Pending User
1. If pending users exist, click **green ✅ button**
2. User moves to active list
3. Check logs for approval action

**Expected Result:** ✅ User approved and added to active list

---

## 👑 PART 5: TEST ADMIN PANEL (5 minutes)

### Test 5.1: Go to Admin Panel Tab
1. Click **"👑 Admin Panel"** tab (3rd tab)
2. Should see three sections:
   - 📋 Demandes de compte
   - 👥 Personnes proposées
   - 🔗 Relations proposées

**Expected Result:** ✅ All three sections visible

### Test 5.2: Check for Pending Items
Currently all sections show "Aucune..." (no pending items).

To create test data:
```python
from database.pending_submissions import pending_submission_repository

# Create test person
pending_submission_repository.submit_person("Test Person", "admin")

# Create test relation
pending_submission_repository.submit_relation("Alice", "Bob", 0, "admin")
```

Then refresh the page.

### Test 5.3: Approve Person/Relation
1. If pending persons exist, click **✅ button** next to person name
2. Should disappear from pending
3. Should appear in main graph
4. **Check logs:**
   ```bash
   tail /tmp/app.log | grep "PERSON APPROVAL"
   ```

**Expected Result:** ✅ Person/Relation approved and added to graph

### Test 5.4: Reject Person/Relation
1. Create new pending item (if needed)
2. Click **❌ button**
3. Item disappears
4. Item is NOT added to graph

**Expected Result:** ✅ Item rejected and removed

---

## 📋 PART 6: TEST HISTORY TAB (3 minutes)

### Test 6.1: Go to History Tab
1. Click **"📋 Historique"** tab (4th tab)
2. Should see audit log with filters

### Test 6.2: Check Audit Entries
Should see recent actions you performed:
- Promotions
- Demotions
- Deletions
- Approvals

### Test 6.3: Filter Audit Log
1. Use dropdown to filter by:
   - Type: person/relation/user/account
   - Action: create/update/delete/approve
2. List updates with filtered results

**Expected Result:** ✅ Filters work and show relevant entries

---

## 🔍 PART 7: VERIFY DATABASE (2 minutes)

### Check All Data is Consistent
```bash
# Check user count
sqlite3 social_network.db "SELECT COUNT(*) FROM users;" 
# Expected: 8 (or more if you added users)

# Check admin count
sqlite3 social_network.db "SELECT COUNT(*) FROM users WHERE is_admin=1;"
# Expected: 1 (just "admin") or 2 if you promoted Diego_admin

# Check deleted users (soft delete)
sqlite3 social_network.db "SELECT COUNT(*) FROM users WHERE is_active=0;"
# Expected: Shows any users you deleted

# Check audit log has entries
sqlite3 social_network.db "SELECT COUNT(*) FROM audit_log;"
# Expected: 2+ (from your testing)

# View audit log entries
sqlite3 social_network.db "SELECT action_type, entity_name, created_at FROM audit_log ORDER BY created_at DESC LIMIT 5;"
# Should show your recent actions
```

**Expected Result:** ✅ All data consistent and audit trail complete

---

## 🧭 PART 8: FINAL VERIFICATION (1 minute)

### Checklist
- [ ] ✅ App loads and responds (HTTP 200)
- [ ] ✅ Login works with admin account
- [ ] ✅ Can see all 5 tabs (Network, Public Forms, Admin Panel, History, Users)
- [ ] ✅ User management tab shows user list
- [ ] ✅ Filters work (All/Admins/Users/Pending)
- [ ] ✅ Promote button changes user to admin
- [ ] ✅ Demote button removes admin status
- [ ] ✅ Delete button removes user from list
- [ ] ✅ Admin Panel tab shows pending items
- [ ] ✅ Approve/Reject buttons work for persons
- [ ] ✅ Approve/Reject buttons work for relations
- [ ] ✅ History tab shows audit log
- [ ] ✅ All changes appear in database

**Result:** All ✅ = **FULLY OPERATIONAL** 🎉

---

## 🆘 TROUBLESHOOTING

### If buttons don't work:
1. Check logs: `tail -20 /tmp/app.log`
2. Look for: `✅ [USER-MGMT] Triggered` 
3. If not found, button click wasn't registered
4. Try: Refresh page, clear cache, restart app

### If data doesn't update:
1. Check database: `sqlite3 social_network.db "SELECT * FROM users LIMIT 1;"`
2. Manually refresh page
3. Check app logs for errors

### If tabs are disabled/grayed:
1. Verify you're logged in as admin
2. Check user's is_admin status: `sqlite3 social_network.db "SELECT is_admin FROM users WHERE username='admin';"`
3. Should show 1 (true)

---

## 📊 QUICK STATUS

**Current App Status:**
```
✅ Backend: All operations working
✅ Frontend: All buttons rendering
✅ Database: All operations working
✅ Callbacks: Debug logging enabled
✅ Audit Trail: Complete and functional
```

**Ready for Testing:** YES ✅

---

## 📞 Need Help?

Refer to:
1. `BUTTON_TROUBLESHOOTING.md` - Debug specific buttons
2. `FUNCTIONAL_VERIFICATION_REPORT.md` - Detailed test procedures
3. `/tmp/app.log` - Application logs
4. Database directly: `sqlite3 social_network.db`

---

**Last Update:** 2025-10-19  
**Status:** Ready for user testing ✅
