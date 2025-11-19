# 🔧 Troubleshooting Guide - Agent Aura

## Issues Resolved (January 18, 2025)

### ✅ Issue 1: 401 Unauthorized on Login
**Symptom:** Frontend shows 401 errors when trying to login  
**Cause:** Backend was returning data in different format than frontend expected  
**Solution:** Updated backend `/api/v1/students` endpoint to return `{students: []}` instead of array directly  

**Files Changed:**
- `agent-aura-backend/app/main.py` - Line 289: Changed `return result` to `return {"students": result}`
- `agent-aura-frontend/lib/api.ts` - Updated `getStudents()` to handle both formats

---

### ✅ Issue 2: 404 Page Not Found
**Symptom:** Clicking buttons shows "404 This page could not be found"  
**Cause:** API response format mismatch causing data loading failures  
**Solution:** Fixed API client to properly parse response format  

**Files Changed:**
- `agent-aura-frontend/app/admin/page.tsx` - Added fallback for array vs object response

---

### ✅ Issue 3: Wrong Demo Credentials Display
**Symptom:** Login page showed incorrect student credentials  
**Cause:** Demo credentials displayed `STU001 / student123` instead of `student1 / student1123`  
**Solution:** Updated login page to show correct credentials  

**Files Changed:**
- `agent-aura-frontend/app/login/page.tsx` - Fixed demo credentials display

---

## Quick Fixes Checklist

If you encounter issues, follow these steps:

### 1. Check Both Services Are Running

```powershell
# Check Backend (Port 8000)
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Check Frontend (Port 3000)
Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
```

**Expected Output:**
- Backend: `{"status": "healthy", "service": "agent-aura-backend", "version": "2.0.0"}`
- Frontend: Status 200

---

### 2. Test Authentication Flow

```powershell
# Login Test
$body = "username=admin&password=admin123"
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
$token = $response.access_token
Write-Host "Token received: $($token.Substring(0,50))..."

# Get User Info
$user = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
  -Headers @{Authorization="Bearer $token"}
Write-Host "User: $($user.username) - Role: $($user.role)"

# Get Students
$students = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/students" `
  -Headers @{Authorization="Bearer $token"}
Write-Host "Students found: $($students.students.Count)"
```

**Expected Output:**
- Token: Long JWT string
- User: `admin` with role `admin`
- Students: 20 students

---

### 3. Restart Services

**Backend:**
```powershell
# Kill Python processes
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# Start backend
cd S:\Courses\Kaggle\Agent_Aura_GIT\agent-aura-backend
& S:/Courses/Kaggle/Agent_Aura_GIT/.venv/Scripts/Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```powershell
# Kill Node processes
Get-Process | Where-Object {$_.ProcessName -eq "node"} | Stop-Process -Force

# Start frontend
cd S:\Courses\Kaggle\Agent_Aura_GIT\agent-aura-frontend
npm run dev
```

---

### 4. Clear Browser Cache

If login works but pages don't load:
1. Open DevTools (F12)
2. Right-click Refresh → Empty Cache and Hard Reload
3. Or clear localStorage:
   ```javascript
   localStorage.clear()
   ```

---

## Common Error Messages

### "401 Unauthorized"
**Cause:** Token expired or invalid  
**Solution:** 
1. Clear browser localStorage
2. Login again
3. Check backend is running on port 8000

---

### "404 Page Not Found"
**Cause:** Route doesn't exist or data failed to load  
**Solution:**
1. Check the URL is correct
2. Verify API returns data correctly
3. Check browser console for errors

---

### "Failed to fetch" or "Network Error"
**Cause:** Backend not running or CORS issue  
**Solution:**
1. Restart backend server
2. Check backend health: `http://localhost:8000/health`
3. Verify CORS settings in backend

---

### "Could not validate credentials"
**Cause:** JWT token validation failing  
**Solution:**
1. Restart backend (ensures SECRET_KEY is loaded)
2. Clear frontend localStorage
3. Login again

---

## Database Issues

### "No students found"
**Cause:** Database not initialized  
**Solution:**
```powershell
cd S:\Courses\Kaggle\Agent_Aura_GIT\agent-aura-backend
& S:/Courses/Kaggle/Agent_Aura_GIT/.venv/Scripts/python.exe -m app.init_demo_data
```

**Expected Output:**
```
✅ Demo database initialized successfully!
Created 22 users, 20 students with risk assessments
```

---

### "Database locked"
**Cause:** Multiple processes accessing SQLite  
**Solution:**
1. Close all backend processes
2. Delete `agent_aura_local.db` (if needed)
3. Reinitialize database
4. Restart backend

---

## Frontend Development Issues

### "Module not found" errors
**Solution:**
```powershell
cd agent-aura-frontend
npm install
```

---

### Port 3000 already in use
**Solution:**
```powershell
# Find and kill process on port 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process -Force

# Or use different port
npm run dev -- -p 3001
```

---

## Backend Development Issues

### "Port 8000 already in use"
**Solution:**
```powershell
# Find and kill process on port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

---

### "Module not found" in Python
**Solution:**
```powershell
cd S:\Courses\Kaggle\Agent_Aura_GIT
& .venv/Scripts/Activate.ps1
pip install -r agent-aura-backend/requirements.txt
```

---

## Testing Checklist

Before recording video, verify:

- [ ] Backend health check passes
- [ ] Frontend loads without errors
- [ ] Login works for all three roles (admin, teacher, student)
- [ ] Admin dashboard shows 20 students
- [ ] Student cards display risk badges correctly
- [ ] Clicking student card opens detail page
- [ ] Student detail page shows GPA, attendance, performance
- [ ] "Run AI Analysis" button opens agent page
- [ ] Agent page loads without 404 error
- [ ] All navigation links work

---

## Working Test Credentials

```
Admin:
  Username: admin
  Password: admin123
  Access: Full system access

Teacher:
  Username: teacher1
  Password: teacher123
  Access: Student monitoring

Student:
  Username: student1
  Password: student1123
  Access: Own profile only
```

---

## Quick Start Script

Run both services with one command:

```powershell
# From project root
.\START_ALL.ps1
```

This script:
1. Activates virtual environment
2. Starts backend on port 8000
3. Starts frontend on port 3000
4. Opens browser to login page

---

## Browser Console Debugging

Open DevTools (F12) and check:

**Network Tab:**
- Look for failed requests (red)
- Check request/response bodies
- Verify Authorization headers

**Console Tab:**
- Look for JavaScript errors
- Check API error messages
- Verify data is being received

**Application Tab:**
- Check localStorage for `auth_token`
- Clear storage if needed

---

## API Endpoint Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/health` | GET | No | Health check |
| `/api/v1/auth/login` | POST | No | Login (form data) |
| `/api/v1/auth/me` | GET | Yes | Get current user |
| `/api/v1/students` | GET | Yes | List all students |
| `/api/v1/students/{id}` | GET | Yes | Get student detail |
| `/api/v1/agent/invoke` | POST | Yes | Run agent analysis (SSE) |
| `/api/v1/sessions` | GET | Yes | List agent sessions |

---

## System Requirements

**Minimum:**
- Windows 10/11
- Python 3.10+
- Node.js 18+
- 4GB RAM
- 2GB disk space

**Recommended:**
- Windows 11
- Python 3.11+
- Node.js 20+
- 8GB RAM
- SSD storage

---

## Performance Tips

1. **Use Chrome/Edge** - Best DevTools support
2. **Close other applications** - Free up memory
3. **Use --reload flag** - Backend hot-reload during dev
4. **Clear browser cache** - Before recording video
5. **Restart services** - If experiencing slowness

---

## Contact & Support

If issues persist after trying all solutions:

1. Check `SYSTEM_WORKING_CONFIRMATION.md` for latest status
2. Review backend logs in PowerShell window
3. Check frontend console for errors
4. Verify all dependencies installed

---

**Last Updated:** January 18, 2025  
**Status:** All known issues resolved ✅
