"""
Single Submission Evaluator Script

This script:
1. Collects roll number, student name, coursera certificate link, linkedin post link, and timestamp
2. Runs evaluator using coursera_tool.py then linkedin_tool.py sequentially
3. Creates output with status and reason
4. Stores data in data_management/data.csv (sorted by roll number)

Usage:
    python submission_evaluator.py
"""

import pandas as pd
import os
from datetime import datetime
from tools.coursera_tool import verify_coursera_certificate
from tools.linkedin_tool import get_linkedin_observations
from utils.context_project_match import llm_project_context_match
from data_management import add_submission, get_submission_stats


def evaluate_submission(student_name, roll_number, coursera_link, linkedin_link):
    """
    Sequential evaluation pipeline following main.py structure:
    1. Verify Coursera certificate
    2. Get LinkedIn observations
    3. Determine verdict (PASS/FAIL/INVALID)
    """

    print(f"\n{'='*60}")
    print(f"Evaluating submission for: {student_name} ({roll_number})")
    print(f"{'='*60}\n")

    # Step 1: Verify Coursera Certificate
    print("Step 1: Verifying Coursera Certificate...")
    coursera_data = verify_coursera_certificate(coursera_link, student_name)

    status = coursera_data.get('Cert_Status')

    # Handle invalid Coursera link
    if status == 'Fail':
        print("❌ INVALID: Coursera link is invalid.\n")
        return {
            "status": "INVALID",
            "reason": "Coursera link is invalid.",
            "project": "-",
            "completion_date": "-"
        }

    coursera_project = coursera_data.get("coursera_project_name", "-")
    completion_date = coursera_data.get("completion_date", "-")
    print(f"✓ Coursera Certificate Valid")
    print(f"  Project: {coursera_project}")
    print(f"  Completion Date: {completion_date}\n")

    # Step 2: Get LinkedIn Observations
    print("Step 2: Analyzing LinkedIn Post...")
    linkedin_data = get_linkedin_observations(
        linkedin_link,
        student_name,
        coursera_project
    )

    project_match = linkedin_data.get("project_match", False)
    linkedin_description = linkedin_data.get("linkedin_description", "")

    # Step 3: Determine Verdict

    # If LinkedIn post mentions the project directly, PASS
    if project_match:
        print("✓ Direct project mention found in LinkedIn post")
        print("✅ PASS\n")
        return {
            "status": "PASS",
            "reason": "LinkedIn post mentions the Coursera project.",
            "project": coursera_project,
            "completion_date": completion_date
        }

    # Otherwise, use LLM for context matching
    print("Step 3: Running LLM Context Match (this may take 1-2 minutes)...")
    llm_result = llm_project_context_match(
        coursera_project,
        linkedin_description
    )

    if llm_result.get("match"):
        confidence = llm_result.get('confidence', 0)
        print(f"✓ LLM Context Match Found (Confidence: {confidence}%)")
        print("✅ PASS\n")
        return {
            "status": "PASS",
            "reason": f"LLM Context Match ({confidence}%)",
            "project": coursera_project,
            "completion_date": completion_date
        }

    # If no match found, FAIL
    print("❌ FAIL: LinkedIn post does not mention the Coursera project.\n")
    return {
        "status": "FAIL",
        "reason": "LinkedIn post does not mention the Coursera project.",
        "project": coursera_project,
        "completion_date": completion_date
    }


def save_to_csv(student_name, roll_number, coursera_link, linkedin_link, result):
    """
    Save submission data to data_management/data.csv
    Data is automatically sorted by roll number.
    """

    success = add_submission(
        roll_number=roll_number,
        name=student_name,
        coursera_link=coursera_link,
        linkedin_link=linkedin_link,
        status=result.get("status", "UNKNOWN"),
        reason=result.get("reason", "")
    )

    if success:
        print(f"✓ Submission saved to database")
    else:
        print(f"❌ Failed to save submission to database")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


def main():
    """
    Main function to collect input and run evaluation
    """

    print("\n" + "="*60)
    print("  COURSERA GUIDED PROJECT SUBMISSION EVALUATOR")
    print("="*60 + "\n")

    # Collect input
    print("Please enter the following details:\n")

    student_name = input("Student Name: ").strip()
    roll_number = input("Roll Number: ").strip()
    coursera_link = input("Coursera Certificate Link: ").strip()
    linkedin_link = input("LinkedIn Post Link: ").strip()

    # Validate inputs
    if not all([student_name, roll_number, coursera_link, linkedin_link]):
        print("\n❌ Error: All fields are required!")
        return

    # Run evaluation
    result = evaluate_submission(
        student_name,
        roll_number,
        coursera_link,
        linkedin_link
    )

    # Save to CSV
    timestamp = save_to_csv(
        student_name,
        roll_number,
        coursera_link,
        linkedin_link,
        result
    )

    # Display final result
    print("\n" + "="*60)
    print("  EVALUATION COMPLETE")
    print("="*60)
    print(f"\nStudent: {student_name}")
    print(f"Roll Number: {roll_number}")
    print(f"Project: {result.get('project')}")
    print(f"Completion Date: {result.get('completion_date')}")
    print(f"Status: {result.get('status')}")
    print(f"Reason: {result.get('reason')}")
    print(f"Timestamp: {timestamp}")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
