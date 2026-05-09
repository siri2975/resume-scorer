"""
jd_parser.py
------------
Cleans and normalizes raw Job Description (JD) text submitted by the user.
Handles extra whitespace, special characters, and section detection.
"""

import re


def clean_text(text: str) -> str:
    """Remove extra whitespace, special characters, and normalize line breaks."""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-ASCII characters (e.g., fancy quotes, em-dashes)
    text = text.encode("ascii", errors="ignore").decode("ascii")

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing spaces from each line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()


def detect_sections(text: str) -> dict:
    """
    Attempt to identify common JD sections like Responsibilities,
    Requirements, Qualifications, Nice-to-Have, etc.

    Returns a dict mapping section names to their content.
    Useful for finer-grained keyword extraction later.
    """
    section_patterns = {
        "responsibilities": r"(responsibilities|what you.ll do|key duties|your role)",
        "requirements": r"(requirements|qualifications|what we.re looking for|must have|you should have)",
        "nice_to_have": r"(nice.to.have|bonus|preferred|plus|good to have)",
        "about_company": r"(about us|who we are|company overview)",
    }

    sections = {}
    lines = text.split("\n")
    current_section = "general"
    sections[current_section] = []

    for line in lines:
        matched = False
        for section_key, pattern in section_patterns.items():
            if re.search(pattern, line.lower()):
                current_section = section_key
                sections[current_section] = []
                matched = True
                break
        if not matched:
            sections[current_section].append(line)

    # Join lines back into strings
    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


def parse_jd(raw_text: str) -> dict:
    """
    Main entry point for JD parsing.

    Args:
        raw_text: Raw job description text pasted by the user.

    Returns:
        A dict with:
            - 'cleaned_text': normalized full JD text
            - 'sections': detected sections dict
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Job description text cannot be empty.")

    cleaned = clean_text(raw_text)
    sections = detect_sections(cleaned)

    return {
        "cleaned_text": cleaned,
        "sections": sections,
    }