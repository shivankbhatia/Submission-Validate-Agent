import re
from tools.coursera_tool import verify_coursera_certificate
from tools.linkedin_tool import get_linkedin_observations
from utils.context_project_match import llm_project_context_match


def is_linkedin_post_url(url: str) -> bool:
    """
    Returns True if the URL points to an actual LinkedIn *post*.
    Rejects bare profile pages (linkedin.com/in/username).

    Accepted patterns:
      - linkedin.com/posts/...
      - linkedin.com/feed/update/urn:li:activity:...
      - linkedin.com/feed/update/urn:li:share:...
      - linkedin.com/feed/update/urn:li:ugcPost:...
      - linkedin.com/pulse/...  (articles)
      - any URL containing 'ugcPost' in query params

    Rejected patterns:
      - linkedin.com/in/username
      - linkedin.com/in/username/overlay/...
    """
    if not url or not isinstance(url, str):
        return False
    url_lower = url.strip().lower()
    # Must at least be a LinkedIn URL
    if "linkedin.com" not in url_lower:
        return False
    # Positive signals — any of these means it's a post
    post_patterns = [
        r"linkedin\.com/posts/",
        r"linkedin\.com/feed/update/",
        r"linkedin\.com/pulse/",
        r"ugcpost",
    ]
    for pattern in post_patterns:
        if re.search(pattern, url_lower):
            return True
    # If none matched → it's likely just a profile link
    return False



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

    # Handle network/scraping errors
    if status == 'Error':
        return {
            "status": "INVALID",
            "reason": f"Coursera verification error: {coursera_data.get('error', 'unknown')}",
            "project": "-",
            "completion_date": "-"
        }

    coursera_project = coursera_data.get("coursera_project_name", "-")
    completion_date = coursera_data.get("completion_date", "-")

    # Step 2: Validate LinkedIn URL is a post (not a profile page)
    if not is_linkedin_post_url(linkedin_link):
        return {
            "status": "FAIL",
            "reason": "LinkedIn link is a profile page, not a post.",
            "project": coursera_project,
            "completion_date": completion_date
        }

    # Step 3: Get LinkedIn Observations
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
def evaluate_student_fast_phase(row: dict, force_llm: bool = False):
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

    if coursera_data.get("Cert_Status") == "Error":
        return {
            "phase": "completed",
            "result": {
                "roll_number": roll,
                "full_name": full_name,
                "project": "-",
                "verdict": "INVALID",
                "reason": f"Coursera verification error: {coursera_data.get('error', 'unknown')}"
            }
        }

    coursera_project = coursera_data.get("coursera_project_name")

    # 2️⃣ Validate LinkedIn URL is a post (not a profile page)
    linkedin_url = str(row["LinkedIn Post Link"]).strip()
    if not is_linkedin_post_url(linkedin_url):
        return {
            "phase": "completed",
            "result": {
                "roll_number": roll,
                "full_name": full_name,
                "project": coursera_project,
                "verdict": "FAIL",
                "reason": "LinkedIn link is a profile page, not a post."
            }
        }

    # 3️⃣ LinkedIn Fast Match
    print("Calling LinkedIn")
    linkedin_data = get_linkedin_observations(
        linkedin_url,
        full_name,
        coursera_project
    )
    print("LinkedIn Done")


    if not force_llm and linkedin_data.get("project_match"):
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

    try:
        llm_result = llm_project_context_match(
            data["project"],
            data["linkedin_description"]
        )
    except Exception as e:
        # Ollama/LLM service unavailable — keep as AI-pending so it can be retried
        print(f"[ERROR] LLM phase failed for {data.get('full_name', '?')}: {e}")
        return {
            "roll_number": data["roll"],
            "full_name": data["full_name"],
            "project": data["project"],
            "verdict": "-",
            "reason": f"LLM service unavailable – will retry later"
        }

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
