# Data Management System

This folder contains the data management system for handling student submissions.

## Files

### `data.csv`
The main data storage file containing all submissions. Automatically maintained in sorted order by roll number.

**Columns:**
- `Timestamp`: Date and time of submission (YYYY-MM-DD HH:MM:SS)
- `Roll Number`: Student roll number
- `Name`: Student name
- `Coursera Certificate Link`: Link to Coursera certificate
- `LinkedIn Post Link`: Link to LinkedIn post
- `Status`: Evaluation result (PASS/FAIL/INVALID)
- `Reason`: Detailed reason for the status

### `data_manager.py`
Python module that provides functions for managing the data.

**Functions:**
- `initialize_data_file()`: Creates data.csv with sample data if it doesn't exist
- `add_submission()`: Adds a new submission and keeps data sorted by roll number
- `get_all_submissions()`: Returns all submissions as a DataFrame
- `get_submissions_by_roll()`: Returns submissions for a specific roll number
- `get_submission_stats()`: Returns statistics (total, pass, fail, invalid counts)
- `export_to_csv()`: Exports data to a custom CSV file

## Usage

### From Python Code

```python
from data_management import add_submission, get_all_submissions, get_submission_stats

# Add a new submission
add_submission(
    roll_number="2021006",
    name="John Doe",
    coursera_link="https://coursera.org/verify/ABC123",
    linkedin_link="https://www.linkedin.com/posts/johndoe-123",
    status="PASS",
    reason="LinkedIn post mentions the Coursera project."
)

# Get all submissions
df = get_all_submissions()
print(df)

# Get statistics
stats = get_submission_stats()
print(f"Total submissions: {stats['total']}")
print(f"Pass: {stats['pass']}")
print(f"Fail: {stats['fail']}")
print(f"Invalid: {stats['invalid']}")
```

### Via API Endpoints

```bash
# Submit a new evaluation
curl -X POST http://localhost:8000/submit-evaluation \
  -H "Content-Type: application/json" \
  -d '{
    "student_name": "John Doe",
    "roll_number": "2021006",
    "coursera_certificate_link": "https://coursera.org/verify/ABC123",
    "linkedin_post_link": "https://www.linkedin.com/posts/johndoe-123"
  }'

# Get all submissions
curl http://localhost:8000/submissions

# Get statistics
curl http://localhost:8000/submissions/stats
```

## Features

### Automatic Sorting
All submissions are automatically sorted by roll number when added, ensuring data is always organized.

### Thread-Safe Operations
The data manager uses thread locks to prevent race conditions when multiple submissions are processed concurrently.

### Sample Data
The system comes pre-initialized with 5 sample submissions to demonstrate the data structure:
- 3 PASS submissions (including LLM match)
- 1 FAIL submission
- 1 INVALID submission

## Data Integrity

- All write operations are protected by a thread lock
- Data is automatically sorted after each addition
- Timestamps are automatically generated
- Roll numbers are stored as strings to preserve leading zeros

## Backup and Export

To create a backup of the data:

```python
from data_management import export_to_csv

export_to_csv("backup/data_backup_2024.csv")
```

## Integration

This data management system is integrated with:
- **API (`api/app.py`)**: All submission endpoints use this system
- **Submission Evaluator (`submission_evaluator.py`)**: Command-line tool saves to this system
- **Core Evaluator (`core/evaluator.py`)**: Evaluation results are stored here
