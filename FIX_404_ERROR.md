# 🔧 Fixing the 404 Error on Evaluate Button

## Problem
When clicking the "Evaluate" button on the Report page, you're getting a **404 Not Found** error for the `/evaluate-stream` endpoint.

## Root Cause
The API server is not running or the frontend is not configured with the correct API URL.

## ✅ Solution (Step by Step)

### Step 1: Configure Frontend Environment

The frontend environment file has been created at `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

This tells the frontend where to find the API server.

### Step 2: Start the API Server

**Option A: Using the batch file (Windows)**
```bash
start_api.bat
```

**Option B: Using the shell script (Linux/Mac)**
```bash
chmod +x start_api.sh
./start_api.sh
```

**Option C: Manual command**
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 3: Verify API is Running

Open your browser and go to:
- **API Documentation:** http://localhost:8000/docs

You should see the Swagger UI with all available endpoints:
- `POST /submit-evaluation`
- `GET /evaluate-stream/{roll_number}`
- `GET /submissions`
- `GET /submissions/stats`

### Step 4: Restart Frontend (Important!)

If the frontend was already running, you MUST restart it for the new `.env` file to take effect:

1. Stop the frontend (press `Ctrl+C` in the frontend terminal)
2. Restart it:

**Windows:**
```bash
start_frontend.bat
```

**Or manually:**
```bash
cd frontend
npm run dev
```

The frontend should start on `http://localhost:5173` (or similar).

### Step 5: Test the Application

1. Open the frontend in your browser: `http://localhost:5173`
2. Navigate to the **Report page** (home page)
3. Enter a roll number (e.g., from submission2.csv)
4. Click **Evaluate**
5. You should see streaming results appear

## 🔍 Verification Steps

### Before using the app, verify everything is set up:

1. **Run the verification script:**
   ```bash
   python verify_api_setup.py
   ```

   This will check:
   - All dependencies are installed
   - Required files exist
   - API can be imported without errors
   - All endpoints are registered

2. **Check both servers are running:**
   - Terminal 1: API server logs (port 8000)
   - Terminal 2: Frontend dev server logs (port 5173)

3. **Test the API directly:**
   - Go to http://localhost:8000/docs
   - Try the `/submissions/stats` endpoint
   - Should return statistics about submissions

## 🐛 Common Issues and Solutions

### Issue 1: "Module not found" when starting API

**Solution:**
```bash
pip install -r requirements.txt
playwright install
```

### Issue 2: Port 8000 already in use

**Solution (Windows):**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Solution (Linux/Mac):**
```bash
lsof -ti:8000 | xargs kill -9
```

### Issue 3: Frontend still shows 404 after starting API

**Solutions:**
1. Verify `.env` file exists in `frontend/` directory
2. Restart the frontend (Ctrl+C and restart)
3. Clear browser cache and reload
4. Check browser console for actual error message

### Issue 4: CORS errors

**Solution:**
The API is already configured for CORS. Make sure:
- API is on `http://localhost:8000`
- Frontend is on `http://localhost:5173`
- Both are using HTTP (not mixing HTTP/HTTPS)

### Issue 5: "submission2.csv not found"

**Solution:**
The file exists in the root directory. Make sure you're running the API from the project root:
```bash
# Should be in: C:\Users\bhati\OneDrive\Documents\6th Sem\6th Sem\DS1\agentic_evaluator\
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 Quick checklist

Before using the app, ensure:

- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Node dependencies installed (`cd frontend && npm install`)
- [ ] Frontend `.env` file exists with correct API URL
- [ ] API server is running on port 8000
- [ ] Frontend dev server is running on port 5173
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:5173

## 📝 Files Created to Fix the Issue

1. **`frontend/.env`** - Frontend environment configuration
2. **`start_api.bat`** - Windows script to start API server
3. **`start_api.sh`** - Linux/Mac script to start API server
4. **`start_frontend.bat`** - Windows script to start frontend
5. **`verify_api_setup.py`** - Verification script
6. **`STARTUP_GUIDE.md`** - Comprehensive startup guide
7. **`FIX_404_ERROR.md`** - This file

## 🎯 Expected Behavior After Fix

When you click "Evaluate" button:
1. Frontend sends request to `http://localhost:8000/evaluate-stream/{roll_number}`
2. API establishes Server-Sent Events (SSE) connection
3. Each submission is evaluated sequentially
4. Results stream back to frontend in real-time
5. Table updates as each project is evaluated
6. Final grade is calculated when all done

## 📞 Still Need Help?

If you're still experiencing issues:

1. Check Terminal 1 (API) for error messages
2. Check Terminal 2 (Frontend) for error messages
3. Check browser console (F12) for frontend errors
4. Run the verification script: `python verify_api_setup.py`
5. Make sure you restarted the frontend after creating `.env`

## 🚀 Quick Start Command Summary

**Terminal 1 - Start API:**
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

That's it! Your evaluate button should now work correctly. 🎉
