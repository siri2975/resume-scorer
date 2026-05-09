"""
keyword_extractor.py
--------------------
Extracts keywords using taxonomy matching only (no spaCy).
Compatible with Render free tier deployment.
"""

import re
import json
import os

TAXONOMY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "matcher", "data", "skills_taxonomy.json"
)

def load_taxonomy() -> list:
    if not os.path.exists(TAXONOMY_PATH):
        return []
    with open(TAXONOMY_PATH, "r") as f:
        data = json.load(f)
    skills = []
    for category in data.values():
        skills.extend([s.lower() for s in category])
    return skills

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())

def extract_keywords(text: str) -> list:
    taxonomy = load_taxonomy()
    text_lower = text.lower()
    found = []
    for skill in taxonomy:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))