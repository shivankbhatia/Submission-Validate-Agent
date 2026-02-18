# 🚀 Quick Reference Guide

## For Developers & Users

---

## 📖 What to Read First?

1. **Just want to run it?** → Read [STARTUP_GUIDE.md](STARTUP_GUIDE.md)
2. **Getting 404 error?** → Read [FIX_404_ERROR.md](FIX_404_ERROR.md)
3. **Want to understand how it works?** → Read [COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md)
4. **Want visual diagrams?** → Read [SYSTEM_DIAGRAMS.md](SYSTEM_DIAGRAMS.md)
5. **Want to use data management?** → Read [data_management/README.md](data_management/README.md)

---

## ⚡ Quick Start (TL;DR)

### Option 1: Start Everything at Once
```bash
start_all.bat
```

### Option 2: Manual Start
**Terminal 1 - Backend:**
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

---

## 📋 Key Files & Their Purpose

### Frontend Files
| File | Purpose |
|------|---------|
| `frontend/src/App.jsx` | Main app with routing |
| `frontend/src/pages/HomePage.jsx` | Batch evaluation (Report page) |
| `frontend/src/pages/SubmissionPage.jsx` | Individual submissions |
| `frontend/src/pages/FailureReasons.jsx` | Guide page |
| `frontend/src/components/BottomNavigation.jsx` | Navigation bar |
| `frontend/.env` | API URL configuration |

### Backend Files
| File | Purpose |
|------|---------|
| `api/app.py` | FastAPI server with 4 endpoints |
| `core/evaluator.py` | Evaluation logic |
| `tools/coursera_tool.py` | Coursera certificate verification |
| `tools/linkedin_tool.py` | LinkedIn post analysis |
| `utils/context_project_match.py` | LLM intelligent matching |

### Data Files
| File | Purpose |
|------|---------|
| `data_management/data.csv` | Main database (auto-sorted) |
| `data_management/data_manager.py` | CRUD operations |
| `submission2.csv` | Source for batch evaluations |

### Helper Scripts
| File | Purpose |
|------|---------|
| `start_all.bat` | Start both servers |
| `start_api.bat` | Start backend only |
| `start_frontend.bat` | Start frontend only |
| `verify_api_setup.py` | Verify setup before running |
| `submission_evaluator.py` | CLI evaluation tool |
| `data_management_examples.py` | Data management usage examples |

---

## 🎯 Common Tasks

### Task 1: Evaluate a Single Student

**Via Web UI:**
1. Start both servers
2. Go to http://localhost:5173
3. Click Submit (+ button)
4. Fill form: Name, Roll, Coursera Link, LinkedIn Link
5. Click "Submit for Evaluation"
6. See instant result

**Via CLI:**
```bash
python submission_evaluator.py
```

### Task 2: Batch Evaluate by Roll Number

**Via Web UI:**
1. Go to Report page (home)
2. Enter roll number
3. Click "Evaluate"
4. Watch real-time results stream in

### Task 3: View Submission History

**Via API:**
```bash
curl http://localhost:8000/submissions
```

**Via Code:**
```python
from data_management import get_all_submissions

df = get_all_submissions()
print(df)
```

### Task 4: Get Statistics

**Via API:**
```bash
curl http://localhost:8000/submissions/stats
```

**Via Code:**
```python
from data_management import get_submission_stats

stats = get_submission_stats()
print(f"Pass: {stats['pass']}, Fail: {stats['fail']}")
```

### Task 5: Export Data

```python
from data_management import export_to_csv

export_to_csv("backup_2024.csv")
```

---

## 🔧 Configuration

### Frontend Configuration

**File:** `frontend/.env`
```env
VITE_API_URL=http://localhost:8000
```

### Backend Configuration

**File:** `.env` (root directory)
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## 🌐 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/submit-evaluation` | Evaluate single submission |
| GET | `/evaluate-stream/{roll}` | Stream batch evaluation (SSE) |
| GET | `/submissions` | Get all submissions |
| GET | `/submissions/stats` | Get statistics |

### Example API Calls

**Submit Evaluation:**
```bash
curl -X POST http://localhost:8000/submit-evaluation \
  -H "Content-Type: application/json" \
  -d '{
    "student_name": "John Doe",
    "roll_number": "2021001",
    "coursera_certificate_link": "https://...",
    "linkedin_post_link": "https://..."
  }'
```

**Get Statistics:**
```bash
curl http://localhost:8000/submissions/stats
```

**Get All Submissions:**
```bash
curl http://localhost:8000/submissions
```

---

## 🎨 UI Features

### Pages

1. **Report Page (/):**
   - Batch evaluation by roll number
   - Real-time streaming results
   - Progress indicators
   - Final grade calculation

2. **Submit Page (/submit):**
   - Individual submission form
   - Instant feedback
   - Visual result display

3. **Guide Page (/guide):**
   - Evaluation criteria
   - Example images
   - Failure explanations

### Theme

- **Colors:** Orange primary (#FF8C42)
- **Dark Mode:** Auto-detect system preference
- **Style:** Rounded corners, gradient backgrounds
- **Navigation:** Fixed bottom bar with 3 sections

---

## 🔍 Evaluation Logic

### 3-Stage Pipeline

```
Stage 1: Coursera Verification → INVALID if fails
         ↓ (if valid)
Stage 2: LinkedIn Quick Match → PASS if found
         ↓ (if not found)
Stage 3: LLM Context Match → PASS/FAIL based on AI
```

### Possible Results

- **PASS:** Certificate valid + LinkedIn mentions project
- **FAIL:** Certificate valid but LinkedIn doesn't mention project
- **INVALID:** Certificate link is not valid

### Timing

- Individual evaluation: 20-40 seconds
- Batch evaluation: N × 30 seconds (N = number of projects)

---

## 🐛 Troubleshooting

### Issue: 404 Error on Evaluate

**Solution:**
1. Check API server is running (Terminal 1)
2. Check `frontend/.env` exists with correct URL
3. Restart frontend

### Issue: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
playwright install
```

### Issue: Port already in use

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:8000 | xargs kill -9
```

### Issue: Data not saving

**Solution:**
1. Check `data_management/data.csv` exists
2. Check file permissions
3. Run: `python data_management_examples.py`

---

## 📊 Data Structure

### data.csv Format

```csv
Timestamp,Roll Number,Name,Coursera Certificate Link,LinkedIn Post Link,Status,Reason
2024-01-15 10:30:00,2021001,John Doe,https://...,https://...,PASS,LinkedIn post mentions project
```

### Fields

- **Timestamp:** When submitted (YYYY-MM-DD HH:MM:SS)
- **Roll Number:** Student ID (string, preserves leading zeros)
- **Name:** Student full name
- **Coursera Certificate Link:** Coursera verification URL
- **LinkedIn Post Link:** LinkedIn post URL
- **Status:** PASS, FAIL, or INVALID
- **Reason:** Detailed explanation

### Special Features

- **Auto-sorted** by roll number
- **Thread-safe** for concurrent writes
- **Pre-initialized** with 5 sample records

---

## 🔐 Environment Variables

### Required

```env
# .env (root)
GOOGLE_API_KEY=your_gemini_api_key

# frontend/.env
VITE_API_URL=http://localhost:8000
```

### Optional

- PORT (for production deployment)
- Other API keys if adding new features

---

## 📦 Dependencies

### Python (Backend)

```
fastapi
uvicorn[standard]
pandas
pydantic
playwright
beautifulsoup4
requests
google-generativeai
```

### JavaScript (Frontend)

```json
{
  "react": "^19.2.0",
  "react-dom": "^19.2.0",
  "react-router-dom": "^7.13.0",
  "tailwindcss": "^3.4.19",
  "vite": "^7.3.1"
}
```

---

## 🎓 Usage Examples

### Example 1: CLI Submission

```bash
python submission_evaluator.py

# Enter when prompted:
# Student Name: John Doe
# Roll Number: 2021001
# Coursera Link: https://coursera.org/verify/ABC123
# LinkedIn Link: https://linkedin.com/posts/johndoe-123

# Output:
# ✅ PASS
# Reason: LinkedIn post mentions the Coursera project.
# Saved to database: data_management/data.csv
```

### Example 2: Data Management

```python
from data_management import (
    add_submission,
    get_all_submissions,
    get_submission_stats
)

# Add submission
add_submission(
    roll_number="2021006",
    name="Alice Johnson",
    coursera_link="https://...",
    linkedin_link="https://...",
    status="PASS",
    reason="LLM Context Match (90%)"
)

# View all
df = get_all_submissions()
print(df)

# Get stats
stats = get_submission_stats()
print(f"Total: {stats['total']}")
print(f"Pass Rate: {stats['pass']/stats['total']*100:.1f}%")
```

### Example 3: API Usage (JavaScript)

```javascript
// Submit evaluation
const response = await fetch('http://localhost:8000/submit-evaluation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    student_name: 'John Doe',
    roll_number: '2021001',
    coursera_certificate_link: 'https://...',
    linkedin_post_link: 'https://...'
  })
});

const result = await response.json();
console.log(result.status);  // "PASS" or "FAIL" or "INVALID"
console.log(result.reason);  // Detailed explanation
```

---

## 🚀 Best Practices

1. **Always run both servers** before using the app
2. **Check API is running** at http://localhost:8000/docs
3. **Restart frontend** after changing `.env`
4. **Use batch evaluation** for multiple projects per student
5. **Use individual submission** for new entries
6. **Backup data** regularly using `export_to_csv()`
7. **Monitor logs** in both terminal windows for debugging

---

## 📁 Project Structure (Simplified)

```
agentic_evaluator/
├── frontend/              # React app
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   └── components/
│   └── .env
│
├── api/                   # FastAPI server
│   └── app.py
│
├── core/                  # Evaluation logic
│   └── evaluator.py
│
├── tools/                 # Web scraping
│   ├── coursera_tool.py
│   └── linkedin_tool.py
│
├── utils/                 # AI matching
│   └── context_project_match.py
│
├── data_management/       # Database
│   ├── data_manager.py
│   └── data.csv
│
└── docs/                  # This is documentation
    ├── STARTUP_GUIDE.md
    ├── COMPLETE_SYSTEM_GUIDE.md
    ├── SYSTEM_DIAGRAMS.md
    ├── FIX_404_ERROR.md
    └── QUICK_REFERENCE.md (this file)
```

---

## 💡 Tips & Tricks

1. **Test API first** using Swagger UI before testing frontend
2. **Use Chrome DevTools** (F12) to debug frontend issues
3. **Check both terminal logs** when debugging
4. **Run verify_api_setup.py** before first use
5. **Keep sample data** in data.csv for reference
6. **Use LLM confidence %** to identify borderline cases
7. **Review failed submissions** manually if needed

---

## 🎯 Next Steps

After getting it running:

1. ✅ Test individual submission
2. ✅ Test batch evaluation
3. ✅ View data in data.csv
4. ✅ Check statistics endpoint
5. ✅ Explore API documentation
6. ✅ Try CLI tool
7. ✅ Export backup

---

## 📞 Need More Help?

- **Full Guide:** [COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md)
- **Setup Issues:** [STARTUP_GUIDE.md](STARTUP_GUIDE.md)
- **404 Error:** [FIX_404_ERROR.md](FIX_404_ERROR.md)
- **Visual Diagrams:** [SYSTEM_DIAGRAMS.md](SYSTEM_DIAGRAMS.md)
- **Data Management:** [data_management/README.md](data_management/README.md)

---

## ⚡ Most Common Commands

```bash
# Verify setup
python verify_api_setup.py

# Start everything
start_all.bat

# Start API only
start_api.bat
# or
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

# Start frontend only
start_frontend.bat
# or
cd frontend && npm run dev

# CLI evaluation
python submission_evaluator.py

# Data examples
python data_management_examples.py
```

---

**That's it! You now have everything you need to use the system.** 🎉
