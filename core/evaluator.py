from tools.coursera_tool import verify_coursera_certificate
from tools.linkedin_tool import get_linkedin_observations
from utils.context_project_match import llm_project_context_match


# -------------------------
# NEW SINGLE SUBMISSION EVALUATOR (following main.py pipeline)
# -------------------------
def evaluate_single_submission(student_name: str, roll_number: str,
                               coursera_link: str, linkedin_link: str):
    """
    Evaluates a single submission following the sequential pipeline from main.py:
    1. Verify Coursera certificate
    2. Get LinkedIn observations
    3. Determine verdict based on project match or LLM validation
    """

    # Step 1: Verify Coursera Certificate
    coursera_data = verify_coursera_certificate(coursera_link, student_name)

    status = coursera_data.get('Cert_Status')

    # Handle invalid Coursera link
    if status == 'Fail':
        return {
            "status": "INVALID",
            "reason": "Coursera link is invalid.",
            "project": "-",
            "completion_date": "-"
        }

    coursera_project = coursera_data.get("coursera_project_name", "-")
    completion_date = coursera_data.get("completion_date", "-")

    # Step 2: Get LinkedIn Observations
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
        return {
            "status": "PASS",
            "reason": "LinkedIn post mentions the Coursera project.",
            "project": coursera_project,
            "completion_date": completion_date
        }

    # Otherwise, use LLM for context matching
    llm_result = llm_project_context_match(
        coursera_project,
        linkedin_description
    )

    if llm_result.get("match"):
        return {
            "status": "PASS",
            "reason": f"LLM Context Match ({llm_result.get('confidence', 0)}%)",
            "project": coursera_project,
            "completion_date": completion_date
        }

    # If no match found, FAIL
    return {
        "status": "FAIL",
        "reason": "LinkedIn post does not mention the Coursera project.",
        "project": coursera_project,
        "completion_date": completion_date
    }


# -------------------------
# EXISTING FUNCTIONS FOR STREAMING EVALUATION
# -------------------------
def evaluate_student_fast_phase(row: dict):
    print("START FAST PHASE")

    roll = row["Roll Number"]
    full_name = row["Full Name"]
    certificate_link = row["Coursera completion certificate link"].strip()

    # 1️⃣ Verify Coursera
    print("Calling Coursera")
    coursera_data = verify_coursera_certificate(
        certificate_link,
        full_name
    )

    if coursera_data.get("Cert_Status") == "Fail":
        return {
            "phase": "completed",
            "result": {
                "roll_number": roll,
                "full_name": full_name,
                "project": "-",
                "verdict": "INVALID",
                "reason": "Coursera link is invalid."
            }
        }

    coursera_project = coursera_data.get("coursera_project_name")

    # 2️⃣ LinkedIn Fast Match
    print("Calling LinkedIn")
    linkedin_data = get_linkedin_observations(
        row["LinkedIn Post Link"],
        full_name,
        coursera_project
    )
    print("LinkedIn Done")


    if linkedin_data.get("project_match"):
        return {
            "phase": "completed",
            "result": {
                "roll_number": roll,
                "full_name": full_name,
                "project": coursera_project,
                "verdict": "PASS",
                "reason": "LinkedIn post mentions the Coursera project."
            }
        }

    # If fast match failed → need LLM
    return {
        "phase": "llm_required",
        "data": {
            "roll": roll,
            "full_name": full_name,
            "project": coursera_project,
            "linkedin_description": linkedin_data.get("linkedin_description", "")
        }
    }

def evaluate_student_llm_phase(data: dict):

    llm_result = llm_project_context_match(
        data["project"],
        data["linkedin_description"]
    )

    if llm_result.get("match"):
        return {
            "roll_number": data["roll"],
            "full_name": data["full_name"],
            "project": data["project"],
            "verdict": "PASS",
            "reason": f"LLM Context Match ({llm_result.get('confidence', 0)}%)"
        }

    return {
        "roll_number": data["roll"],
        "full_name": data["full_name"],
        "project": data["project"],
        "verdict": "FAIL",
        "reason": "LinkedIn post does not mention the Coursera project."
    }
