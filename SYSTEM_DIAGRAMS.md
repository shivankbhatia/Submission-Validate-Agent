# 📊 Visual System Diagrams

## Table of Contents
1. [High-Level System Architecture](#high-level-system-architecture)
2. [Evaluation Pipeline Flow](#evaluation-pipeline-flow)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Component Interaction](#component-interaction)

---

## High-Level System Architecture

```
                    ┌─────────────────────────────────┐
                    │         USER'S BROWSER          │
                    │    http://localhost:5173        │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────▼────────────────────┐
                    │      REACT FRONTEND             │
                    │  ┌──────────────────────────┐   │
                    │  │  Bottom Navigation       │   │
                    │  │  ┌────┬────────┬──────┐ │   │
                    │  │  │Rpt │ Submit │Guide │ │   │
                    │  │  └────┴────────┴──────┘ │   │
                    │  └──────────────────────────┘   │
                    │                                 │
                    │  ┌──────────────────────────┐   │
                    │  │   Report Page (/)        │   │
                    │  │   • Batch evaluation     │   │
                    │  │   • SSE streaming        │   │
                    │  │   • Real-time updates    │   │
                    │  └──────────────────────────┘   │
                    │                                 │
                    │  ┌──────────────────────────┐   │
                    │  │  Submission Page         │   │
                    │  │   • Individual eval      │   │
                    │  │   • Instant feedback     │   │
                    │  └──────────────────────────┘   │
                    │                                 │
                    │  ┌──────────────────────────┐   │
                    │  │   Guide Page             │   │
                    │  │   • Examples             │   │
                    │  │   • Criteria             │   │
                    │  └──────────────────────────┘   │
                    └────────────┬────────────────────┘
                                 │
                    HTTP/SSE     │
                    Requests     │
                                 │
                    ┌────────────▼────────────────────┐
                    │     FASTAPI BACKEND             │
                    │   http://localhost:8000         │
                    │                                 │
                    │  /submit-evaluation (POST)      │
                    │  /evaluate-stream/{roll} (GET)  │
                    │  /submissions (GET)             │
                    │  /submissions/stats (GET)       │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────▼────────────────────┐
                    │   EVALUATION PIPELINE           │
                    │                                 │
                    │   ┌─────────────────────┐       │
                    │   │  1. Coursera Tool   │       │
                    │   │  verify_coursera_   │       │
                    │   │  certificate()      │       │
                    │   │  • Validate link    │       │
                    │   │  • Extract info     │       │
                    │   └──────────┬──────────┘       │
                    │              │                  │
                    │   ┌──────────▼──────────┐       │
                    │   │  2. LinkedIn Tool   │       │
                    │   │  get_linkedin_      │       │
                    │   │  observations()     │       │
                    │   │  • Fetch post       │       │
                    │   │  • Quick match      │       │
                    │   └──────────┬──────────┘       │
                    │              │                  │
                    │   ┌──────────▼──────────┐       │
                    │   │  3. LLM Matching    │       │
                    │   │  llm_project_       │       │
                    │   │  context_match()    │       │
                    │   │  • Semantic match   │       │
                    │   │  • Confidence %     │       │
                    │   └──────────┬──────────┘       │
                    │              │                  │
                    │   ┌──────────▼──────────┐       │
                    │   │  Result:            │       │
                    │   │  PASS/FAIL/INVALID  │       │
                    │   └─────────────────────┘       │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────▼────────────────────┐
                    │    DATA MANAGEMENT              │
                    │                                 │
                    │  data_management/data.csv       │
                    │  ┌───────────────────────────┐  │
                    │  │ Timestamp | Roll | Name  │  │
                    │  │ Links | Status | Reason  │  │
                    │  ├───────────────────────────┤  │
                    │  │ Auto-sorted by roll #    │  │
                    │  │ Thread-safe operations   │  │
                    │  └───────────────────────────┘  │
                    └─────────────────────────────────┘
```

---

## Evaluation Pipeline Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                        START EVALUATION                          │
│            Student: John Doe, Roll: 2021001                      │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
               ╔════════════════════════╗
               ║   STAGE 1: COURSERA    ║
               ║  verify_coursera_cert  ║
               ╚════════════╤═══════════╝
                            │
                 ┌──────────▼──────────┐
                 │ 1. Parse URL        │
                 │ 2. Launch browser   │
                 │ 3. Navigate to page │
                 │ 4. Wait for load    │
                 │ 5. Extract data     │
                 └──────────┬──────────┘
                            │
              ┌─────────────▼─────────────┐
              │   Certificate Valid?      │
              └─────────┬──────────┬──────┘
                       NO          YES
                        │           │
                        ▼           ▼
            ┌──────────────┐   ┌────────────────┐
            │   INVALID    │   │  Continue to   │
            │   ❌ STOP    │   │   Stage 2      │
            └──────────────┘   └────────┬───────┘
                                        │
                                        │
                  ╔════════════════════════╗
                  ║   STAGE 2: LINKEDIN    ║
                  ║ get_linkedin_obs()     ║
                  ╚════════════╤═══════════╝
                               │
                    ┌──────────▼──────────┐
                    │ 1. Fetch post       │
                    │ 2. Extract text     │
                    │ 3. Quick search     │
                    │    for project name │
                    └──────────┬──────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │  Project name in post?    │
                 └─────────┬──────────┬──────┘
                          YES         NO
                           │           │
                           ▼           ▼
              ┌──────────────┐   ┌────────────────┐
              │     PASS     │   │  Continue to   │
              │   ✓ STOP     │   │   Stage 3      │
              └──────────────┘   └────────┬───────┘
                                          │
                                          │
                       ╔════════════════════════╗
                       ║   STAGE 3: LLM MATCH   ║
                       ║ llm_project_context()  ║
                       ╚════════════╤═══════════╝
                                    │
                         ┌──────────▼──────────┐
                         │ 1. Build prompt     │
                         │ 2. Send to Gemini   │
                         │ 3. Get AI response  │
                         │ 4. Parse result     │
                         └──────────┬──────────┘
                                    │
                      ┌─────────────▼─────────────┐
                      │  AI finds context match?  │
                      └─────────┬──────────┬──────┘
                               YES         NO
                                │           │
                                ▼           ▼
                   ┌──────────────────┐ ┌────────────┐
                   │      PASS        │ │    FAIL    │
                   │ LLM Match (85%)  │ │ No match   │
                   │    ✓ STOP        │ │  ❌ STOP   │
                   └──────────────────┘ └────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  Save to database     │
                        │  data.csv             │
                        └───────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  Return to frontend   │
                        └───────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   EVALUATION END    │
                         └─────────────────────┘
```

---

## Data Flow Diagrams

### Flow 1: Individual Submission (SubmissionPage)

```
USER                    FRONTEND                  BACKEND                 TOOLS                   DATABASE
 │                         │                         │                      │                        │
 │   Fill Form             │                         │                      │                        │
 │═════════════════════>   │                         │                      │                        │
 │                         │                         │                      │                        │
 │   Click Submit          │                         │                      │                        │
 │─────────────────────>   │                         │                      │                        │
 │                         │                         │                      │                        │
 │                         │  POST /submit-eval      │                      │                        │
 │                         │═════════════════════>   │                      │                        │
 │                         │                         │                      │                        │
 │                         │                         │  verify_coursera()   │                        │
 │                         │                         │══════════════════>   │                        │
 │                         │                         │                      │                        │
 │                         │                         │  {status, project}   │                        │
 │                         │                         │<══════════════════   │                        │
 │                         │                         │                      │                        │
 │                         │                         │  get_linkedin_obs()  │                        │
 │                         │                         │══════════════════>   │                        │
 │                         │                         │                      │                        │
 │                         │                         │  {match, text}       │                        │
 │                         │                         │<══════════════════   │                        │
 │                         │                         │                      │                        │
 │                         │                         │  llm_match()         │                        │
 │                         │                         │══════════════════>   │                        │
 │                         │                         │                      │                        │
 │                         │                         │  {match, conf}       │                        │
 │                         │                         │<══════════════════   │                        │
 │                         │                         │                      │                        │
 │                         │                         │  add_submission()                             │
 │                         │                         │════════════════════════════════════════════>   │
 │                         │                         │                                               │
 │                         │                         │  Success                                      │
 │                         │                         │<════════════════════════════════════════════   │
 │                         │                         │                      │                        │
 │                         │  200 OK {status,...}    │                      │                        │
 │                         │<═════════════════════   │                      │                        │
 │                         │                         │                      │                        │
 │   Show Result           │                         │                      │                        │
 │<═════════════════════   │                         │                      │                        │
 │   PASS ✓                │                         │                      │                        │
 │                         │                         │                      │                        │

Timeline: ~20-40 seconds total
```

### Flow 2: Batch Evaluation (Report Page)

```
USER                FRONTEND                  BACKEND (SSE)              EVALUATOR              DATABASE
 │                     │                           │                         │                      │
 │ Enter Roll          │                           │                         │                      │
 │ Click Evaluate      │                           │                         │                      │
 │─────────────────>   │                           │                         │                      │
 │                     │                           │                         │                      │
 │                     │ EventSource created       │                         │                      │
 │                     │ GET /evaluate-stream/...  │                         │                      │
 │                     │═══════════════════════>   │                         │                      │
 │                     │                           │                         │                      │
 │                     │                           │ Load submissions        │                      │
 │                     │                           │ from submission2.csv    │                      │
 │                     │                           │                         │                      │
 │                     │                           │                         │                      │
 │                     │ ─── FOR EACH PROJECT ─────────────────────────────────────────────────────┐
 │                     │                           │                         │                      │
 │                     │ SSE: "Queued"             │                         │                      │
 │                     │<═══════════════════════   │                         │                      │
 │  Show "Queued"      │                           │                         │                      │
 │<─────────────────   │                           │                         │                      │
 │                     │                           │                         │                      │
 │                     │ SSE: "Evaluating"         │                         │                      │
 │                     │<═══════════════════════   │                         │                      │
 │  Show "Evaluating"  │                           │                         │                      │
 │<─────────────────   │                           │                         │                      │
 │                     │                           │                         │                      │
 │                     │                           │ evaluate_fast_phase()   │                      │
 │                     │                           │═════════════════════>   │                      │
 │                     │                           │                         │                      │
 │                     │                           │ {phase, result}         │                      │
 │                     │                           │<═════════════════════   │                      │
 │                     │                           │                         │                      │
 │                     │                           │ evaluate_llm_phase()    │                      │
 │                     │                           │ (if needed)             │                      │
 │                     │                           │═════════════════════>   │                      │
 │                     │                           │                         │                      │
 │                     │                           │ {verdict, reason}       │                      │
 │                     │                           │<═════════════════════   │                      │
 │                     │                           │                         │                      │
 │                     │ SSE: "Completed"          │                         │                      │
 │                     │      {verdict, reason}    │                         │                      │
 │                     │<═══════════════════════   │                         │                      │
 │  Show PASS/FAIL     │                           │                         │                      │
 │<─────────────────   │                           │                         │                      │
 │                     │                           │                         │                      │
 │                     │ ───────────────────────────────────────────────────────────────────────────┘
 │                     │                           │                         │                      │
 │                     │ SSE: "done"               │                         │                      │
 │                     │<═══════════════════════   │                         │                      │
 │  Show Final Grade   │                           │                         │                      │
 │<─────────────────   │                           │                         │                      │
 │   6/8 ✓             │                           │                         │                      │
 │                     │                           │                         │                      │

Timeline: ~(N projects × 30 seconds) total
```

---

## Component Interaction

### Frontend Component Hierarchy

```
App.jsx (Root)
│
├─ Routes
│  │
│  ├─ Route "/"
│  │  └─ HomePage
│  │     ├─ Header (orange gradient)
│  │     ├─ Input section (roll number)
│  │     ├─ Results table (streaming)
│  │     └─ Final grading section
│  │
│  ├─ Route "/submit"
│  │  └─ SubmissionPage
│  │     ├─ Form (4 inputs)
│  │     ├─ Submit button
│  │     └─ Result display
│  │
│  └─ Route "/guide"
│     └─ FailureReasons
│        ├─ INVALID section
│        ├─ Example images
│        └─ FAIL section
│
└─ BottomNavigation (fixed)
   ├─ Report icon
   ├─ Submit button (+)
   └─ Guide icon
```

### Backend Component Interaction

```
api/app.py (FastAPI)
│
├─ Endpoints
│  ├─ POST /submit-evaluation
│  │  └─> core/evaluator.evaluate_single_submission()
│  │      └─> tools/coursera_tool.py
│  │      └─> tools/linkedin_tool.py
│  │      └─> utils/context_project_match.py
│  │      └─> data_management/data_manager.add_submission()
│  │
│  ├─ GET /evaluate-stream/{roll}
│  │  └─> core/evaluator.evaluate_student_fast_phase()
│  │  └─> core/evaluator.evaluate_student_llm_phase()
│  │
│  ├─ GET /submissions
│  │  └─> data_management/data_manager.get_all_submissions()
│  │
│  └─ GET /submissions/stats
│     └─> data_management/data_manager.get_submission_stats()
│
└─ On Startup
   └─> data_management/data_manager.initialize_data_file()
```

### Data Management Module

```
data_management/
│
├─ __init__.py
│  └─ Exports all functions
│
├─ data_manager.py
│  │
│  ├─ initialize_data_file()
│  │  └─> Creates data.csv with sample data
│  │
│  ├─ add_submission()
│  │  └─> Adds & sorts by roll number
│  │  └─> Thread-safe with lock
│  │
│  ├─ get_all_submissions()
│  │  └─> Returns DataFrame
│  │
│  ├─ get_submissions_by_roll()
│  │  └─> Filters by roll number
│  │
│  ├─ get_submission_stats()
│  │  └─> Calculates statistics
│  │
│  └─ export_to_csv()
│     └─> Backup functionality
│
└─ data.csv
   └─ Persistent storage
```

---

## State Machine Diagram

### Submission States

```
                    ┌─────────────┐
                    │   INITIAL   │
                    │  (No data)  │
                    └──────┬──────┘
                           │
                           │ User fills form
                           │
                    ┌──────▼──────┐
                    │  VALIDATING │
                    │   (form)    │
                    └──────┬──────┘
                           │
                           │ All fields filled
                           │
                    ┌──────▼──────┐
                    │ SUBMITTING  │
                    │ (API call)  │
                    └──────┬──────┘
                           │
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │ SUCCESS  │  │ SUCCESS  │  │ SUCCESS  │
      │  (PASS)  │  │  (FAIL)  │  │(INVALID) │
      └──────────┘  └──────────┘  └──────────┘
             │             │             │
             └─────────────┼─────────────┘
                           │
                           │ Reset form
                           │
                    ┌──────▼──────┐
                    │   INITIAL   │
                    │  (reset)    │
                    └─────────────┘
```

### SSE Streaming States

```
    ┌─────────────┐
    │  CONNECTED  │
    └──────┬──────┘
           │
           │ For each project
           │
    ┌──────▼──────┐
    │   QUEUED    │
    └──────┬──────┘
           │
           │ Start evaluation
           │
    ┌──────▼──────┐
    │ EVALUATING  │
    └──────┬──────┘
           │
           │
     ┌─────┴─────┐
     │           │
     │ Fast?     │ LLM needed?
     │           │
     ▼           ▼
┌─────────┐  ┌─────────────┐
│COMPLETED│  │LLM VALIDATING│
└────┬────┘  └──────┬──────┘
     │              │
     │              │
     │              ▼
     │         ┌─────────┐
     │         │COMPLETED│
     │         └────┬────┘
     │              │
     └──────────────┘
           │
           │ More projects?
           │
      ┌────▼─────┐
      │   DONE   │
      └──────────┘
```

---

## Technology Stack Diagram

```
┌───────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                    │
│  ┌──────────────────────────────────────────────┐     │
│  │ React 19 + React Router + Tailwind CSS       │     │
│  │ • Component-based UI                         │     │
│  │ • Client-side routing                        │     │
│  │ • Responsive design                          │     │
│  │ • Dark/Light mode                            │     │
│  └──────────────────────────────────────────────┘     │
└─────────────────────┬─────────────────────────────────┘
                      │ HTTP/SSE
                      │
┌─────────────────────▼─────────────────────────────────┐
│                   API LAYER                            │
│  ┌──────────────────────────────────────────────┐     │
│  │ FastAPI + Pydantic + Uvicorn                 │     │
│  │ • RESTful endpoints                          │     │
│  │ • Server-Sent Events                         │     │
│  │ • Request validation                         │     │
│  │ • API documentation (Swagger)                │     │
│  └──────────────────────────────────────────────┘     │
└─────────────────────┬─────────────────────────────────┘
                      │
                      │
┌─────────────────────▼─────────────────────────────────┐
│                BUSINESS LOGIC LAYER                    │
│  ┌──────────────────────────────────────────────┐     │
│  │ Python Evaluation Pipeline                   │     │
│  │ • Sequential processing                      │     │
│  │ • Error handling                             │     │
│  │ • Validation logic                           │     │
│  └──────────────────────────────────────────────┘     │
└─────────────────────┬─────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────────┐
│ WEB      │   │ DATA     │   │ AI/ML        │
│ SCRAPING │   │ HANDLING │   │ INTEGRATION  │
│          │   │          │   │              │
│Playwright│   │ Pandas   │   │Google Gemini │
│Beautif...│   │ CSV ops  │   │   API        │
└──────────┘   └──────────┘   └──────────────┘
      │               │               │
      └───────────────┼───────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│                   DATA LAYER                         │
│  ┌──────────────────────────────────────────────┐   │
│  │ CSV File Storage                             │   │
│  │ • data_management/data.csv                   │   │
│  │ • submission2.csv                            │   │
│  │ • Thread-safe operations                     │   │
│  │ • Auto-sorted by roll number                 │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## Summary

This system uses:
- **Modern Frontend** (React + Tailwind)
- **Fast Backend** (FastAPI)
- **Intelligent Evaluation** (Multi-stage pipeline + AI)
- **Real-time Updates** (Server-Sent Events)
- **Organized Storage** (CSV with auto-sorting)

All working together to automate student project evaluation! 🚀
