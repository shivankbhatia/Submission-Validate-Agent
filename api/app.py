from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os
import logging
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
submission_df = pd.read_csv("./data_management/data.csv")


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

        evaluation_status = result.get("status", "UNKNOWN")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Only store in data.csv if the submission passed
        if evaluation_status == "PASS":
            success = add_submission(
                roll_number=request.roll_number,
                name=request.student_name,
                email=request.email_address,
                coursera_link=request.coursera_certificate_link,
                linkedin_link=request.linkedin_post_link,
                status=evaluation_status,
                reason=result.get("reason", ""),
                project=result.get("project", "-"),
                submitted_at=""  # Will auto-generate current timestamp
            )

            if not success:
                return {
                    "error": "Failed to save submission to database"
                }

        # Return result to frontend
        return {
            "status": evaluation_status,
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
                "status": "Queued",
                "full_name": str(row.get("Full Name", ""))
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.1)

            # 2️⃣ Evaluating
            payload = {
                "row_id": idx,
                "status": "Evaluating",
                "full_name": str(row.get("Full Name", ""))
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
                    "status": "LLM Validation (may take 1-2 minutes)",
                    "full_name": str(row.get("Full Name", ""))
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.2)

                # Run LLM in a thread pool to avoid blocking, and send heartbeats
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as pool:
                    llm_task = loop.run_in_executor(pool, evaluate_student_llm_phase, fast_result["data"])
                    
                    while not llm_task.done():
                        yield ": heartbeat\n\n"
                        await asyncio.sleep(15) # Heartbeat every 15 seconds
                    
                    final_result = await llm_task


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
@app.get("/evaluate-cached")
async def evaluate_cached(roll_number: str = "", name: str = "", target_link: str = "", force: bool = False):


    """
    Simple evaluation endpoint:
    - Matches by Roll Number OR Student Name from recent data.csv
    - Run evaluation, save, display
    """
    try:
        df = pd.read_csv("./data_management/data.csv", dtype={"Roll Number": str})
        df["Roll Number"] = df["Roll Number"].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    except Exception:
        df = pd.DataFrame()
        
    roll_number = roll_number.strip()
    name = name.strip()

    if roll_number and name:
        matches = df[(df["Roll Number"].astype(str) == roll_number) & (df["Full Name"].astype(str).str.lower().str.contains(name.lower(), na=False))].reset_index(drop=True)
    elif name:
        matches = df[df["Full Name"].astype(str).str.lower().str.contains(name.lower(), na=False)].reset_index(drop=True)
    else:
        matches = df[df["Roll Number"].astype(str) == roll_number].reset_index(drop=True)

    if target_link:
        # If a specific certificate is targeted, filter by normalized link
        norm_target = normalize_link(target_link)

        matches["Temp_Norm_Link"] = matches["Coursera completion certificate link"].apply(normalize_link)
        matches = matches[matches["Temp_Norm_Link"] == norm_target].reset_index(drop=True)
        matches = matches.drop(columns=["Temp_Norm_Link"])


    if matches.empty:
        async def error_stream():
            payload = {"error": "No records found for the given criteria."}
            yield f"data: {json.dumps(payload)}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    async def event_generator():
        yield f"data: {{ \"count\": {len(matches)} }}\n\n"
        for idx, row in matches.iterrows():
            coursera_link = str(row.get("Coursera completion certificate link", ""))
            linkedin_link = str(row.get("LinkedIn Post Link", ""))

            row_roll_number = str(row.get("Roll Number", "")).strip()
            
            # Check if status already exists in data.csv
            existing_result = get_cached_result_for_submission(
                roll_number=row_roll_number,
                coursera_link=coursera_link,
                linkedin_link=linkedin_link
            )

            if existing_result and not force:
                # Display existing result
                payload = {
                    "row_id": idx,
                    "status": "Completed",
                    "result": {
                        "Status": existing_result["status"],
                        "Reason": existing_result["reason"],
                        "Project": existing_result.get("project", "-"),
                        "Submitted At": existing_result.get("submitted_at", ""),
                        "Roll Number": row_roll_number,
                        "Full Name": existing_result["name"],
                        "Email": existing_result["email"],
                        "Coursera Link": coursera_link,
                        "LinkedIn Link": linkedin_link
                    }
                }


                yield f"data: {json.dumps(payload)}\n\n"
            else:
                # Run evaluation
                payload = {"row_id": idx, "status": "Queued", "full_name": str(row.get("Full Name", ""))}
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.1)

                payload = {"row_id": idx, "status": "Evaluating", "full_name": str(row.get("Full Name", ""))}
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.1)

                fast_result = evaluate_student_fast_phase(row, force_llm=force)

                if fast_result["phase"] == "completed":
                    result = fast_result["result"]
                elif fast_result["phase"] == "llm_required":
                    payload = {"row_id": idx, "status": "LLM Validation (may take 1-2 minutes)", "full_name": str(row.get("Full Name", ""))}
                    yield f"data: {json.dumps(payload)}\n\n"
                    await asyncio.sleep(0.2)
                    
                    # Run LLM in a thread pool to avoid blocking, and send heartbeats
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor() as pool:
                        llm_task = loop.run_in_executor(pool, evaluate_student_llm_phase, fast_result["data"])
                        
                        while not llm_task.done():
                            yield ": heartbeat\n\n"
                            await asyncio.sleep(15) # Heartbeat every 15 seconds
                        
                        result = await llm_task
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
                        "Roll Number": row_roll_number,
                        "Full Name": str(row.get("Full Name", "")),
                        "Email": str(row.get("Email Address", "")),
                        "Coursera Link": coursera_link,
                        "LinkedIn Link": linkedin_link
                    }
                }


                yield f"data: {json.dumps(payload)}\n\n"



        payload = {"done": True}
        yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# -------------------------
# NEW ENDPOINTS: Data Management
# -------------------------
@app.get("/student-records")
async def get_student_records(name: str):
    """
    Get count of records for a specific student name
    """
    try:
        # Read directly from data.csv to get the most up-to-date data
        df = pd.read_csv("./data_management/data.csv", dtype={"Roll Number": str})
        
        # Case insensitive exact match or partial match (let's do partial match or exact)
        # We'll use case-insensitive partial match to be forgiving
        if "Full Name" in df.columns:
            matches = df[df["Full Name"].str.lower().str.contains(name.lower(), na=False)]
            return {"student_name": name, "records_found": len(matches)}
        return {"student_name": name, "records_found": 0}
    except Exception as e:
        return {"error": str(e), "records_found": 0}

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



# -------------------------
# BATCH EVALUATE ALL RECORDS  (PARALLEL)
# -------------------------
@app.get("/batch-evaluate-all")
async def batch_evaluate_all(new_only: bool = False, start_from: int = 0):
    """
    Processes records in data_management/data.csv **in parallel**.
    If new_only is True, only processes records with an empty Status.
    Otherwise, processes all records that aren't PASS, FAIL, or INVALID.
    'start_from' allows skipping the first N records of the file.
    """
    NUM_WORKERS: int = os.cpu_count() or 4

    async def batch_generator():
        # --- Load CSV ---
        try:
            df = pd.read_csv("./data_management/data.csv", dtype={"Roll Number": str})
            df["Roll Number"] = df["Roll Number"].fillna("").astype(str).str.strip()
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Failed to read data.csv: {str(e)}'})}\n\n"
            return

        df["Status"] = df["Status"].fillna("").astype(str).str.strip()
        
        # Apply start_from offset if provided
        if start_from > 0:
            df = df.iloc[start_from:].copy()
            
        # Filter records to process
        if new_only:
            # Process records where Status is empty OR Project is '-'
            df_to_process = df[(df["Status"] == "")].copy()
        else:
            # Process records that haven't reached a final verdict OR have Project as '-'
            # This ensures we re-evaluate records with missing project names
            df_to_process = df[
                (~df["Status"].isin(["PASS", "FAIL", "INVALID"])) | 
                (df["Project"] == "-")
            ].copy()
            
        total = len(df_to_process)
        
        if total == 0:
            yield f"data: {json.dumps({'total': 0, 'type': 'init', 'workers': NUM_WORKERS})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'total': 0})}\n\n"
            return
        yield f"data: {json.dumps({'total': total, 'type': 'init', 'workers': NUM_WORKERS})}\n\n"

        # --- Build row payloads ---
        rows = [
            {
                "idx":            idx,
                "roll_number":    str(row.get("Roll Number", "")).strip(),
                "full_name":      str(row.get("Full Name", "")).strip(),
                "coursera_link":  str(row.get("Coursera completion certificate link", "")).strip(),
                "linkedin_link":  str(row.get("LinkedIn Post Link", "")).strip(),
                "email":          str(row.get("Email Address", "")).strip(),
            }
            for idx, row in df_to_process.iterrows()
        ]

        # ----------------------------------------------------------
        # WORKER: Fast phase only (Coursera + LinkedIn scrape + fuzzy)
        # Rows that would normally go to AI validation are finalized
        # here with placeholder values so the FAST pipeline keeps moving.
        # ----------------------------------------------------------
        def fast_evaluate_row(item: dict):
            """Run the FAST pipeline and finalize every row in this phase."""
            idx           = item["idx"]
            roll_number   = item["roll_number"]
            full_name     = item["full_name"]
            coursera_link = item["coursera_link"]
            linkedin_link = item["linkedin_link"]
            email         = item["email"]

            try:
                csv_row = {
                    "Roll Number": roll_number,
                    "Full Name": full_name,
                    "Coursera completion certificate link": coursera_link,
                    "LinkedIn Post Link": linkedin_link,
                    "Email Address": email,
                }
                fast_result = evaluate_student_fast_phase(csv_row)

                if fast_result["phase"] == "completed":
                    result = fast_result["result"]
                    save_evaluation_result(
                        roll_number=roll_number, name=full_name, email=email,
                        coursera_link=coursera_link, linkedin_link=linkedin_link,
                        status=result.get("verdict", "UNKNOWN"),
                        reason=result.get("reason", ""),
                        project=result.get("project", "-"),
                        submitted_at=""
                    )
                    payload = {
                        "row_id": idx, "type": "progress", "status": "Completed",
                        "roll_number": roll_number, "full_name": full_name,
                        "result": {
                            "Status": result.get("verdict", "UNKNOWN"),
                            "Reason": result.get("reason", ""),
                            "Project": result.get("project", "-"),
                            "Roll Number": roll_number,
                            "Full Name": full_name, "Email": email,
                        }
                    }
                    return payload, None  # Done — no LLM needed

                elif fast_result["phase"] == "llm_required":
                    llm_data = fast_result.get("data", {})
                    save_evaluation_result(
                        roll_number=roll_number, name=full_name, email=email,
                        coursera_link=coursera_link, linkedin_link=linkedin_link,
                        status="-", reason="-",
                        project=llm_data.get("project", "-"),
                        submitted_at=""
                    )
                    payload = {
                        "row_id": idx, "type": "progress", "status": "Completed",
                        "roll_number": roll_number, "full_name": full_name,
                        "result": {
                            "Status": "-",
                            "Reason": "-",
                            "Project": llm_data.get("project", "-"),
                            "Roll Number": roll_number,
                            "Full Name": full_name, "Email": email,
                        }
                    }
                    return payload, None

                else:
                    result = {"verdict": "UNKNOWN", "reason": "Evaluation failed", "project": "-"}
                    save_evaluation_result(
                        roll_number=roll_number, name=full_name, email=email,
                        coursera_link=coursera_link, linkedin_link=linkedin_link,
                        status="UNKNOWN", reason="Evaluation failed",
                        project="-", submitted_at=""
                    )
                    payload = {
                        "row_id": idx, "type": "progress", "status": "Completed",
                        "roll_number": roll_number, "full_name": full_name,
                        "result": {
                            "Status": "UNKNOWN", "Reason": "Evaluation failed",
                            "Project": "-", "Roll Number": roll_number,
                            "Full Name": full_name, "Email": email,
                        }
                    }
                    return payload, None

            except Exception as e:
                return {
                    "row_id": idx, "type": "progress", "status": "Error",
                    "roll_number": roll_number, "full_name": full_name,
                    "error": str(e)
                }, None

        # --- Stream "Queued" events for all rows up front ---
        for item in rows:
            queued_payload = {
                "row_id":     item["idx"],
                "type":       "progress",
                "status":     "Queued",
                "roll_number": item["roll_number"],
                "full_name":   item["full_name"],
            }
            yield f"data: {json.dumps(queued_payload)}\n\n"
        await asyncio.sleep(0.05)

        # ==========================================================
        #  PHASE 1 — Fast pipeline (all threads, full concurrency)
        #  Rows that would require AI evaluation are written with
        #  placeholder Status/Reason values and processing continues.
        # ==========================================================
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            futures = {executor.submit(fast_evaluate_row, item): item for item in rows}

            for future in as_completed(futures):
                payload, _ = future.result()
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0)

        # ==========================================================
        #  PHASE 2 — LLM validation (all threads, full concurrency)
        #  No fast work is competing, so all cores go to AI inference.
        # ==========================================================
        yield f"data: {json.dumps({'type': 'done', 'total': total})}\n\n"

    return StreamingResponse(batch_generator(), media_type="text/event-stream")


@app.get("/batch-evaluate-ai-pending")
async def batch_evaluate_ai_pending(start_from: int = 0):
    """
    Runs AI validation only for rows in data.csv that were marked with
    placeholder status '-' during the FAST-only batch pipeline.
    Now processes in parallel for better performance and reliability.
    'start_from' allows skipping the first N records of the file.
    """
    """
    Runs AI validation only for rows in data.csv that were marked with
    placeholder status '-' during the FAST-only batch pipeline.
    Now processes in parallel for better performance and reliability.
    """
    NUM_WORKERS: int = os.cpu_count() or 4

    async def batch_generator():
        try:
            df = pd.read_csv("./data_management/data.csv", dtype={"Roll Number": str})
            df["Roll Number"] = df["Roll Number"].fillna("").astype(str).str.strip()
            df["Status"] = df["Status"].fillna("").astype(str).str.strip()
            
            # Apply start_from offset if provided
            if start_from > 0:
                df = df.iloc[start_from:].copy()
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Failed to read data.csv: {str(e)}'})}\n\n"
            return

        # Identify pending AI tasks
        pending_df = df[df["Status"] == "-"].copy()
        total = len(pending_df)
        
        if total == 0:
            yield f"data: {json.dumps({'total': 0, 'type': 'init', 'workers': NUM_WORKERS})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'total': 0})}\n\n"
            return
            
        yield f"data: {json.dumps({'total': total, 'type': 'init', 'workers': NUM_WORKERS})}\n\n"

        rows = [
            {
                "idx": idx,
                "roll_number": str(row.get("Roll Number", "")).strip(),
                "full_name": str(row.get("Full Name", "")).strip(),
                "coursera_link": str(row.get("Coursera completion certificate link", "")).strip(),
                "linkedin_link": str(row.get("LinkedIn Post Link", "")).strip(),
                "email": str(row.get("Email Address", "")).strip(),
            }
            for idx, row in pending_df.iterrows()
        ]

        def evaluate_pending_ai_row(item: dict):
            idx = item["idx"]
            roll_number = item["roll_number"]
            full_name = item["full_name"]
            coursera_link = item["coursera_link"]
            linkedin_link = item["linkedin_link"]
            email = item["email"]

            try:
                csv_row = {
                    "Roll Number": roll_number,
                    "Full Name": full_name,
                    "Coursera completion certificate link": coursera_link,
                    "LinkedIn Post Link": linkedin_link,
                    "Email Address": email,
                }

                # We already know it needs AI (Status was "-")
                # but we call evaluate_student_fast_phase to get the data required for LLM
                fast_result = evaluate_student_fast_phase(csv_row)

                if fast_result["phase"] == "completed":
                    result = fast_result["result"]
                elif fast_result["phase"] == "llm_required":
                    result = evaluate_student_llm_phase(fast_result["data"])
                else:
                    result = {
                        "verdict": "UNKNOWN",
                        "reason": "Evaluation failed",
                        "project": "-",
                    }

                save_evaluation_result(
                    roll_number=roll_number,
                    name=full_name,
                    email=email,
                    coursera_link=coursera_link,
                    linkedin_link=linkedin_link,
                    status=result.get("verdict", "UNKNOWN"),
                    reason=result.get("reason", ""),
                    project=result.get("project", "-"),
                    submitted_at=""
                )

                return {
                    "row_id": idx,
                    "type": "progress",
                    "status": "Completed",
                    "roll_number": roll_number,
                    "full_name": full_name,
                    "result": {
                        "Status": result.get("verdict", "UNKNOWN"),
                        "Reason": result.get("reason", ""),
                        "Project": result.get("project", "-"),
                        "Roll Number": roll_number,
                        "Full Name": full_name,
                        "Email": email,
                    }
                }, None
            except Exception as e:
                return {
                    "row_id": idx,
                    "type": "progress",
                    "status": "Error",
                    "roll_number": roll_number,
                    "full_name": full_name,
                    "error": str(e),
                }, None

        # --- Stream "Queued" events ---
        for item in rows:
            queued_payload = {
                "row_id": item["idx"],
                "type": "progress",
                "status": "Queued",
                "roll_number": item["roll_number"],
                "full_name": item["full_name"],
            }
            yield f"data: {json.dumps(queued_payload)}\n\n"
        await asyncio.sleep(0.05)

        # --- Parallel Processing ---
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            futures = {executor.submit(evaluate_pending_ai_row, item): item for item in rows}

            for future in as_completed(futures):
                payload, _ = future.result()
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0)

        yield f"data: {json.dumps({'type': 'done', 'total': total})}\n\n"

    return StreamingResponse(batch_generator(), media_type="text/event-stream")


@app.get("/batch-evaluate-invalid")
async def batch_evaluate_invalid(start_from: int = 0):
    """
    Runs evaluation only for rows in data.csv that were marked with
    status 'INVALID'.
    Processes in parallel.
    'start_from' allows skipping the first N records of the file.
    """
    NUM_WORKERS: int = os.cpu_count() or 4

    async def batch_generator():
        try:
            df = pd.read_csv("./data_management/data.csv", dtype={"Roll Number": str})
            df["Roll Number"] = df["Roll Number"].fillna("").astype(str).str.strip()
            df["Status"] = df["Status"].fillna("").astype(str).str.strip()
            
            # Apply start_from offset if provided
            if start_from > 0:
                df = df.iloc[start_from:].copy()
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Failed to read data.csv: {str(e)}'})}\n\n"
            return

        # Identify INVALID tasks
        invalid_df = df[df["Status"] == "INVALID"].copy()
        total = len(invalid_df)
        
        if total == 0:
            yield f"data: {json.dumps({'total': 0, 'type': 'init', 'workers': NUM_WORKERS})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'total': 0})}\n\n"
            return
            
        yield f"data: {json.dumps({'total': total, 'type': 'init', 'workers': NUM_WORKERS})}\n\n"

        rows = [
            {
                "idx": idx,
                "roll_number": str(row.get("Roll Number", "")).strip(),
                "full_name": str(row.get("Full Name", "")).strip(),
                "coursera_link": str(row.get("Coursera completion certificate link", "")).strip(),
                "linkedin_link": str(row.get("LinkedIn Post Link", "")).strip(),
                "email": str(row.get("Email Address", "")).strip(),
            }
            for idx, row in invalid_df.iterrows()
        ]

        def evaluate_invalid_row(item: dict):
            idx = item["idx"]
            roll_number = item["roll_number"]
            full_name = item["full_name"]
            coursera_link = item["coursera_link"]
            linkedin_link = item["linkedin_link"]
            email = item["email"]

            try:
                csv_row = {
                    "Roll Number": roll_number,
                    "Full Name": full_name,
                    "Coursera completion certificate link": coursera_link,
                    "LinkedIn Post Link": linkedin_link,
                    "Email Address": email,
                }

                fast_result = evaluate_student_fast_phase(csv_row)

                if fast_result["phase"] == "completed":
                    result = fast_result["result"]
                elif fast_result["phase"] == "llm_required":
                    result = evaluate_student_llm_phase(fast_result["data"])
                else:
                    result = {
                        "verdict": "UNKNOWN",
                        "reason": "Evaluation failed",
                        "project": "-",
                    }

                save_evaluation_result(
                    roll_number=roll_number,
                    name=full_name,
                    email=email,
                    coursera_link=coursera_link,
                    linkedin_link=linkedin_link,
                    status=result.get("verdict", "UNKNOWN"),
                    reason=result.get("reason", ""),
                    project=result.get("project", "-"),
                    submitted_at=""
                )

                return {
                    "row_id": idx,
                    "type": "progress",
                    "status": "Completed",
                    "roll_number": roll_number,
                    "full_name": full_name,
                    "result": {
                        "Status": result.get("verdict", "UNKNOWN"),
                        "Reason": result.get("reason", ""),
                        "Project": result.get("project", "-"),
                        "Roll Number": roll_number,
                        "Full Name": full_name,
                        "Email": email,
                    }
                }, None
            except Exception as e:
                return {
                    "row_id": idx,
                    "type": "progress",
                    "status": "Error",
                    "roll_number": roll_number,
                    "full_name": full_name,
                    "error": str(e),
                }, None

        # --- Stream "Queued" events ---
        for item in rows:
            queued_payload = {
                "row_id": item["idx"],
                "type": "progress",
                "status": "Queued",
                "roll_number": item["roll_number"],
                "full_name": item["full_name"],
            }
            yield f"data: {json.dumps(queued_payload)}\n\n"
        await asyncio.sleep(0.05)

        # --- Parallel Processing ---
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            futures = {executor.submit(evaluate_invalid_row, item): item for item in rows}

            for future in as_completed(futures):
                payload, _ = future.result()
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0)

        yield f"data: {json.dumps({'type': 'done', 'total': total})}\n\n"

    return StreamingResponse(batch_generator(), media_type="text/event-stream")


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
