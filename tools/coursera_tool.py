import re
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def _is_share_link(url: str) -> bool:
    """Return True if the URL is a coursera.org/share/ link."""
    return bool(re.search(r"coursera\.org/share/", url, re.IGNORECASE))


def _is_course_page_link(url: str) -> bool:
    """
    Return True if the URL points to a Coursera *course page* rather than
    a certificate/accomplishment.  e.g.
        coursera.org/learn/.../home/module/...
    These are NOT valid certificate links.
    """
    return bool(re.search(r"coursera\.org/learn/.+/home/", url, re.IGNORECASE))


def verify_coursera_certificate(url, expected_name=None):

    headers = {"User-Agent": "Mozilla/5.0"}

    # -------------------------
    # Quick reject: course-page URLs are never certificates
    # -------------------------
    if _is_course_page_link(url):
        return {
            "Cert_Status": "Fail",
            "coursera_project_name": '',
            "completion_date": '',
            "student_name_found": '',
        }

    # Determine whether this is a share link.
    # Share links render the student name via JavaScript so it will NOT
    # appear in the static HTML.  We therefore skip the name check for
    # share links and rely on OG-metadata presence instead.
    is_share = _is_share_link(url)

    try:
        # -------------------------
        # FAST EXTRACTION (Requests)
        # -------------------------
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # OG extraction
        og_data = {}
        for tag in soup.find_all("meta"):
            if tag.get("property", "").startswith("og:"):
                og_data[tag["property"]] = tag.get("content", "")

        project_name = og_data.get("og:title")
        completion_date = og_data.get("og:description")  # Often contains completion info

        if project_name:
            project_name = " ".join(project_name.split()[3:])

        # ---------------------------------------------------------
        # Share links: validate via OG metadata only (skip name check)
        # If og:title exists the certificate is real.
        # ---------------------------------------------------------
        if is_share:
            if og_data.get("og:title"):
                return {
                    "Cert_Status": "Success",
                    "coursera_project_name": project_name,
                    "completion_date": completion_date,
                    "student_name_found": True,  # trusted via OG
                }
            else:
                # Share link but no OG title → broken / invalid share hash
                return {
                    "Cert_Status": "Fail",
                    "coursera_project_name": '',
                    "completion_date": '',
                    "student_name_found": '',
                }

        # ---------------------------------------------------------
        # Non-share links (verify / certificate): use name check
        # ---------------------------------------------------------
        # Extract static page text
        page_text = soup.get_text(separator=" ")

        name_found = False

        if expected_name and expected_name.lower() in page_text.lower():
            name_found = True

        if not name_found and expected_name:
            return {
                "Cert_Status": "Fail",
                "coursera_project_name": '',
                "completion_date": '',
                "student_name_found": '',
            }
        
        return {
            "Cert_Status": "Success",
            "coursera_project_name": project_name,
            "completion_date": completion_date,
            "student_name_found": name_found,
        }

    except Exception as e:
        return {
            "Cert_Status": "Error",
            "error": str(e)
        }
