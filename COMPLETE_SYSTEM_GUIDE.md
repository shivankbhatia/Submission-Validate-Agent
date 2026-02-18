# 📘 Complete System Working Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Frontend Application](#frontend-application)
4. [Backend API](#backend-api)
5. [Evaluation Pipeline](#evaluation-pipeline)
6. [Data Management](#data-management)
7. [Complete Request Flow](#complete-request-flow)
8. [Key Components Explained](#key-components-explained)

---

## System Overview

### What Does This System Do?

This is an **Agentic Evaluator System** that automatically evaluates student submissions for Coursera Guided Projects. It:

1. **Verifies Coursera certificates** are genuine and valid
2. **Checks LinkedIn posts** to ensure students shared their projects
3. **Uses AI/LLM** for intelligent context matching when needed
4. **Provides instant feedback** (PASS/FAIL/INVALID)
5. **Stores all submissions** in a organized database
6. **Provides batch and individual evaluation** modes

### Technology Stack

**Frontend:**
- React 19.2.0 (UI framework)
- React Router (Navigation)
- Tailwind CSS (Styling)
- Vite (Build tool)

**Backend:**
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- Pandas (Data handling)

**Evaluation Tools:**
- Playwright (Web scraping)
- Beautiful Soup (HTML parsing)
- Google Gemini AI (LLM for context matching)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│                     (React Frontend)                         │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────┐           │
│  │  Report  │  │  Submission  │  │    Guide    │           │
│  │   Page   │  │     Page     │  │    Page     │           │
│  └──────────┘  └──────────────┘  └─────────────┘           │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/SSE Requests
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND API                             │
│                     (FastAPI Server)                         │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Endpoints:                                        │     │
│  │  • POST /submit-evaluation                         │     │
│  │  • GET  /evaluate-stream/{roll}                    │     │
│  │  • GET  /submissions                               │     │
│  │  • GET  /submissions/stats                         │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   EVALUATION PIPELINE                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Coursera   │→ │   LinkedIn   │→ │  LLM Match   │       │
│  │    Tool     │  │     Tool     │  │   (if needed)│       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA MANAGEMENT                            │
│              (data_management/data.csv)                      │
│   Stores: Timestamp, Roll, Name, Links, Status, Reason      │
│   Sorted by: Roll Number                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Application

### Structure

```
frontend/
├── src/
│   ├── App.jsx                    # Main app with routing
│   ├── main.jsx                   # Entry point
│   ├── components/
│   │   └── BottomNavigation.jsx   # Bottom nav bar
│   └── pages/
│       ├── HomePage.jsx            # Report/Evaluate page
│       ├── SubmissionPage.jsx     # New submission page
│       └── FailureReasons.jsx     # Guide page
├── .env                           # API_URL configuration
└── package.json                   # Dependencies
```

### 1. App.jsx - Main Application

**Purpose:** Root component that sets up routing and navigation

**Key Features:**
- Sets up React Router with 3 routes
- Manages state for HomePage (roll, records, streaming status)
- Renders BottomNavigation on all pages

**Routes:**
```javascript
/ (home)     → HomePage (Report/Evaluate)
/submit      → SubmissionPage (New submissions)
/guide       → FailureReasons (Guidelines)
```

### 2. HomePage (Report Page)

**Location:** `frontend/src/pages/HomePage.jsx`

**Purpose:** Batch evaluation - evaluate all submissions for a roll number

**How It Works:**

```javascript
// User enters roll number and clicks "Evaluate"
handleEvaluate() {
  // 1. Clear previous results
  // 2. Establish SSE connection to backend
  const eventSource = new EventSource(
    `${API_URL}/evaluate-stream/${roll}`
  );

  // 3. Listen for streaming events
  eventSource.onmessage = (event) => {
    // 4. Update UI as each project is evaluated
    // Shows: Queued → Evaluating → LLM Validation → Completed
  }
}
```

**UI Flow:**
1. User enters roll number
2. Shows student name when found
3. Table appears showing each project
4. Each row updates in real-time:
   - Status: "Queued" → "Evaluating" → "LLM Validation" → "Completed"
   - Verdict: PASS/FAIL/INVALID
   - Reason: Why it passed or failed
5. Final grade calculation shown at end

**Features:**
- Server-Sent Events (SSE) for real-time streaming
- Live status updates for each project
- Progress bar showing final score
- Error handling for no records/service down

### 3. SubmissionPage (Individual Submission)

**Location:** `frontend/src/pages/SubmissionPage.jsx`

**Purpose:** Single submission evaluation

**How It Works:**

```javascript
handleSubmit(e) {
  e.preventDefault();

  // 1. Validate all fields filled
  // 2. POST to /submit-evaluation
  const response = await fetch(`${API_URL}/submit-evaluation`, {
    method: 'POST',
    body: JSON.stringify({
      student_name, roll_number,
      coursera_certificate_link,
      linkedin_post_link
    })
  });

  // 3. Display result (PASS/FAIL/INVALID)
  // 4. Show reason
}
```

**UI Features:**
- Clean form with 4 input fields
- Loading spinner during evaluation
- Visual result display (✓ PASS or ✗ FAIL)
- "Submit Another" button to reset

### 4. FailureReasons (Guide Page)

**Location:** `frontend/src/pages/FailureReasons.jsx`

**Purpose:** Educational - shows evaluation criteria

**Content:**
- **INVALID section:** Shows correct vs incorrect certificate links
- **FAIL section:** Explains LinkedIn post requirements
- Images showing examples

### 5. BottomNavigation

**Location:** `frontend/src/components/BottomNavigation.jsx`

**Purpose:** Navigation bar fixed at bottom

**Features:**
- 3 navigation items (Report, Submit, Guide)
- Center "+" button for Submit page
- Active state highlighting (orange color)
- Icons for each section

### Theme System

**Colors:**
- Primary: Orange (#FF8C42)
- Supports light/dark mode automatically
- Rounded corners (rounded-xl, rounded-2xl)
- Gradient backgrounds

**Dark Mode:**
```javascript
// main.jsx - detects system preference
const prefersDark = window.matchMedia(
  "(prefers-color-scheme: dark)"
).matches;

// Automatically applies 'dark' class to HTML element
```

---

## Backend API

### Structure

```
api/
└── app.py                 # Main FastAPI application

core/
└── evaluator.py          # Evaluation logic

tools/
├── coursera_tool.py      # Coursera verification
└── linkedin_tool.py      # LinkedIn analysis

utils/
└── context_project_match.py  # LLM matching

data_management/
├── data_manager.py       # Data operations
└── data.csv              # Storage
```

### API Endpoints

#### 1. POST /submit-evaluation

**Purpose:** Evaluate a single submission

**Request Body:**
```json
{
  "student_name": "John Doe",
  "roll_number": "2021001",
  "coursera_certificate_link": "https://coursera.org/verify/ABC123",
  "linkedin_post_link": "https://linkedin.com/posts/johndoe-123"
}
```

**Process:**
1. Calls `evaluate_single_submission()` from evaluator
2. Saves result to `data_management/data.csv`
3. Returns result to frontend

**Response:**
```json
{
  "status": "PASS",
  "reason": "LinkedIn post mentions the Coursera project.",
  "project": "Introduction to Data Science",
  "completion_date": "2024-01-15",
  "timestamp": "2024-02-18 12:30:00"
}
```

#### 2. GET /evaluate-stream/{roll_number}

**Purpose:** Stream evaluation of all submissions for a roll number

**Technology:** Server-Sent Events (SSE)

**Process:**
1. Loads all submissions for roll number from `submission2.csv`
2. For each submission:
   - Sends "Queued" status
   - Sends "Evaluating" status
   - Runs fast evaluation phase
   - If needed, runs LLM phase
   - Sends final result
3. Sends "done" when finished

**Events Sent:**
```javascript
// Event 1 - Queued
data: {"row_id": 0, "status": "Queued"}

// Event 2 - Evaluating
data: {"row_id": 0, "status": "Evaluating"}

// Event 3 - Result
data: {
  "row_id": 0,
  "status": "Completed",
  "result": {
    "verdict": "PASS",
    "reason": "..."
  }
}

// Final event
data: {"done": true}
```

#### 3. GET /submissions

**Purpose:** Get all submissions from database

**Response:**
```json
{
  "submissions": [
    {
      "Timestamp": "2024-01-15 10:30:00",
      "Roll Number": "2021001",
      "Name": "John Doe",
      "Status": "PASS",
      ...
    }
  ],
  "count": 5
}
```

#### 4. GET /submissions/stats

**Purpose:** Get statistics

**Response:**
```json
{
  "total": 10,
  "pass": 6,
  "fail": 3,
  "invalid": 1,
  "unique_students": 8
}
```

---

## Evaluation Pipeline

### Overview

The evaluation follows a **sequential pipeline** with 3 stages:

```
1. Coursera → 2. LinkedIn → 3. LLM (if needed)
```

### Stage 1: Coursera Verification

**File:** `tools/coursera_tool.py`

**Function:** `verify_coursera_certificate(link, student_name)`

**Process:**
1. **Parse the URL** - Extract certificate ID
2. **Fetch certificate page** using Playwright (headless browser)
3. **Extract information:**
   - Project name
   - Student name
   - Completion date
4. **Validate:**
   - Is it a valid Coursera certificate page?
   - Does the name match?
   - Is it a completion certificate?

**Outputs:**
```python
{
  "Cert_Status": "Pass" or "Fail",
  "coursera_project_name": "Project Name",
  "completion_date": "January 15, 2024"
}
```

**Fail Reasons:**
- Link is not a Coursera URL
- Certificate page doesn't load
- Invalid certificate format
- Name mismatch

### Stage 2: LinkedIn Analysis

**File:** `tools/linkedin_tool.py`

**Function:** `get_linkedin_observations(link, student_name, project_name)`

**Process:**
1. **Fetch LinkedIn post** using Playwright
2. **Extract post content:**
   - Post text/description
   - Comments
   - Any project mentions
3. **Quick text matching:**
   - Search for project name in post
   - Search for keywords related to Coursera
   - Check if project is directly mentioned

**Outputs:**
```python
{
  "project_match": True/False,  # Quick text match
  "linkedin_description": "Full post text..."
}
```

**if `project_match = True`:**
- ✅ PASS immediately (no LLM needed)
- Reason: "LinkedIn post mentions the Coursera project."

**if `project_match = False`:**
- → Go to Stage 3 (LLM)

### Stage 3: LLM Context Matching

**File:** `utils/context_project_match.py`

**Function:** `llm_project_context_match(project_name, description)`

**Purpose:** Intelligent matching when direct text match fails

**Uses:** Google Gemini AI (gemini-1.5-flash)

**Process:**
1. **Send prompt to AI:**
   ```
   Does this LinkedIn post describe completing the project "{project_name}"?

   Post: {description}

   Respond with:
   - "match": true/false
   - "confidence": 0-100
   - "reasoning": explanation
   ```

2. **AI analyzes:**
   - Semantic meaning (not just keywords)
   - Context and intent
   - Student's description of their work

3. **AI responds:**
   ```json
   {
     "match": true,
     "confidence": 85,
     "reasoning": "The post describes building a data visualization dashboard, which matches the project requirements."
   }
   ```

**Final Decision:**
- if `match = true`: ✅ PASS
- if `match = false`: ❌ FAIL

**Reason examples:**
- PASS: "LLM Context Match (85%)"
- FAIL: "LinkedIn post does not mention the Coursera project."

### Complete Evaluation Logic Flow

```python
def evaluate_single_submission(student_name, roll_number,
                               coursera_link, linkedin_link):

    # STAGE 1: Coursera
    coursera_data = verify_coursera_certificate(coursera_link, student_name)

    if coursera_data['Cert_Status'] == 'Fail':
        return {
            "status": "INVALID",
            "reason": "Coursera link is invalid."
        }

    project = coursera_data['coursera_project_name']

    # STAGE 2: LinkedIn
    linkedin_data = get_linkedin_observations(
        linkedin_link, student_name, project
    )

    if linkedin_data['project_match']:  # Direct match found
        return {
            "status": "PASS",
            "reason": "LinkedIn post mentions the Coursera project."
        }

    # STAGE 3: LLM (only if direct match failed)
    llm_result = llm_project_context_match(
        project,
        linkedin_data['linkedin_description']
    )

    if llm_result['match']:
        return {
            "status": "PASS",
            "reason": f"LLM Context Match ({llm_result['confidence']}%)"
        }

    # No match found anywhere
    return {
        "status": "FAIL",
        "reason": "LinkedIn post does not mention the Coursera project."
    }
```

---

## Data Management

### File: `data_management/data.csv`

**Purpose:** Centralized storage for all submissions

**Columns:**
```csv
Timestamp, Roll Number, Name, Coursera Certificate Link,
LinkedIn Post Link, Status, Reason
```

**Example Data:**
```csv
2024-01-15 10:30:00,2021001,John Doe,https://...,https://...,PASS,LinkedIn post mentions project
2024-01-15 11:45:00,2021002,Jane Smith,https://...,https://...,FAIL,No project mention
```

### Data Manager Functions

**File:** `data_management/data_manager.py`

#### 1. initialize_data_file()

**Purpose:** Create data.csv with sample data if doesn't exist

**Process:**
- Checks if file exists
- If not, creates with 5 sample submissions
- If exists, validates structure

#### 2. add_submission()

**Purpose:** Add new submission to database

**Process:**
```python
def add_submission(roll_number, name, coursera_link,
                  linkedin_link, status, reason):
    # 1. Generate timestamp
    timestamp = datetime.now()

    # 2. Create new entry
    new_entry = {...}

    # 3. Read existing data
    df = pd.read_csv('data.csv')

    # 4. Append new entry
    df = pd.concat([df, new_entry])

    # 5. Sort by roll number
    df = df.sort_values('Roll Number')

    # 6. Save back to file
    df.to_csv('data.csv')
```

**Key Feature:** Thread-safe with locks for concurrent access

#### 3. get_all_submissions()

**Purpose:** Retrieve all submissions

**Returns:** Pandas DataFrame sorted by roll number

#### 4. get_submission_stats()

**Purpose:** Calculate statistics

**Returns:**
```python
{
    "total": 10,
    "pass": 6,
    "fail": 3,
    "invalid": 1,
    "unique_students": 8
}
```

### Data Flow Diagram

```
User Submits Form
        ↓
Frontend sends POST /submit-evaluation
        ↓
Backend runs evaluation pipeline
        ↓
Result: {status: "PASS/FAIL/INVALID", reason: "..."}
        ↓
data_manager.add_submission() called
        ↓
New entry added to data.csv (auto-sorted by roll number)
        ↓
Result returned to frontend
        ↓
User sees result on screen
```

---

## Complete Request Flow

### Flow 1: Individual Submission (SubmissionPage)

```
┌──────────────┐
│ User fills   │
│ form fields  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│ Frontend: SubmissionPage.jsx                     │
│ handleSubmit() → POST /submit-evaluation         │
└──────┬───────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│ Backend: api/app.py                              │
│ @app.post("/submit-evaluation")                  │
│   ↓                                              │
│ evaluate_single_submission() called              │
└──────┬───────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│ Evaluator: core/evaluator.py                    │
│   ↓                                              │
│ Stage 1: verify_coursera_certificate()          │
│   ↓                                              │
│ Stage 2: get_linkedin_observations()            │
│   ↓                                              │
│ Stage 3: llm_project_context_match() [if needed]│
│   ↓                                              │
│ Returns: {status, reason, project, date}         │
└──────┬───────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│ Data Manager: data_management/data_manager.py   │
│ add_submission() → saves to data.csv             │
└──────┬───────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│ Backend returns JSON response                    │
│ {status, reason, project, completion_date}       │
└──────┬───────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│ Frontend displays result                         │
│ • Green checkmark for PASS                       │
│ • Red X for FAIL                                 │
│ • Shows reason                                   │
└──────────────────────────────────────────────────┘
```

### Flow 2: Batch Evaluation (HomePage/Report)

```
┌──────────────┐
│ User enters  │
│ roll number  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│ Frontend: HomePage.jsx                           │
│ handleEvaluate() → EventSource created           │
│ GET /evaluate-stream/{roll}                      │
└──────┬───────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│ Backend: api/app.py                              │
│ @app.get("/evaluate-stream/{roll_number}")      │
│   ↓                                              │
│ Load submissions from submission2.csv            │
│   ↓                                              │
│ For each submission:                             │
│   - Send "Queued" event                          │
│   - Send "Evaluating" event                      │
│   - Run evaluate_student_fast_phase()            │
│   - If needed, run evaluate_student_llm_phase()  │
│   - Send "Completed" event with result           │
│   ↓                                              │
│ Send "done" event                                │
└──────┬───────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│ Frontend receives SSE events                     │
│   ↓                                              │
│ Updates table row by row:                        │
│ Row 1: Queued → Evaluating → Completed (PASS)   │
│ Row 2: Queued → Evaluating → LLM → Completed    │
│ Row 3: Queued → Evaluating → Completed (FAIL)   │
│   ...                                            │
│   ↓                                              │
│ Shows final grade when all done                  │
└──────────────────────────────────────────────────┘
```

---

## Key Components Explained

### 1. Server-Sent Events (SSE)

**What is it?**
A way for the server to send real-time updates to the browser.

**Why use it?**
- Evaluation can take 1-2 minutes per project
- User needs to see progress
- Better UX than waiting for everything to finish

**How it works:**
```javascript
// Frontend opens connection
const eventSource = new EventSource('/evaluate-stream/2021001');

// Backend sends events
yield f"data: {json.dumps(payload)}\n\n"

// Frontend receives events
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Update UI
}
```

### 2. Playwright Web Scraping

**What is it?**
Headless browser automation tool

**Why use it?**
- Coursera and LinkedIn require JavaScript to load
- Need to render pages like a real browser
- Can handle authentication, dynamic content

**Example:**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(certificate_url)

    # Wait for content to load
    page.wait_for_selector('.certificate-title')

    # Extract data
    title = page.query_selector('.certificate-title').inner_text()
```

### 3. LLM Integration (Google Gemini)

**Purpose:** Intelligent context understanding

**Why needed?**
- Students may not mention exact project name
- They might describe the project in their own words
- Need semantic understanding, not just keyword matching

**Example:**
```
Project: "Introduction to Data Visualization with Tableau"

LinkedIn Post: "Just completed an amazing course where I learned
to build interactive dashboards and analyze data trends!"

🤖 LLM Analysis:
- Recognizes "interactive dashboards" relates to Tableau
- Understands "analyze data trends" matches visualization
- Confidence: 85%
- Result: PASS ✅
```

### 4. State Management (React)

**HomePage uses multiple states:**
```javascript
const [roll, setRoll] = useState("");        // Input value
const [records, setRecords] = useState([]);  // Evaluation results
const [isStreaming, setIsStreaming] = useState(false);  // Loading state
const [errorMessage, setErrorMessage] = useState(null); // Errors
```

**Why?**
- React re-renders when state changes
- UI automatically updates as data streams in
- Clean separation of data and presentation

### 5. Pandas DataFrames

**Used for:**
- Reading CSV files
- Filtering data (by roll number)
- Sorting data (by roll number)
- Computing statistics

**Example:**
```python
# Read CSV
df = pd.read_csv('data.csv')

# Filter by roll number
matches = df[df['Roll Number'] == '2021001']

# Sort by roll number
df = df.sort_values('Roll Number')

# Get statistics
pass_count = len(df[df['Status'] == 'PASS'])
```

### 6. Thread Safety

**Why needed?**
Multiple submissions could be evaluated simultaneously

**Solution:**
```python
import threading

data_lock = threading.Lock()

def add_submission(...):
    with data_lock:  # Only one thread can execute at a time
        # Read file
        # Modify data
        # Write file
```

---

## Summary: What Happens When You Click "Evaluate"?

### Individual Submission (Submit Page):

1. You fill the form with 4 fields
2. Click "Submit for Evaluation"
3. **Frontend** sends POST request to backend
4. **Backend** starts evaluation pipeline:
   - ✅ Checks Coursera certificate (5-10 seconds)
   - ✅ Analyzes LinkedIn post (5-10 seconds)
   - ✅ If needed, asks AI for context match (10-20 seconds)
5. **Backend** saves result to database (data.csv)
6. **Backend** returns result
7. **Frontend** shows PASS/FAIL with reason
8. Done! ✅

**Total time:** 20-40 seconds

### Batch Evaluation (Report Page):

1. You enter roll number
2. Click "Evaluate"
3. **Frontend** opens SSE connection
4. **Backend** finds all submissions for that roll number
5. **For each submission:**
   - Shows "Queued"
   - Shows "Evaluating"
   - Runs 3-stage pipeline
   - Shows result
6. **Backend** sends "done" when all finished
7. **Frontend** shows final grade
8. Done! ✅

**Total time:** (number of submissions × 20-40 seconds)

---

## File Structure Summary

```
agentic_evaluator/
├── frontend/                    # React application
│   ├── src/
│   │   ├── App.jsx             # Main app + routing
│   │   ├── components/
│   │   │   └── BottomNavigation.jsx
│   │   └── pages/
│   │       ├── HomePage.jsx             # Report/batch eval
│   │       ├── SubmissionPage.jsx       # Individual eval
│   │       └── FailureReasons.jsx       # Guide
│   └── .env                    # API_URL config
│
├── api/
│   └── app.py                  # FastAPI backend (4 endpoints)
│
├── core/
│   └── evaluator.py            # Evaluation logic
│
├── tools/
│   ├── coursera_tool.py        # Stage 1: Coursera check
│   └── linkedin_tool.py        # Stage 2: LinkedIn check
│
├── utils/
│   └── context_project_match.py # Stage 3: LLM match
│
├── data_management/
│   ├── data_manager.py         # CRUD operations
│   ├── data.csv                # Database
│   └── README.md               # Documentation
│
├── submission2.csv             # Batch evaluation source
├── start_api.bat               # Start backend
├── start_frontend.bat          # Start frontend
├── start_all.bat               # Start both
└── COMPLETE_SYSTEM_GUIDE.md   # This file
```

---

## Key Takeaways

1. **Two Modes:**
   - Individual: Submit one at a time (SubmissionPage)
   - Batch: Evaluate all for a roll number (HomePage)

2. **Three-Stage Pipeline:**
   - Coursera (required)
   - LinkedIn (quick match)
   - LLM (smart match if needed)

3. **Two Servers:**
   - Frontend (React on port 5173)
   - Backend (FastAPI on port 8000)

4. **One Database:**
   - data.csv (sorted by roll number)

5. **Real-time Updates:**
   - SSE for streaming results
   - React state for UI updates

6. **Smart Evaluation:**
   - Direct text matching
   - AI context understanding
   - Confidence scoring

This system automates what would take hours of manual checking into seconds of automated evaluation! 🚀
