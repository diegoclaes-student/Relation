# 🔧 BUTTON TROUBLESHOOTING GUIDE

## Quick Checklist

### ✅ Before Testing
```bash
# 1. Verify app is running
curl -s http://localhost:8052 | grep -q "Centrale Potins" && echo "✅ App running" || echo "❌ App down"

# 2. Check logs are clean
tail -20 /tmp/app.log | grep ERROR || echo "✅ No errors"

# 3. Clear browser cache
# Ctrl+Shift+Delete on Windows/Linux
# Cmd+Shift+Delete on Mac
```

### 🧪 Testing Each Button Type

#### **TYPE 1: Filter Buttons** (👤 Utilisateurs tab)
```
Buttons: "Tous" | "👑 Admins" | "👤 Utilisateurs" | "⏳ En attente"

Expected: Clicking changes the filter, list updates immediately
Check logs for: ✅ [USER-MGMT] Triggered: filter-all-users
```

#### **TYPE 2: Admin Toggle Buttons** (👤 Utilisateurs tab)
```
Button: "Promouvoir admin" or "Retirer admin" (yellow)

Before: Find a non-admin user like "Diego_admin"
Action: Click yellow button
After: User gets 👑 badge
Check logs for: ✅ [USER-MGMT] Triggered: {'type': 'toggle-admin', 'index': X}
              ✅ Promoted/Demoted [username]
```

#### **TYPE 3: Delete Buttons** (👤 Utilisateurs tab)
```
Button: Trash icon (red)

Before: User visible in list
Action: Click trash
After: User disappears
Check logs for: ✅ [USER-MGMT] Triggered: {'type': 'delete-user', 'index': X}
              ✅ Deleted [username]
```

#### **TYPE 4: Pending Approval Buttons** (👤 Utilisateurs tab - bottom section)
```
Buttons: ✅ (approve) | 👑 (approve as admin) | ❌ (reject)

Before: Users in "⏳ En attente d'approbation"
Action: Click any button
After: User moves to active list or is deleted
Check logs for: ✅ [USER-MGMT] Triggered: {'type': 'approve-pending-user', 'index': X}
              ✅ Approved [username] as user
```

#### **TYPE 5: Admin Panel Buttons** (👑 Admin Panel tab)
```
Buttons: ✅ (approve) | ❌ (reject) for persons/relations

Before: Persons/Relations in pending sections
Action: Click button
After: Items move to main graph or disappear
Check logs for: No [USER-MGMT] logs (different callback)
               Should see: 🔍 PERSON APPROVAL
```

---

## 🚨 Troubleshooting: Button Clicked But Nothing Happens

### Step 1: Check if callback is triggered
```bash
tail -f /tmp/app.log | grep "\[USER-MGMT\]"
# Should see: ✅ [USER-MGMT] Triggered: ...
```

**If NO logs appear:**
- Issue: Callback not firing
- Solutions:
  1. Refresh page (Ctrl+R)
  2. Check browser console (F12 → Console tab)
  3. Look for JavaScript errors
  4. Make sure you're logged in as admin

**If logs appear but say nothing changed:**
- Issue: Callback fired but database operation failed
- Solutions:
  1. Check full logs: `tail -100 /tmp/app.log`
  2. Look for SQL errors or database locks
  3. Verify database file exists: `ls -la social_network.db`

### Step 2: Check browser console
```
F12 → Console tab
Look for: Red errors or warnings
If found: Copy entire error and check logs
```

### Step 3: Check database directly
```bash
# Example: Verify user was actually promoted
sqlite3 social_network.db "SELECT username, is_admin FROM users WHERE username='Diego_admin';"

# Expected output: 
# Diego_admin|1  ← means is_admin = True (1 = true, 0 = false)
```

---

## 🐛 Common Issues & Fixes

### Issue: "Button clicked but list doesn't update"

**Diagnosis:**
```bash
# Check if callback is running
tail -f /tmp/app.log | grep -E "\[USER-MGMT\]|Error|Traceback"

# Check database
sqlite3 social_network.db "SELECT COUNT(*) FROM users;"
```

**Fix:**
1. Click the **"🔄 Actualiser"** button manually
2. Refresh the browser page (Ctrl+R)
3. Logout and login again

### Issue: "Buttons are grayed out / disabled"

**Cause:** You're not logged in as admin
**Fix:** Login with `admin` / `admin123`

### Issue: "Getting SQL errors in logs"

**Cause:** Database locked or corrupted
**Fix:**
```bash
# Kill app
pkill -f "python app_v2.py"
sleep 2

# Check database
sqlite3 social_network.db ".tables"
# Should show: users, pending_accounts, audit_log, etc.

# Restart app
cd /Users/diegoclaes/Code/Relation && python app_v2.py > /tmp/app.log 2>&1 &
```

---

## 📊 Real-Time Debugging

### Monitor logs while testing
```bash
# Terminal 1: Watch logs
tail -f /tmp/app.log | grep -E "\[USER-MGMT\]|ERROR"

# Terminal 2: Do this while watching logs
# 1. Click a button in the browser
# 2. Look for output in Terminal 1
```

### Expected output sequence:
```
✅ [USER-MGMT] Triggered: {'type': 'toggle-admin', 'index': 7}
  Action: toggle-admin on user 7
  ✅ Promoted Diego_admin
```

### If you see this instead:
```
❌ Error in user management callback: ...
Traceback (most recent call last):
  ...
```

Then there's a code error. Send the full error to debug.

---

## 🧬 How Buttons Work

```
User clicks button
    ↓
Browser sends POST to /_dash-update-component
    ↓
Dash receives callback trigger
    ↓
ctx.triggered_id = {'type': 'toggle-admin', 'index': 7}
    ↓
Python callback function runs:
  - Extracts user_id from triggered_id
  - Calls UserRepository.promote_to_admin(user_id)
  - Logs action to AuditRepository
  - Fetches updated user list
  - Returns updated HTML to browser
    ↓
Browser updates the UI
```

If ANY step fails, button doesn't work.

---

## ✅ All Systems Green Checklist

- [ ] App running (HTTP 200)
- [ ] No errors in logs
- [ ] Logged in as admin
- [ ] Data appears in tables
- [ ] Buttons are not disabled/grayed
- [ ] Filter buttons work
- [ ] Admin toggle button works
- [ ] Delete button works
- [ ] Approval buttons work
- [ ] Changes persist after page refresh

---

## 📞 If Nothing Works

1. **Collect evidence:**
   ```bash
   # Save current logs
   cp /tmp/app.log /tmp/app.log.backup
   
   # Test specific action
   # Click button and observe
   
   # Check what happened
   tail -100 /tmp/app.log
   ```

2. **Check if it's a Dash issue:**
   ```python
   # Test callback directly
   from components.user_management import update_users_list
   from dash import ctx
   # (This won't work in console, but shows the callback exists)
   ```

3. **Reset app:**
   ```bash
   pkill -f "python app_v2.py"
   sleep 3
   cd /Users/diegoclaes/Code/Relation && python app_v2.py > /tmp/app.log 2>&1 &
   sleep 3
   curl http://localhost:8052
   ```

---

**Last Updated:** 2025-10-19  
**Status:** All buttons have debug logging enabled ✅
