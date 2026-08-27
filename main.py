import math
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from queue import Queue
from typing import Any, Dict, List, Optional

import pandas as pd

from tools.coursera_tool import verify_coursera_certificate
from tools.linkedin_tool import get_linkedin_observations
from utils.context_project_match import llm_project_context_match
from utils.google_sheet_logger import append_result_live
from utils.google_sheet_logger import init_sheet


DEFAULT_FAST_WORKER_CAP = 32
DEFAULT_LLM_WORKER_CAP = 8
FAST_WORKER_MULTIPLIER = 4


@dataclass
class PipelineRuntime:
    results: List[Optional[Dict[str, Any]]]
    llm_queue: Queue
    counter_lock: threading.Lock = field(default_factory=threading.Lock)
    duplicate_lock: threading.Lock = field(default_factory=threading.Lock)
    fast_completed: int = 0
    llm_completed: int = 0


# -------------------------
# DEBUG STATUS LOGGER
# -------------------------
def debug_status(prefix, message):
    print(f"[{prefix}] {message}")


def _read_worker_override(env_name):
    raw_value = os.getenv(env_name, "").strip()

    if not raw_value:
        return None

    try:
        worker_count = int(raw_value)
    except ValueError:
        debug_status("CONFIG", f"Ignoring invalid {env_name}={raw_value!r}")
        return None

    if worker_count < 1:
        debug_status("CONFIG", f"Ignoring non-positive {env_name}={raw_value!r}")
        return None

    return worker_count


def calculate_worker_counts(record_count):
    logical_cores = os.cpu_count() or 1

    fast_default = max(
        1,
        min(DEFAULT_FAST_WORKER_CAP, logical_cores * FAST_WORKER_MULTIPLIER)
    )
    llm_default = max(
        1,
        min(DEFAULT_LLM_WORKER_CAP, math.ceil(logical_cores / 2))
    )

    fast_workers = _read_worker_override("PIPELINE_FAST_WORKERS") or fast_default
    llm_workers = _read_worker_override("PIPELINE_LLM_WORKERS") or llm_default

    fast_workers = min(record_count, fast_workers)
    llm_workers = min(record_count, llm_workers)

    return logical_cores, fast_workers, llm_workers


def select_input_subset(df):
    row_slice = os.getenv("PIPELINE_ROW_SLICE", "").strip()

    if not row_slice:
        return df.reset_index(drop=True)

    try:
        start_text, end_text = row_slice.split(":", 1)
        start = int(start_text) if start_text else None
        end = int(end_text) if end_text else None
    except ValueError:
        debug_status(
            "CONFIG",
            f"Ignoring invalid PIPELINE_ROW_SLICE={row_slice!r}; expected start:end"
        )
        return df.reset_index(drop=True)

    return df.iloc[start:end].reset_index(drop=True)


def handle_invalid_coursera_link(index, row, runtime, reason):
    result_entry = {
        "Roll Number": str(row["Roll Number"]).strip(),
        "Full Name": str(row["Full Name"]).strip(),
        "Coursera Project": "-",
        "Certificate Completion Date": "-",
        "Project Mention Match": False,
        "Final Verdict": "INVALID",
        "Failure Reason": reason,
        "Duplicate Certificate": False,
        "LLM Context Match": False,
        "LLM Confidence": 0,
    }

    runtime.results[index] = result_entry

    append_result_live([
        result_entry["Roll Number"],
        result_entry["Full Name"],
        result_entry["Coursera Project"],
        result_entry["Certificate Completion Date"],
        result_entry["Project Mention Match"],
        result_entry["Final Verdict"],
        result_entry["Failure Reason"]
    ])


# -------------------------
# LLM WORKER THREAD
# -------------------------
def llm_worker(runtime):

    worker_name = threading.current_thread().name
    debug_status("LLM", f"{worker_name} started")

    while True:

        task = runtime.llm_queue.get()

        if task is None:
            runtime.llm_queue.task_done()
            debug_status("LLM", f"{worker_name} stopped")
            break

        index, roll, name, coursera_project, completion_date, linkedin_description = task

        llm_match_result = llm_project_context_match(
            coursera_project,
            linkedin_description
        )

        if llm_match_result["match"]:
            verdict = "PASS"
            reason = f"LLM Context Match ({llm_match_result['confidence']}%)"
        else:
            verdict = "FAIL"
            reason = "LinkedIn post does not mention the Coursera project."

        results[index]["Final Verdict"] = verdict
        results[index]["Failure Reason"] = reason

        append_result_live([
            roll,
            name,
            coursera_project,
            completion_date,
            results[index]["Project Mention Match"],
            verdict,
            reason
        ])

        llm_queue.task_done()

        # ⭐ LLM COUNTER + STATUS
        with counter_lock:
            llm_completed += 1

            debug_status(
                "LLM",
                f"Completed: {llm_completed} | Remaining Queue: {llm_queue.qsize()}"
            )


# -------------------------
# FAST RECORD PROCESSING
# -------------------------
def process_fast_record(index, row, results, seen_certificates_by_roll):

    global fast_completed

    roll = row["Roll Number"]
    certificate_link = row["Coursera completion certificate link"].strip()

    coursera_data = verify_coursera_certificate(
        certificate_link,
        row["Full Name"]
    )

    coursera_project = coursera_data.get("coursera_project_name")
    completion_date = coursera_data.get("completion_date", "")
    
    status = coursera_data.get('Cert_Status')
    if status == 'Fail':
        handle_invalid_coursera_link(index, row, results)
    
    linkedin_data = get_linkedin_observations(
        row["LinkedIn Post Link"],
        row["Full Name"],
        coursera_project
    )

    if roll not in seen_certificates_by_roll:
        seen_certificates_by_roll[roll] = set()

    is_duplicate = certificate_link in seen_certificates_by_roll[roll]

    if not is_duplicate:
        seen_certificates_by_roll[roll].add(certificate_link)

    linkedin_description = linkedin_data.get("linkedin_description", "")

    result_entry = {
        "Roll Number": roll,
        "Full Name": row["Full Name"],
        "Coursera Project": coursera_project,
        "Certificate Completion Date": completion_date,
        "Project Mention Match": linkedin_data.get("project_match"),
        "Final Verdict": None,
        "Failure Reason": "",
        "Duplicate Certificate": is_duplicate,
        "LLM Context Match": False,
        "LLM Confidence": 0,
    }

    results[index] = result_entry
    current_index = index

    # -------------------------
    # FAST VERDICT LOGIC
    # -------------------------

    if is_duplicate:

        results[current_index]["Final Verdict"] = "FAIL"
        results[current_index]["Failure Reason"] = "Duplicate certificate"

        append_result_live([
            roll,
            row["Full Name"],
            coursera_project,
            completion_date,
            linkedin_data.get("project_match"),
            "FAIL",
            "Duplicate certificate"
        ])

    elif linkedin_data.get("project_match"):

        results[current_index]["Final Verdict"] = "PASS"

        append_result_live([
            roll,
            row["Full Name"],
            coursera_project,
            completion_date,
            linkedin_data.get("project_match"),
            "PASS",
            ""
        ])

    else:

        llm_queue.put((
            current_index,
            roll,
            row["Full Name"],
            coursera_project,
            completion_date,
            linkedin_description
        ))

    # ⭐ FAST COUNTER + STATUS
    with counter_lock:
        fast_completed += 1

        debug_status(
            "FAST",
            f"Completed: {fast_completed} | LLM Queue: {llm_queue.qsize()}"
        )


# -------------------------
# MAIN PIPELINE
# -------------------------
def run_pipeline(input_filename):

    input_path = os.path.join("data", "inputs", input_filename)
    df = pd.read_csv(input_path)

    init_sheet()

    results = []
    seen_certificates_by_roll = {}

    NUM_LLM_WORKERS = 2
    FAST_WORKERS = 4

    workers = []

    for _ in range(NUM_LLM_WORKERS):
        t = threading.Thread(target=llm_worker, args=(results,))
        t.start()
        workers.append(t)

    subset = df.iloc[4449:4451].reset_index(drop=True)

    results = [None] * len(subset)

    # FAST PARALLEL
    with ThreadPoolExecutor(max_workers=FAST_WORKERS) as executor:

        futures = []

        for idx, row in subset.iterrows():
            futures.append(
                executor.submit(
                    process_fast_record,
                    idx,
                    row,
                    results,
                    seen_certificates_by_roll
                )
            )


        for f in futures:
            f.result()

    debug_status("PIPELINE", "FAST processing finished")
    debug_status("PIPELINE", f"Waiting LLM completion | Pending: {llm_queue.qsize()}")

    llm_queue.join()

    for _ in workers:
        llm_queue.put(None)

    for w in workers:
        w.join()

    output_path = os.path.join("data", "outputs", "Final_Evaluation_8.csv")

    output_df = pd.DataFrame(results)

    output_df = output_df[[
        "Roll Number",
        "Full Name",
        "Coursera Project",
        "Certificate Completion Date",
        "Project Mention Match",
        "Final Verdict",
        "Failure Reason"
    ]]

    output_df.to_csv(output_path, index=False)

    debug_status("PIPELINE", "Evaluation Complete")


if __name__ == "__main__":
    run_pipeline("submission2.csv")
