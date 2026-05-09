"""
scorer.py
---------
Core matching and scoring engine.

Takes resume keywords and JD keywords, computes:
  - Overall match score (0-100)
  - Matched skills
  - Missing skills
  - Score label (Poor / Fair / Good / Excellent)
  - Section-level breakdown
  - Improvement suggestions
"""

import json
import os
import re
from typing import Optional

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data", "config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

WEIGHTS = CONFIG["scoring"]["weights"]
THRESHOLDS = CONFIG["scoring"]["thresholds"]

# Experience-level keywords for section scoring
EXPERIENCE_KEYWORDS = [
    "years of experience", "year experience", "senior", "junior", "lead",
    "manager", "director", "intern", "entry level", "mid-level", "principal",
    "architect", "head of", "vp", "vice president"
]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "degree", "diploma", "b.tech", "m.tech",
    "b.e", "m.e", "b.sc", "m.sc", "mba", "certification", "certified",
    "bootcamp", "associate degree"
]


def normalize_keyword_list(keywords: list) -> set:
    """Lowercase and strip all keywords for comparison."""
    return {kw.strip().lower() for kw in keywords if kw}


def compute_overlap(resume_kws: set, jd_kws: set) -> tuple:
    """
    Returns (matched, missing, match_ratio).
    matched  = skills in both resume and JD
    missing  = skills in JD but NOT in resume
    """
    matched = resume_kws & jd_kws
    missing = jd_kws - resume_kws
    ratio = len(matched) / len(jd_kws) if jd_kws else 0.0
    return matched, missing, ratio


def get_score_label(score: float) -> str:
    """Convert numeric score to human-readable label."""
    if score >= THRESHOLDS["good"]:
        return "Excellent"
    elif score >= THRESHOLDS["fair"]:
        return "Good"
    elif score >= THRESHOLDS["poor"]:
        return "Fair"
    else:
        return "Poor"


def score_skills_section(resume_kws: set, jd_kws: set) -> dict:
    """Score based purely on skills keyword overlap."""
    matched, missing, ratio = compute_overlap(resume_kws, jd_kws)
    score = round(ratio * 100, 1)
    return {
        "score": score,
        "matched_count": len(matched),
        "total_jd_skills": len(jd_kws),
        "reason": f"{len(matched)} of {len(jd_kws)} JD skills found in resume."
    }


def score_keyword_coverage(resume_text: str, jd_text: str) -> dict:
    """
    Score based on how many important JD words appear anywhere in the resume.
    Focuses on single important words (not just extracted keywords).
    """
    # Extract all meaningful words from JD (length > 3, not stopwords)
    stopwords = {
        "with", "that", "this", "have", "from", "they", "will", "your",
        "more", "also", "when", "been", "into", "their", "which", "about",
        "able", "other", "some", "such", "than", "then", "there", "these",
        "those", "must", "should", "would", "could", "being", "each",
        "after", "before", "where", "while"
    }
    jd_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", jd_text.lower()))
    jd_words -= stopwords

    resume_lower = resume_text.lower()
    found_words = {w for w in jd_words if re.search(r"\b" + re.escape(w) + r"\b", resume_lower)}

    ratio = len(found_words) / len(jd_words) if jd_words else 0.0
    score = round(ratio * 100, 1)

    return {
        "score": score,
        "found": len(found_words),
        "total": len(jd_words),
        "reason": f"{len(found_words)} of {len(jd_words)} important JD words present in resume."
    }


def score_experience_alignment(resume_text: str, jd_text: str) -> dict:
    """
    Score based on how well experience-level language aligns.
    Checks if resume mentions similar experience/seniority keywords as JD.
    """
    jd_lower = jd_text.lower()
    resume_lower = resume_text.lower()

    jd_exp_hits = [kw for kw in EXPERIENCE_KEYWORDS if kw in jd_lower]
    resume_exp_hits = [kw for kw in EXPERIENCE_KEYWORDS if kw in resume_lower]

    overlap = set(jd_exp_hits) & set(resume_exp_hits)
    ratio = len(overlap) / len(jd_exp_hits) if jd_exp_hits else 0.8  # Default if JD vague

    score = round(min(ratio, 1.0) * 100, 1)

    return {
        "score": score,
        "jd_exp_terms": jd_exp_hits,
        "resume_exp_terms": resume_exp_hits,
        "reason": (
            f"Experience alignment: {len(overlap)} of {len(jd_exp_hits)} experience-level terms matched."
            if jd_exp_hits else "No specific experience level detected in JD."
        )
    }


def generate_suggestions(matched: set, missing: set, resume_text: str, jd_text: str) -> list:
    """
    Generate actionable improvement suggestions based on gaps.
    """
    suggestions = []

    # 1. Missing skills suggestions
    if missing:
        top_missing = sorted(missing)[:5]
        suggestions.append({
            "section": "Skills",
            "problem": f"Key skills not found: {', '.join(top_missing)}",
            "suggestion": (
                f"Add these skills to your Skills section if you have experience with them: "
                f"{', '.join(top_missing)}. Even basic exposure counts — include personal projects."
            )
        })

    # 2. Check if resume has bullet points (achievement-focused)
    bullet_count = resume_text.count("•") + resume_text.count("-") + resume_text.count("*")
    if bullet_count < 5:
        suggestions.append({
            "section": "Experience",
            "problem": "Resume may lack structured bullet points.",
            "suggestion": (
                "Use bullet points for each job role. Format: "
                "'Action verb + Task + Result'. E.g., 'Reduced API latency by 35% by optimizing database queries.'"
            )
        })

    # 3. Quantifiable achievements
    numbers_in_resume = re.findall(r"\b\d+[%xX]?\b", resume_text)
    if len(numbers_in_resume) < 3:
        suggestions.append({
            "section": "Experience",
            "problem": "Few or no quantifiable achievements found.",
            "suggestion": (
                "Add measurable impact to your bullet points. "
                "Use numbers: 'Improved performance by 40%', 'Led a team of 5 engineers', 'Delivered project 2 weeks early'."
            )
        })

    # 4. Check for summary/objective section
    if "summary" not in resume_text.lower() and "objective" not in resume_text.lower() and "profile" not in resume_text.lower():
        suggestions.append({
            "section": "Summary",
            "problem": "No professional summary or profile section detected.",
            "suggestion": (
                "Add a 3-4 line professional summary at the top of your resume. "
                "Tailor it to the specific role using keywords from the job description."
            )
        })

    # 5. Length check (rough estimate by word count)
    word_count = len(resume_text.split())
    if word_count < 200:
        suggestions.append({
            "section": "Overall",
            "problem": "Resume appears too short.",
            "suggestion": "Expand your resume to at least 400-600 words. Add more detail to your experience and projects."
        })
    elif word_count > 1200:
        suggestions.append({
            "section": "Overall",
            "problem": "Resume may be too long.",
            "suggestion": "Trim your resume to 1-2 pages. Keep only the most relevant experience for this role."
        })

    return suggestions


def score_resume(
    resume_text: str,
    jd_text: str,
    resume_keywords: list,
    jd_keywords: list
) -> dict:
    """
    Main scoring function.

    Args:
        resume_text:     Full extracted resume text.
        jd_text:         Full cleaned JD text.
        resume_keywords: Keywords extracted from resume.
        jd_keywords:     Keywords extracted from JD.

    Returns:
        A dict with score, label, breakdown, matched/missing skills, suggestions.
    """
    resume_kws = normalize_keyword_list(resume_keywords)
    jd_kws = normalize_keyword_list(jd_keywords)

    # --- Section Scores ---
    skills_result = score_skills_section(resume_kws, jd_kws)
    keyword_result = score_keyword_coverage(resume_text, jd_text)
    experience_result = score_experience_alignment(resume_text, jd_text)

    # --- Weighted Overall Score ---
    overall = (
        skills_result["score"] * WEIGHTS["skills_match"] +
        keyword_result["score"] * WEIGHTS["keyword_coverage"] +
        experience_result["score"] * WEIGHTS["experience_keywords"]
    )
    overall = round(min(overall, 100), 1)

    # --- Matched and Missing ---
    matched, missing, _ = compute_overlap(resume_kws, jd_kws)

    # --- Suggestions ---
    suggestions = generate_suggestions(matched, missing, resume_text, jd_text)

    # --- Bonus skills (in resume but not in JD — added value) ---
    bonus = resume_kws - jd_kws

    return {
        "overall_score": overall,
        "score_label": get_score_label(overall),
        "section_scores": {
            "skills_match": skills_result,
            "keyword_coverage": keyword_result,
            "experience_alignment": experience_result
        },
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "bonus_skills": sorted(list(bonus))[:10],  # Top 10 only
        "suggestions": suggestions,
        "stats": {
            "resume_keyword_count": len(resume_kws),
            "jd_keyword_count": len(jd_kws),
            "matched_count": len(matched),
            "missing_count": len(missing)
        }
    }