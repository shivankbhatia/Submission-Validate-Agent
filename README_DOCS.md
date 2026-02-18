# 📚 Agentic Evaluator - Complete Documentation Index

Welcome to the Agentic Evaluator system documentation! This system automates the evaluation of student Coursera Guided Project submissions.

---

## 🎯 What is This System?

An intelligent evaluation platform that:
- ✅ Verifies Coursera certificates automatically
- ✅ Checks LinkedIn posts for project mentions
- ✅ Uses AI for intelligent context matching
- ✅ Provides instant PASS/FAIL/INVALID feedback
- ✅ Stores all data in organized database
- ✅ Supports batch and individual evaluations

---

## 📖 Documentation Quick Links

### 🚀 Getting Started (Read These First!)

1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ⭐ **START HERE**
   - Quick reference for common tasks
   - Key commands and API endpoints
   - Troubleshooting tips
   - File structure overview

2. **[STARTUP_GUIDE.md](STARTUP_GUIDE.md)**
   - How to install dependencies
   - How to start the application
   - Environment configuration
   - Step-by-step setup instructions

3. **[FIX_404_ERROR.md](FIX_404_ERROR.md)**
   - Fixing the evaluate-stream 404 error
   - Environment setup
   - Verification steps
   - Common issues and solutions

### 📚 Understanding the System

4. **[COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md)** 📖 **COMPREHENSIVE**
   - Complete system architecture
   - Frontend application explained
   - Backend API explained
   - Evaluation pipeline in detail
   - Data management explained
   - Request flow diagrams
   - All components explained

5. **[SYSTEM_DIAGRAMS.md](SYSTEM_DIAGRAMS.md)** 📊 **VISUAL**
   - High-level architecture diagrams
   - Evaluation pipeline flowcharts
   - Data flow diagrams
   - Component interaction diagrams
   - State machine diagrams
   - Technology stack overview

### 🗄️ Data Management

6. **[data_management/README.md](data_management/README.md)**
   - Data management system
   - How to use data_manager functions
   - API endpoints for data
   - Sample data included
   - Backup and export

---

## ⚡ Quick Start

### The Fastest Way to Get Started

```bash
# 1. Start everything at once
start_all.bat

# 2. Open browser
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

That's it! 🎉

### Or Start Manually

**Terminal 1 - Backend:**
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## 📋 Directory Structure

```
agentic_evaluator/
│
├── 📁 frontend/                    # React frontend application
│   ├── src/
│   │   ├── App.jsx                # Main app with routing
│   │   ├── pages/
│   │   │   ├── HomePage.jsx       # Report/Batch evaluation
│   │   │   ├── SubmissionPage.jsx # Individual submission
│   │   │   └── FailureReasons.jsx # Guide page
│   │   └── components/
│   │       └── BottomNavigation.jsx
│   └── .env                       # Frontend config
│
├── 📁 api/                        # FastAPI backend
│   └── app.py                     # Main API server
│
├── 📁 core/                       # Evaluation logic
│   └── evaluator.py               # Main evaluator
│
├── 📁 tools/                      # Web scraping tools
│   ├── coursera_tool.py           # Coursera verification
│   └── linkedin_tool.py           # LinkedIn analysis
│
├── 📁 utils/                      # Utilities
│   └── context_project_match.py   # LLM matching
│
├── 📁 data_management/            # Database system
│   ├── data_manager.py            # CRUD operations
│   ├── data.csv                   # Main database
│   └── README.md                  # Data docs
│
├── 📄 submission2.csv             # Source for batch eval
│
├── 🚀 start_all.bat               # Start both servers
├── 🚀 start_api.bat               # Start backend only
├── 🚀 start_frontend.bat          # Start frontend only
│
├── 🔧 verify_api_setup.py         # Setup verification
├── 🔧 submission_evaluator.py     # CLI evaluation tool
├── 🔧 data_management_examples.py # Data usage examples
│
└── 📚 Documentation Files
    ├── QUICK_REFERENCE.md         # Quick reference ⭐
    ├── STARTUP_GUIDE.md           # Setup guide
    ├── COMPLETE_SYSTEM_GUIDE.md   # Full explanation
    ├── SYSTEM_DIAGRAMS.md         # Visual diagrams
    ├── FIX_404_ERROR.md           # Troubleshooting
    └── README_DOCS.md             # This file
```

---

## 🎯 What to Read Based on Your Goal

### "I just want to run it"
→ Read: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### "I'm getting errors during setup"
→ Read: [STARTUP_GUIDE.md](STARTUP_GUIDE.md)

### "The evaluate button shows 404 error"
→ Read: [FIX_404_ERROR.md](FIX_404_ERROR.md)

### "I want to understand how it works"
→ Read: [COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md)

### "I want visual diagrams"
→ Read: [SYSTEM_DIAGRAMS.md](SYSTEM_DIAGRAMS.md)

### "I want to manage the data"
→ Read: [data_management/README.md](data_management/README.md)

---

## 🌟 Key Features

### Frontend (React)
- 🎨 Modern UI with orange theme
- 🌓 Auto dark/light mode
- 📱 Responsive design
- 🔄 Real-time streaming updates
- 🧭 Bottom navigation bar

### Backend (FastAPI)
- ⚡ Fast API server
- 📡 Server-Sent Events (SSE)
- 📝 Automatic API documentation
- 🔒 CORS enabled
- 🎯 4 main endpoints

### Evaluation System
- ✅ Coursera certificate verification
- 📱 LinkedIn post analysis
- 🤖 AI-powered context matching (Google Gemini)
- 📊 Confidence scoring
- 💾 Automatic data storage

### Data Management
- 📁 CSV database
- 🔤 Auto-sorted by roll number
- 🔐 Thread-safe operations
- 📊 Statistics and analytics
- 💾 Export and backup

---

## 🎓 Three Ways to Evaluate

### 1. Web UI - Individual Submission
Navigate to: http://localhost:5173/submit
- Fill form with student details
- Click "Submit for Evaluation"
- Get instant result

### 2. Web UI - Batch Evaluation
Navigate to: http://localhost:5173/
- Enter roll number
- Click "Evaluate"
- Watch real-time streaming results

### 3. Command Line Interface
```bash
python submission_evaluator.py
```
- Enter details when prompted
- See evaluation progress
- Result saved automatically

---

## 🔧 Available Scripts

| Script | Purpose |
|--------|---------|
| `start_all.bat` | Start both frontend and backend |
| `start_api.bat` | Start backend only |
| `start_frontend.bat` | Start frontend only |
| `verify_api_setup.py` | Verify everything is set up correctly |
| `submission_evaluator.py` | CLI evaluation tool |
| `data_management_examples.py` | Data management examples |

---

## 📡 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/submit-evaluation` | POST | Evaluate single submission |
| `/evaluate-stream/{roll}` | GET | Batch evaluation (SSE) |
| `/submissions` | GET | Get all submissions |
| `/submissions/stats` | GET | Get statistics |

**API Documentation:** http://localhost:8000/docs (when running)

---

## 🔍 Evaluation Pipeline

```
User Submits
    ↓
Stage 1: Coursera Verification
    ↓ (if valid)
Stage 2: LinkedIn Quick Match
    ↓ (if not found)
Stage 3: LLM Context Match
    ↓
Result: PASS / FAIL / INVALID
    ↓
Save to Database
    ↓
Return to User
```

**Possible Results:**
- ✅ **PASS** - Certificate valid + LinkedIn mentions project
- ❌ **FAIL** - Certificate valid but no project mention
- ⚠️ **INVALID** - Certificate link is not valid

---

## 💾 Data Storage

All submissions stored in:
- **Location:** `data_management/data.csv`
- **Format:** CSV (sorted by roll number)
- **Fields:** Timestamp, Roll Number, Name, Links, Status, Reason
- **Features:** Thread-safe, auto-sorted, pre-initialized

---

## 🐛 Common Issues & Solutions

### Issue: 404 Error on Evaluate
**Solution:** API server not running → [FIX_404_ERROR.md](FIX_404_ERROR.md)

### Issue: Module not found
**Solution:** `pip install -r requirements.txt`

### Issue: Port already in use
**Solution:** Kill process or use different port

### Issue: Data not saving
**Solution:** Check file permissions and path

---

## 📊 Statistics & Analytics

Get statistics using:

**API:**
```bash
curl http://localhost:8000/submissions/stats
```

**Python:**
```python
from data_management import get_submission_stats
stats = get_submission_stats()
```

**Returns:**
- Total submissions
- Pass count
- Fail count
- Invalid count
- Unique students

---

## 🎨 UI Pages

### 1. Report Page (/)
- Batch evaluation by roll number
- Real-time streaming results
- Final grade calculation
- Pass/Fail breakdown

### 2. Submission Page (/submit)
- Individual submission form
- 4 input fields
- Instant feedback
- Visual result display

### 3. Guide Page (/guide)
- Evaluation criteria
- Example images
- Failure explanations
- Help documentation

---

## 🔐 Environment Configuration

### Frontend `.env`
```env
VITE_API_URL=http://localhost:8000
```

### Backend `.env`
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## 🚀 Technology Stack

**Frontend:**
- React 19.2.0
- React Router 7.13.0
- Tailwind CSS 3.4.19
- Vite 7.3.1

**Backend:**
- FastAPI
- Uvicorn
- Pandas
- Pydantic

**Tools:**
- Playwright (web scraping)
- Beautiful Soup (HTML parsing)
- Google Gemini (AI/LLM)

---

## 📝 Sample Data Included

The system comes with 5 sample submissions to help you understand the data structure:

```csv
2021001,John Doe,PASS,LinkedIn post mentions project
2021002,Jane Smith,FAIL,No project mention
2021003,Alice Johnson,PASS,LLM Context Match (85%)
2021004,Bob Williams,INVALID,Invalid Coursera link
2021005,Charlie Brown,PASS,LinkedIn post mentions project
```

---

## 🎯 Next Steps After Setup

1. ✅ Verify setup: `python verify_api_setup.py`
2. ✅ Start servers: `start_all.bat`
3. ✅ Test individual submission
4. ✅ Test batch evaluation
5. ✅ View data.csv
6. ✅ Check API documentation
7. ✅ Try CLI tool
8. ✅ Explore data management

---

## 💡 Pro Tips

1. **Always check both terminal logs** when debugging
2. **Use API docs** (Swagger UI) to test endpoints
3. **Restart frontend** after changing .env
4. **Backup data.csv** regularly
5. **Monitor LLM confidence** for borderline cases
6. **Use batch eval** for efficiency
7. **Review failed submissions** manually if needed

---

## 🤝 Contributing

When modifying the system:

1. **Frontend changes** → Test in browser
2. **Backend changes** → Test in Swagger UI
3. **Evaluation logic** → Test with sample data
4. **Data management** → Use examples script
5. **Always update** relevant documentation

---

## 📞 Documentation Map

```
If you're looking for...        →  Read this file
─────────────────────────────────────────────────────
Quick commands                  →  QUICK_REFERENCE.md
How to start the app            →  STARTUP_GUIDE.md
Fixing 404 error                →  FIX_404_ERROR.md
Complete explanation            →  COMPLETE_SYSTEM_GUIDE.md
Visual diagrams                 →  SYSTEM_DIAGRAMS.md
Data management                 →  data_management/README.md
All documentation links         →  README_DOCS.md (this file)
```

---

## ✨ Summary

This system provides:
- 🚀 **Fast** automated evaluation
- 🤖 **Intelligent** AI-powered matching
- 📊 **Organized** data management
- 🎨 **Beautiful** modern UI
- 📡 **Real-time** streaming updates
- 📚 **Comprehensive** documentation

**Everything you need to automate student project evaluation!**

---

## 🔗 Quick Links Summary

- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference guide ⭐
- [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - Setup and installation
- [FIX_404_ERROR.md](FIX_404_ERROR.md) - Troubleshooting 404 errors
- [COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md) - Full system explanation 📖
- [SYSTEM_DIAGRAMS.md](SYSTEM_DIAGRAMS.md) - Visual diagrams 📊
- [data_management/README.md](data_management/README.md) - Data management guide

---

**Happy Evaluating! 🎓✨**
