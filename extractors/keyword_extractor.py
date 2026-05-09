"""
keyword_extractor.py
--------------------
Extracts meaningful keywords and skills from resume or JD text.

Strategy:
  1. Load a skills taxonomy (skills_taxonomy.json) as a known-skills dictionary.
  2. Match those known skills against the input text (fast, accurate).
  3. Also apply spaCy NLP to catch noun phrases not in the taxonomy.
  4. Return a deduplicated, normalized keyword list.
"""

import re
import json
import os

import spacy

# Load spaCy English model (small — fast enough for this use case)
# If not installed: python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError(
        "spaCy model 'en_core_web_sm' not found.\n"
        "Run: python -m spacy download en_core_web_sm"
    )

# Path to the skills taxonomy JSON
TAXONOMY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "matcher", "data", "skills_taxonomy.json"
)


def load_taxonomy() -> list:
    """Load the skills taxonomy list from JSON file."""
    if not os.path.exists(TAXONOMY_PATH):
        return []  # Graceful fallback if file missing
    with open(TAXONOMY_PATH, "r") as f:
        data = json.load(f)
    # Flatten all categories into a single list of skill strings
    skills = []
    for category in data.values():
        skills.extend([s.lower() for s in category])
    return skills


def normalize(text: str) -> str:
    """Lowercase and strip extra whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_taxonomy_matches(text: str, taxonomy: list) -> list:
    """
    Find all skills from taxonomy that appear in the text.
    Uses word-boundary regex for accuracy (avoids partial matches).
    """
    text_lower = text.lower()
    found = []
    for skill in taxonomy:
        # Escape special regex chars in skill name
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def extract_nlp_keywords(text: str) -> list:
    """
    Use spaCy to extract noun chunks and named entities
    as additional keywords beyond the taxonomy.
    """
    doc = nlp(text[:100000])  # Limit to 100k chars to avoid memory issues
    keywords = set()

    # Extract noun chunks (e.g., "machine learning", "project management")
    for chunk in doc.noun_chunks:
        cleaned = normalize(chunk.text)
        # Filter out very short or very long chunks
        if 2 <= len(cleaned.split()) <= 4:
            keywords.add(cleaned)

    # Extract named entities (ORG, PRODUCT — often tools/tech)
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT", "GPE", "LANGUAGE"):
            keywords.add(normalize(ent.text))

    return list(keywords)


def extract_keywords(text: str) -> list:
    """
    Main entry point.

    Combines taxonomy matching + spaCy NLP extraction.

    Args:
        text: Raw text from resume or JD.

    Returns:
        Deduplicated list of normalized keyword strings.
    """
    taxonomy = load_taxonomy()

    taxonomy_hits = extract_taxonomy_matches(text, taxonomy)
    nlp_hits = extract_nlp_keywords(text)

    # Merge and deduplicate
    all_keywords = set(taxonomy_hits) | set(nlp_hits)

    # Filter out single-character items and pure numbers
    filtered = [
        kw for kw in all_keywords
        if len(kw) > 1 and not kw.isdigit()
    ]

    return sorted(filtered)