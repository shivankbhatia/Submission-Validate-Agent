# 🚀 Application Startup Guide

This guide will help you start the Agentic Evaluator application successfully.

## Prerequisites

Before starting, ensure you have:
- Python 3.8+ installed
- Node.js 16+ and npm installed
- All dependencies installed

## Quick Start (Windows)

### Option 1: Using Batch Files (Recommended)

1. **Start the API Server** (in Terminal 1):
   ```bash
   start_api.bat
   ```
   - The API will start on `http://localhost:8000`
   - You should see: "Uvicorn running on http://0.0.0.0:8000"

2. **Start the Frontend** (in Terminal 2):
   ```bash
   start_frontend.bat
   ```
   - The frontend will start on `http://localhost:5173` (or similar)
   - Your browser should open automatically

3. **Access the Application**:
   - Open `http://localhost:5173` in your browser
   - You should see the application with the orange theme

### Option 2: Manual Start

**Terminal 1 - API Server:**
```bash
# From the project root directory
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
# From the project root directory
cd frontend
npm run dev
```

## Quick Start (Linux/Mac)

1. **Make scripts executable** (first time only):
   ```bash
   chmod +x start_api.sh
   ```

2. **Start the API Server** (Terminal 1):
   ```bash
   ./start_api.sh
   ```

3. **Start the Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

## Installation (First Time Setup)

### Backend Setup

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright (for web scraping):**
   ```bash
   playwright install
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory with:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node Dependencies:**
   ```bash
   npm install
   ```

3. **Environment Configuration:**
   The `.env` file should already exist in `frontend/.env` with:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

## Verifying the Setup

### Check API Server

Once the API is running, visit:
- **API Docs:** `http://localhost:8000/docs`
- **Health Check:** Try the endpoints in the Swagger UI

You should see these endpoints:
- `POST /submit-evaluation` - Submit new evaluation
- `GET /evaluate-stream/{roll_number}` - Stream evaluation results
- `GET /submissions` - Get all submissions
- `GET /submissions/stats` - Get statistics

### Check Frontend

Once the frontend is running, you should see:
- **Bottom Navigation Bar** with Report, Submit (+), and Guide icons
- **Orange theme** with rounded corners
- **Three pages:**
  - Report Page (/) - For evaluating student records
  - Submission Page (/submit) - For new submissions
  - Guide Page (/guide) - Evaluation guidelines

## Troubleshooting

### 404 Error on Evaluate Button

**Problem:** Getting 404 error when clicking "Evaluate" button

**Solutions:**
1. ✅ **Ensure API server is running:**
   - Check Terminal 1 for API server logs
   - Visit `http://localhost:8000/docs` - should show API documentation

2. ✅ **Check frontend .env file:**
   - File location: `frontend/.env`
   - Should contain: `VITE_API_URL=http://localhost:8000`

3. ✅ **Restart the frontend after creating .env:**
   ```bash
   # Stop the frontend (Ctrl+C)
   # Then restart:
   cd frontend
   npm run dev
   ```

4. ✅ **Verify API endpoint exists:**
   - Go to `http://localhost:8000/docs`
   - Look for `/evaluate-stream/{roll_number}` endpoint
   - Try testing it directly in Swagger UI

### Port Already in Use

**Problem:** Error "Address already in use" on port 8000 or 5173

**Solution:**
- **Windows:** Find and kill the process
  ```bash
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```
- **Linux/Mac:** Find and kill the process
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```

### Module Not Found Errors

**Problem:** Python modules not found when starting API

**Solution:**
```bash
pip install -r requirements.txt
playwright install
```

### CORS Errors

**Problem:** CORS errors in browser console

**Solution:** The API is already configured for CORS. Ensure:
1. Frontend is using `http://localhost:5173`
2. API is using `http://localhost:8000`
3. Both servers are running

### Data Management Issues

**Problem:** Submissions not saving

**Solution:**
1. Check that `data_management/data.csv` exists
2. Check file permissions
3. Review API server logs for errors

## Application Features

### 1. Report Page (/)
- Enter a roll number to evaluate all their submissions
- Shows real-time streaming evaluation
- Displays pass/fail status with reasons
- Shows final grade calculation

### 2. Submission Page (/submit)
- Submit individual evaluations
- Fill in: Student Name, Roll Number, Coursera Link, LinkedIn Link
- Get instant Pass/Fail/Invalid results
- Results are saved to `data_management/data.csv`

### 3. Guide Page (/guide)
- View evaluation criteria
- See examples of correct/incorrect certificate links
- Understand failure reasons

## Data Storage

All submissions are stored in:
- **File:** `data_management/data.csv`
- **Format:** Sorted by roll number
- **Fields:** Timestamp, Roll Number, Name, Links, Status, Reason

## API Endpoints

### POST /submit-evaluation
Submit a new evaluation and get results

**Request Body:**
```json
{
  "student_name": "John Doe",
  "roll_number": "2021001",
  "coursera_certificate_link": "https://coursera.org/verify/...",
  "linkedin_post_link": "https://linkedin.com/posts/..."
}
```

**Response:**
```json
{
  "status": "PASS",
  "reason": "LinkedIn post mentions the Coursera project.",
  "project": "Project Name",
  "completion_date": "2024-01-15",
  "timestamp": "2024-01-15 10:30:00"
}
```

### GET /evaluate-stream/{roll_number}
Stream evaluation results for a roll number (Server-Sent Events)

### GET /submissions
Get all submissions from database

### GET /submissions/stats
Get submission statistics

## Development Tips

1. **Use --reload flag** for automatic server restart on code changes
2. **Check API logs** in Terminal 1 for debugging
3. **Check browser console** for frontend errors
4. **Use API docs** at `http://localhost:8000/docs` for testing endpoints

## Need Help?

If you encounter issues:
1. Check both terminal windows for error messages
2. Verify all prerequisites are installed
3. Ensure both servers are running
4. Check the `.env` files are configured correctly
5. Try restarting both servers

## Next Steps

After starting the application:
1. Try the Submit page to test individual submissions
2. Try the Report page with a roll number from submission2.csv
3. Check the Guide page for evaluation criteria
4. View submissions in `data_management/data.csv`

Happy Evaluating! 🎓
