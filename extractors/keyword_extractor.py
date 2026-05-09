import re
import json
import os

TAXONOMY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "matcher", "data", "skills_taxonomy.json"
)

def load_taxonomy():
    if not os.path.exists(TAXONOMY_PATH):
        return []
    with open(TAXONOMY_PATH, "r") as f:
        data = json.load(f)
    skills = []
    for category in data.values():
        skills.extend([s.lower() for s in category])
    return skills

def extract_keywords(text):
    taxonomy = load_taxonomy()
    text_lower = text.lower()
    found = []
    for skill in taxonomy:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))