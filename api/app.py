from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import asyncio
from datetime import datetime
import os
from core.evaluator import (
    evaluate_student_fast_phase,
    evaluate_student_llm_phase,
    evaluate_single_submission
)
from data_management import (
    add_submission,
    get_all_submissions,
    get_submission_stats,
    check_duplicate_submission,
    get_cached_evaluation_results,
    get_cached_result_for_submission,
    save_evaluation_result,
    initialize_data_file
)

# Initialize data file on startup
initialize_data_file()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Load submission file ONCE
# -------------------------
submission_df = pd.read_csv("submission2.csv")


class StudentQuery(BaseModel):
    roll_number: str
    full_name: str


class SubmissionRequest(BaseModel):
    student_name: str
    roll_number: str
    email_address: str
    coursera_certificate_link: str
    linkedin_post_link: str


# -------------------------
# NEW ENDPOINT: Submit Evaluation
# -------------------------
@app.post("/submit-evaluation")
async def submit_evaluation(request: SubmissionRequest):
    """
    Evaluates a single student submission and stores it in data.csv
    Checks for duplicates using binary search before evaluating.
    Data is automatically kept sorted by roll number.
    """

    try:
        # Check for duplicate submission using binary search
        is_duplicate = check_duplicate_submission(
            roll_number=request.roll_number,
            coursera_link=request.coursera_certificate_link,
            linkedin_link=request.linkedin_post_link
        )

        if is_duplicate:
            return {
                "status": "DUPLICATE",
                "error": "Record already exists",
                "message": f"A submission with the same roll number ({request.roll_number}) and links already exists in the database.",
                "duplicate": True
            }

        # Run evaluation (only if not duplicate)
        result = evaluate_single_submission(
            student_name=request.student_name,
            roll_number=request.roll_number,
            coursera_link=request.coursera_certificate_link,
            linkedin_link=request.linkedin_post_link
        )

        # Add submission to data.csv (automatically sorted by roll number)
        success = add_submission(
            roll_number=request.roll_number,
            name=request.student_name,
            email=request.email_address,
            coursera_link=request.coursera_certificate_link,
            linkedin_link=request.linkedin_post_link,
            status=result.get("status", "UNKNOWN"),
            reason=result.get("reason", ""),
            project=result.get("project", "-"),
            submitted_at=""  # Will auto-generate current timestamp
        )

        if not success:
            return {
                "error": "Failed to save submission to database"
            }

        # Get timestamp from the saved entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Return result to frontend
        return {
            "status": result.get("status"),
            "reason": result.get("reason"),
            "project": result.get("project"),
            "submitted_at": timestamp,
            "duplicate": False
        }

    except Exception as e:
        return {
            "error": str(e)
        }


@app.get("/evaluate-stream/{roll_number}")
async def evaluate_stream(roll_number: str):

    matches = submission_df[
        submission_df["Roll Number"].astype(str) == roll_number
    ].reset_index(drop=True)

    # -------------------------
    # No records found
    # -------------------------
    if matches.empty:
        async def error_stream():
            payload = {"error": "Roll number not found"}
            yield f"data: {json.dumps(payload)}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    # -------------------------
    # Main Stream Generator
    # -------------------------
    async def event_generator():

        for idx, row in matches.iterrows():

            # 1️⃣ Queued
            payload = {
                "row_id": idx,
                "status": "Queued"
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.1)

            # 2️⃣ Evaluating
            payload = {
                "row_id": idx,
                "status": "Evaluating"
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.1)

            # 3️⃣ FAST PHASE
            fast_result = evaluate_student_fast_phase(row)

            # -------------------------
            # Completed in FAST phase
            # -------------------------
            if fast_result["phase"] == "completed":

                payload = {
                    "row_id": idx,
                    "status": "Completed",
                    "result": {
                        "Status": fast_result["result"].get("verdict", "UNKNOWN"),
                        "Reason": fast_result["result"].get("reason", ""),
                        "Project": fast_result["result"].get("project", "-"),
                        "Submitted At": "",  # Will be set by save_evaluation_result
                        "Full Name": str(row.get("Full Name", "")),
                        "Email": str(row.get("Email Address", ""))
                    }
                }

                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.2)

                # Save result to data.csv for caching
                save_evaluation_result(
                    roll_number=str(row.get("Roll Number", "")),
                    name=str(row.get("Full Name", "")),
                    email=str(row.get("Email Address", "")),
                    coursera_link=str(row.get("Coursera completion certificate link", "")),
                    linkedin_link=str(row.get("LinkedIn Post Link", "")),
                    status=fast_result["result"].get("verdict", "UNKNOWN"),
                    reason=fast_result["result"].get("reason", ""),
                    project=fast_result["result"].get("project", "-"),
                    submitted_at=""  # Will auto-generate current timestamp
                )

                continue

            # -------------------------
            # LLM REQUIRED
            # -------------------------
            if fast_result["phase"] == "llm_required":

                # Notify frontend slow validation
                payload = {
                    "row_id": idx,
                    "status": "LLM Validation (may take 1-2 minutes)"
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.2)

                # Run LLM
                final_result = evaluate_student_llm_phase(
                    fast_result["data"]
                )

                payload = {
                    "row_id": idx,
                    "status": "Completed",
                    "result": {
                        "Status": final_result.get("verdict", "UNKNOWN"),
                        "Reason": final_result.get("reason", ""),
                        "Project": final_result.get("project", "-"),
                        "Submitted At": "",  # Will be set by save_evaluation_result
                        "Full Name": str(row.get("Full Name", "")),
                        "Email": str(row.get("Email Address", ""))
                    }
                }

                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.2)

                # Save result to data.csv for caching
                save_evaluation_result(
                    roll_number=str(row.get("Roll Number", "")),
                    name=str(row.get("Full Name", "")),
                    email=str(row.get("Email Address", "")),
                    coursera_link=str(row.get("Coursera completion certificate link", "")),
                    linkedin_link=str(row.get("LinkedIn Post Link", "")),
                    status=final_result.get("verdict", "UNKNOWN"),
                    reason=final_result.get("reason", ""),
                    project=final_result.get("project", "-"),
                    submitted_at=""  # Will auto-generate current timestamp
                )

        # Stream finished
        payload = {"done": True}
        yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# -------------------------
# EVALUATE ENDPOINT (With data.csv integration)
# -------------------------
@app.get("/evaluate-cached/{roll_number}")
async def evaluate_cached(roll_number: str):
    """
    Simple evaluation endpoint:
    - If status exists in data.csv: display it
    - If not: run evaluation, save, display
    """

    matches = submission_df[
        submission_df["Roll Number"].astype(str) == roll_number
    ].reset_index(drop=True)

    if matches.empty:
        async def error_stream():
            payload = {"error": "Roll number not found"}
            yield f"data: {json.dumps(payload)}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    async def event_generator():
        for idx, row in matches.iterrows():
            coursera_link = str(row.get("Coursera completion certificate link", ""))
            linkedin_link = str(row.get("LinkedIn Post Link", ""))

            # Check if status already exists in data.csv
            existing_result = get_cached_result_for_submission(
                roll_number=roll_number,
                coursera_link=coursera_link,
                linkedin_link=linkedin_link
            )

            if existing_result:
                # Display existing result
                payload = {
                    "row_id": idx,
                    "status": "Completed",
                    "result": {
                        "Status": existing_result["status"],
                        "Reason": existing_result["reason"],
                        "Project": existing_result.get("project", "-"),
                        "Submitted At": existing_result.get("submitted_at", ""),
                        "Full Name": existing_result["name"],
                        "Email": existing_result["email"]
                    }
                }
                yield f"data: {json.dumps(payload)}\n\n"
            else:
                # Run evaluation
                payload = {"row_id": idx, "status": "Evaluating"}
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.1)

                fast_result = evaluate_student_fast_phase(row)

                if fast_result["phase"] == "completed":
                    result = fast_result["result"]
                elif fast_result["phase"] == "llm_required":
                    result = evaluate_student_llm_phase(fast_result["data"])
                else:
                    result = {"verdict": "UNKNOWN", "reason": "Evaluation failed", "project": "-"}

                # Save to data.csv
                save_evaluation_result(
                    roll_number=str(row.get("Roll Number", "")),
                    name=str(row.get("Full Name", "")),
                    email=str(row.get("Email Address", "")),
                    coursera_link=coursera_link,
                    linkedin_link=linkedin_link,
                    status=result.get("verdict", "UNKNOWN"),
                    reason=result.get("reason", ""),
                    project=result.get("project", "-"),
                    submitted_at=""  # Will auto-generate current timestamp
                )

                # Display result
                payload = {
                    "row_id": idx,
                    "status": "Completed",
                    "result": {
                        "Status": result.get("verdict", "UNKNOWN"),
                        "Reason": result.get("reason", ""),
                        "Project": result.get("project", "-"),
                        "Submitted At": "",  # Will be set by data manager
                        "Full Name": str(row.get("Full Name", "")),
                        "Email": str(row.get("Email Address", ""))
                    }
                }
                yield f"data: {json.dumps(payload)}\n\n"

        payload = {"done": True}
        yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# -------------------------
# NEW ENDPOINTS: Data Management
# -------------------------
@app.get("/submissions")
async def get_submissions():
    """
    Get all submissions from data.csv (sorted by roll number)
    """
    try:
        df = get_all_submissions()
        return {
            "submissions": df.to_dict(orient="records"),
            "count": len(df)
        }
    except Exception as e:
        return {
            "error": str(e)
        }


@app.get("/submissions/stats")
async def get_stats():
    """
    Get submission statistics
    """
    try:
        stats = get_submission_stats()
        return stats
    except Exception as e:
        return {
            "error": str(e)
        }
