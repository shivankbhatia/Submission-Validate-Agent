"""
Data Management Module

This module handles all data operations for submission management:
- Initializing data.csv with proper structure
- Adding new submissions
- Maintaining data sorted by roll number
- Reading and filtering data
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, Optional
import threading

# Thread lock for concurrent write operations
data_lock = threading.Lock()

# Path to the main data file
DATA_FILE = os.path.join("data_management", "data.csv")


def normalize_roll_number(roll: str) -> str:
    """Standardizes roll numbers by removing .0 and stripping whitespace."""
    if not roll or not isinstance(roll, str):
        return str(roll or "").strip()
    return str(roll).strip().replace(".0", "")


def normalize_link(link: str) -> str:
    """Strips protocol, www, trailing slashes and query params for comparison."""
    if not link:
        return ""
    l = str(link).lower().strip()
    # Remove protocol
    if "://" in l:
        l = l.split("://")[1]
    # Remove www.
    if l.startswith("www."):
        l = l[4:]
    # Remove query parameters
    l = l.split("?")[0]
    # Remove trailing slash
    if l.endswith("/"):
        l = l[:-1]
    return l



def initialize_data_file():
    """
    Initialize data.csv with proper column structure if it doesn't exist.
    If file exists, validates and cleans up duplicate columns.
    """

    # Define the required columns (matching actual data.csv structure)
    columns = [
        "Timestamp",
        "Email Address",
        "Full Name",
        "Roll Number",
        "Coursera completion certificate link",
        "LinkedIn Post Link",
        "Project",
        "Submitted At",
        "Status",
        "Reason"
    ]

    if not os.path.exists(DATA_FILE):
        # Create new file with sample data
        sample_data = [
            {
                "Timestamp": "2024-01-15 10:30:00",
                "Email Address": "sample1@example.com",
                "Full Name": "John Doe",
                "Roll Number": "2021001",
                "Coursera completion certificate link": "https://coursera.org/verify/sample1",
                "LinkedIn Post Link": "https://www.linkedin.com/posts/johndoe-sample1",
                "Project": "Sample Project 1",
                "Submitted At": "2024-01-15 10:30:00",
                "Status": "PASS",
                "Reason": "LinkedIn post mentions the Coursera project."
            },
            {
                "Timestamp": "2024-01-15 11:45:00",
                "Email Address": "sample2@example.com",
                "Full Name": "Jane Smith",
                "Roll Number": "2021002",
                "Coursera completion certificate link": "https://coursera.org/verify/sample2",
                "LinkedIn Post Link": "https://www.linkedin.com/posts/janesmith-sample2",
                "Project": "Sample Project 2",
                "Submitted At": "2024-01-15 11:45:00",
                "Status": "FAIL",
                "Reason": "LinkedIn post does not mention the Coursera project."
            },
            {
                "Timestamp": "2024-01-15 12:15:00",
                "Email Address": "sample3@example.com",
                "Full Name": "Alice Johnson",
                "Roll Number": "2021003",
                "Coursera completion certificate link": "https://coursera.org/verify/sample3",
                "LinkedIn Post Link": "https://www.linkedin.com/posts/alicejohnson-sample3",
                "Project": "Sample Project 3",
                "Submitted At": "2024-01-15 12:15:00",
                "Status": "PASS",
                "Reason": "LLM Context Match (85%)"
            },
            {
                "Timestamp": "2024-01-15 14:20:00",
                "Email Address": "sample4@example.com",
                "Full Name": "Bob Williams",
                "Roll Number": "2021004",
                "Coursera completion certificate link": "https://invalid-link",
                "LinkedIn Post Link": "https://www.linkedin.com/posts/bobwilliams-sample4",
                "Project": "-",
                "Submitted At": "2024-01-15 14:20:00",
                "Status": "INVALID",
                "Reason": "Coursera link is invalid."
            },
            {
                "Timestamp": "2024-01-15 15:30:00",
                "Email Address": "sample5@example.com",
                "Full Name": "Charlie Brown",
                "Roll Number": "2021005",
                "Coursera completion certificate link": "https://coursera.org/verify/sample5",
                "LinkedIn Post Link": "https://www.linkedin.com/posts/charliebrown-sample5",
                "Project": "Sample Project 5",
                "Submitted At": "2024-01-15 15:30:00",
                "Status": "PASS",
                "Reason": "LinkedIn post mentions the Coursera project."
            }
        ]

        df = pd.DataFrame(sample_data, columns=columns)
        df = df.sort_values("Roll Number")
        df.to_csv(DATA_FILE, index=False)
        print(f"[OK] Initialized {DATA_FILE} with sample data")
        # File exists - clean up duplicate columns if any
        try:
            df = pd.read_csv(DATA_FILE, dtype={"Roll Number": str})
            df["Roll Number"] = df["Roll Number"].apply(normalize_roll_number)


            # Remove duplicate columns
            columns_to_remove = ["Name", "Coursera Certificate Link"]
            modified = False
            for col in columns_to_remove:
                if col in df.columns:
                    df = df.drop(columns=[col])
                    modified = True
                    print(f"[OK] Removed duplicate column: {col}")

            # Save if modified
            if modified:
                df.to_csv(DATA_FILE, index=False)
                print(f"[OK] Cleaned up {DATA_FILE}")
            else:
                print(f"[OK] {DATA_FILE} already exists and is valid")
        except Exception as e:
            print(f"[WARNING] Could not clean up {DATA_FILE}: {str(e)}")


def add_submission(roll_number: str, name: str, email: str, coursera_link: str,
                  linkedin_link: str, status: str, reason: str = "",
                  project: str = "-", submitted_at: str = "") -> bool:
    """
    Add a new submission to data.csv and keep it sorted by roll number.

    Args:
        roll_number: Student roll number
        name: Student name
        email: Student email address
        coursera_link: Coursera certificate link
        linkedin_link: LinkedIn post link
        status: Evaluation status (PASS/FAIL/INVALID)
        reason: Reason for the status
        project: Coursera project/course name
        submitted_at: Submission timestamp (will be auto-generated if not provided)

    Returns:
        True if successful, False otherwise
    """

    with data_lock:
        try:
            # Generate timestamp in datetime format (YYYY-MM-DD HH:MM:SS)
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

            # Use provided submitted_at or current timestamp
            if not submitted_at:
                submitted_at = timestamp

            # Create new entry with correct column names
            new_entry = {
                "Timestamp": timestamp,
                "Email Address": email,
                "Full Name": name,
                "Roll Number": roll_number,
                "Coursera completion certificate link": coursera_link,
                "LinkedIn Post Link": linkedin_link,
                "Project": project,
                "Submitted At": submitted_at,
                "Status": status,
                "Reason": reason
            }

            # Read existing data
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE, dtype={"Roll Number": str})
            else:
                initialize_data_file()
                df = pd.read_csv(DATA_FILE, dtype={"Roll Number": str})

            # Append new entry
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

            # Ensure Roll Number is string type and normalized before sorting
            df["Roll Number"] = df["Roll Number"].apply(normalize_roll_number)

            # Sort by roll number
            df = df.sort_values("Roll Number")

            # Save to file
            df.to_csv(DATA_FILE, index=False)

            print(f"[OK] Added submission for {name} ({roll_number})")
            return True

        except Exception as e:
            print(f"[ERROR] Error adding submission: {str(e)}")
            return False


def get_all_submissions() -> pd.DataFrame:
    """
    Get all submissions from data.csv

    Returns:
        DataFrame with all submissions sorted by roll number
    """

    if not os.path.exists(DATA_FILE):
        initialize_data_file()

    df = pd.read_csv(DATA_FILE, dtype={"Roll Number": str})
    df["Roll Number"] = df["Roll Number"].apply(normalize_roll_number)
    return df.sort_values("Roll Number")


def get_submissions_by_roll(roll_number: str) -> pd.DataFrame:
    """
    Get all submissions for a specific roll number

    Args:
        roll_number: Student roll number

    Returns:
        DataFrame with matching submissions
    """

    df = get_all_submissions()
    return df[df["Roll Number"] == roll_number]


def check_duplicate_submission(roll_number: str, coursera_link: str,
                               linkedin_link: str) -> bool:
    """
    Check if a submission already exists using binary search on sorted roll numbers.

    Args:
        roll_number: Student roll number
        coursera_link: Coursera certificate link
        linkedin_link: LinkedIn post link

    Returns:
        True if duplicate exists, False otherwise
    """

    if not os.path.exists(DATA_FILE):
        return False

    df = pd.read_csv(DATA_FILE, dtype={"Roll Number": str})

    if df.empty:
        return False

    # Ensure Roll Number is string and get sorted list
    df["Roll Number"] = df["Roll Number"].apply(normalize_roll_number)
    df = df.sort_values("Roll Number").reset_index(drop=True)

    # Binary search for roll number
    roll_numbers = df["Roll Number"].tolist()

    # Find first occurrence of roll_number using binary search
    left, right = 0, len(roll_numbers) - 1
    first_match = -1

    while left <= right:
        mid = (left + right) // 2
        if roll_numbers[mid] == roll_number:
            first_match = mid
            right = mid - 1  # Continue searching left for first occurrence
        elif roll_numbers[mid] < roll_number:
            left = mid + 1
        else:
            right = mid - 1

    # If roll number not found
    if first_match == -1:
        return False

    # Normalize input links for comparison
    norm_coursera = normalize_link(coursera_link)
    norm_linkedin = normalize_link(linkedin_link)

    coursera_col = "Coursera completion certificate link"
    linkedin_col = "LinkedIn Post Link"

    idx = first_match
    while idx < len(df) and df.loc[idx, "Roll Number"] == roll_number:
        existing_coursera = normalize_link(df.loc[idx, coursera_col])
        existing_linkedin = normalize_link(df.loc[idx, linkedin_col])
        existing_status = str(df.loc[idx, "Status"]).strip().upper()

        # 1. Match for either link (blocked if already passed or duplicate)
        # Students shouldn't reuse certificates OR LinkedIn posts for the same roll number
        if existing_coursera == norm_coursera:
            # If they already passed this specific certificate, it's a hard duplicate
            if existing_status == "PASS":
                return True
            # If it's the exact same link and post, it's also a duplicate
            if existing_linkedin == norm_linkedin:
                return True
            
        if existing_linkedin == norm_linkedin and existing_status == "PASS":
            return True
            
        idx += 1

    return False


def get_submission_stats() -> Dict:
    """
    Get statistics about submissions

    Returns:
        Dictionary with stats (total, pass, fail, invalid counts)
    """

    df = get_all_submissions()

    stats = {
        "total": len(df),
        "pass": len(df[df["Status"] == "PASS"]),
        "fail": len(df[df["Status"] == "FAIL"]),
        "invalid": len(df[df["Status"] == "INVALID"]),
        "unique_students": df["Roll Number"].nunique()
    }

    return stats


def get_cached_evaluation_results(roll_number: str) -> Optional[Dict]:
    """
    Get cached evaluation results for a student from data.csv

    Args:
        roll_number: Student roll number

    Returns:
        Dictionary with cached results if found, None otherwise
    """

    if not os.path.exists(DATA_FILE):
        return None

    df = pd.read_csv(DATA_FILE, dtype={"Roll Number": str})
    df["Roll Number"] = df["Roll Number"].apply(normalize_roll_number)


    # Get all entries for this roll number
    matches = df[df["Roll Number"] == roll_number]

    if matches.empty:
        return None

    # Return the results as a list of evaluations
    results = []
    for _, row in matches.iterrows():
        # Skip rows without status (old data before evaluation)
        if pd.isna(row.get("Status")) or row.get("Status") == "":
            continue

        results.append({
            "timestamp": row.get("Timestamp", ""),
            "email": row.get("Email Address", ""),
            "name": row.get("Full Name", ""),
            "roll_number": row.get("Roll Number", ""),
            "coursera_link": row.get("Coursera completion certificate link", ""),
            "linkedin_link": row.get("LinkedIn Post Link", ""),
            "status": row.get("Status", ""),
            "reason": row.get("Reason", "")
        })

    return results if results else None


def get_cached_result_for_submission(roll_number: str, coursera_link: str,
                                     linkedin_link: str) -> Optional[Dict]:
    """
    Get cached evaluation result for a specific submission by matching links.

    Args:
        roll_number: Student roll number
        coursera_link: Coursera certificate link
        linkedin_link: LinkedIn post link

    Returns:
        Dictionary with cached result if found, None otherwise
    """

    if not os.path.exists(DATA_FILE):
        return None

    df = pd.read_csv(DATA_FILE, dtype={"Roll Number": str})
    df["Roll Number"] = df["Roll Number"].apply(normalize_roll_number)


    coursera_col = "Coursera completion certificate link"
    linkedin_col = "LinkedIn Post Link"

    # Find exact match by roll number and both links
    # Find match by normalized roll number and both links
    # This is more expensive but robust
    df["Norm_Roll"] = df["Roll Number"].apply(normalize_roll_number)
    df["Norm_Coursera"] = df[coursera_col].apply(normalize_link)
    df["Norm_Linkedin"] = df[linkedin_col].apply(normalize_link)

    norm_roll = normalize_roll_number(roll_number)
    norm_coursera = normalize_link(coursera_link)
    norm_linkedin = normalize_link(linkedin_link)

    matches = df[
        (df["Norm_Roll"] == norm_roll) &
        (df["Norm_Coursera"] == norm_coursera) &
        (df["Norm_Linkedin"] == norm_linkedin)
    ]

    if matches.empty:
        return None

    # Get the first (and should be only) match
    row = matches.iloc[0]

    # Check if it has status/reason (i.e., has been evaluated)
    status_val = row.get("Status")
    reason_val = row.get("Reason")

    # Return None if Status is missing, empty, NaN, or "UNKNOWN"
    # or if Reason is NaN or empty
    if (pd.isna(status_val) or
        status_val == "" or
        str(status_val).upper() == "UNKNOWN" or
        pd.isna(reason_val) or
        reason_val == ""):
        return None

    return {
        "timestamp": row.get("Timestamp", ""),
        "email": row.get("Email Address", ""),
        "name": row.get("Full Name", ""),
        "roll_number": row.get("Roll Number", ""),
        "coursera_link": row.get(coursera_col, ""),
        "linkedin_link": row.get(linkedin_col, ""),
        "project": row.get("Project", "-"),
        "submitted_at": row.get("Submitted At", ""),
        "status": row.get("Status", ""),
        "reason": row.get("Reason", "")
    }


def save_evaluation_result(roll_number: str, name: str, email: str,
                           coursera_link: str, linkedin_link: str,
                           status: str, reason: str,
                           project: str = "-", submitted_at: str = "") -> bool:
    """
    Save evaluation result to data.csv by updating existing row or adding new one.
    Updates in-place if the submission exists but lacks Status/Reason.

    Args:
        roll_number: Student roll number
        name: Student name
        email: Student email address
        coursera_link: Coursera certificate link
        linkedin_link: LinkedIn post link
        status: Evaluation status (PASS/FAIL/INVALID)
        reason: Reason for the status
        project: Coursera project/course name
        submitted_at: Submission timestamp (will be auto-generated if not provided)

    Returns:
        True if successful, False otherwise
    """

    print(f"[DEBUG] Saving - Status: {status}, Reason: {reason[:50] if reason else 'None'}")

    with data_lock:
        try:
            # Read existing data
            if not os.path.exists(DATA_FILE):
                initialize_data_file()

            df = pd.read_csv(DATA_FILE, dtype={"Roll Number": str})
            df["Roll Number"] = df["Roll Number"].apply(normalize_roll_number)


            coursera_col = "Coursera completion certificate link"
            linkedin_col = "LinkedIn Post Link"

            # Check if this exact submission already exists
            # Check if this exact submission already exists using normalized matching
            df["Norm_Roll"] = df["Roll Number"].apply(normalize_roll_number)
            df["Norm_Coursera"] = df[coursera_col].apply(normalize_link)
            df["Norm_Linkedin"] = df[linkedin_col].apply(normalize_link)

            norm_roll = normalize_roll_number(roll_number)
            norm_coursera = normalize_link(coursera_link)
            norm_linkedin = normalize_link(linkedin_link)

            matching_rows = df[
                (df["Norm_Roll"] == norm_roll) &
                (df["Norm_Coursera"] == norm_coursera) &
                (df["Norm_Linkedin"] == norm_linkedin)
            ]

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

            # Use provided submitted_at or current timestamp
            if not submitted_at:
                submitted_at = timestamp

            if not matching_rows.empty:
                # Row exists - update it with Status, Reason, Project, and Submitted At
                idx = matching_rows.index[0]
                df.loc[idx, "Status"] = status
                df.loc[idx, "Reason"] = reason
                df.loc[idx, "Project"] = project
                df.loc[idx, "Submitted At"] = submitted_at
                df.loc[idx, "Timestamp"] = timestamp  # Update timestamp
                print(f"[OK] Updated evaluation result for {name} ({roll_number}) - Status: {status}")
            else:
                # Row doesn't exist - add new entry
                new_entry = {
                    "Timestamp": timestamp,
                    "Email Address": email,
                    "Full Name": name,
                    "Roll Number": roll_number,
                    coursera_col: coursera_link,
                    linkedin_col: linkedin_link,
                    "Project": project,
                    "Submitted At": submitted_at,
                    "Status": status,
                    "Reason": reason
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                print(f"[OK] Added evaluation result for {name} ({roll_number}) - Status: {status}")

            # Remove duplicate columns if they exist
            columns_to_remove = ["Name", "Coursera Certificate Link"]
            for col in columns_to_remove:
                if col in df.columns:
                    df = df.drop(columns=[col])

            # Ensure Roll Number is string type before sorting
            df["Roll Number"] = df["Roll Number"].astype(str)

            # Sort by roll number
            df = df.sort_values("Roll Number")

            # Drop normalization columns before saving
            df = df.drop(columns=["Norm_Roll", "Norm_Coursera", "Norm_Linkedin"], errors='ignore')

            # Save to file
            df.to_csv(DATA_FILE, index=False)
            print(f"[OK] Saved to {DATA_FILE}")

            return True

        except Exception as e:
            print(f"[ERROR] Error saving evaluation result: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def export_to_csv(output_path: str) -> bool:
    """
    Export data to a custom CSV file

    Args:
        output_path: Path to export file

    Returns:
        True if successful, False otherwise
    """

    try:
        df = get_all_submissions()
        df.to_csv(output_path, index=False)
        print(f"[OK] Exported data to {output_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error exporting data: {str(e)}")
        return False


# Initialize on module import
if __name__ != "__main__":
    initialize_data_file()
