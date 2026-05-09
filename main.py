"""
main.py
-------
Command-line interface for the Resume Scorer.
Useful for testing without running the web server.

Usage:
  python main.py --resume path/to/resume.pdf --jd path/to/jd.txt
  python main.py --resume resume.docx --jd "We are looking for a Python developer..."
"""

import argparse
import json
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.resume_parser import parse_resume
from parsers.jd_parser import parse_jd
from extractors.keyword_extractor import extract_keywords
from matcher.scorer import score_resume


def print_divider(char="─", width=60):
    print(char * width)


def print_result(result: dict):
    """Pretty-print the scoring result in the terminal."""
    score = result["overall_score"]
    label = result["score_label"]

    # Score bar visualization
    filled = int(score / 5)
    bar = "█" * filled + "░" * (20 - filled)

    print_divider("═")
    print(f"  RESUME SCORE RESULT")
    print_divider("═")
    print(f"  Overall Score : {score}/100  [{label}]")
    print(f"  [{bar}] {score}%")
    print()

    # Section scores
    print("  SECTION BREAKDOWN:")
    print_divider()
    sections = result["section_scores"]
    for section_name, data in sections.items():
        label_str = section_name.replace("_", " ").title()
        s = data["score"]
        mini_bar = "█" * int(s / 10) + "░" * (10 - int(s / 10))
        print(f"  {label_str:<25} [{mini_bar}] {s}/100")
        print(f"    → {data['reason']}")
    print()

    # Matched skills
    matched = result["matched_skills"]
    print(f"  ✅ MATCHED SKILLS ({len(matched)}):")
    print_divider()
    if matched:
        print("  " + ",  ".join(matched[:20]))
        if len(matched) > 20:
            print(f"  ... and {len(matched) - 20} more")
    else:
        print("  None found.")
    print()

    # Missing skills
    missing = result["missing_skills"]
    print(f"  ❌ MISSING SKILLS ({len(missing)}) — Add these to boost your score:")
    print_divider()
    if missing:
        print("  " + ",  ".join(missing[:20]))
    else:
        print("  None! Great match.")
    print()

    # Suggestions
    suggestions = result["suggestions"]
    print(f"  💡 IMPROVEMENT SUGGESTIONS ({len(suggestions)}):")
    print_divider()
    for i, s in enumerate(suggestions, 1):
        print(f"  {i}. [{s['section']}] {s['problem']}")
        print(f"     → {s['suggestion']}")
        print()

    print_divider("═")
    stats = result["stats"]
    print(f"  Resume keywords: {stats['resume_keyword_count']}  |  "
          f"JD keywords: {stats['jd_keyword_count']}  |  "
          f"Matched: {stats['matched_count']}  |  "
          f"Missing: {stats['missing_count']}")
    print_divider("═")


def main():
    parser = argparse.ArgumentParser(
        description="Resume Scorer CLI — compare a resume against a job description."
    )
    parser.add_argument("--resume", required=True, help="Path to resume file (PDF or DOCX)")
    parser.add_argument(
        "--jd",
        required=True,
        help="Job description: path to a .txt file OR the raw JD text in quotes"
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text")

    args = parser.parse_args()

    # Load JD: either from file or inline string
    if os.path.isfile(args.jd):
        with open(args.jd, "r", encoding="utf-8") as f:
            jd_raw = f.read()
    else:
        jd_raw = args.jd

    print(f"\nParsing resume: {args.resume}")
    resume_text = parse_resume(args.resume)
    print(f"  Extracted {len(resume_text.split())} words from resume.")

    print("Parsing job description...")
    jd_parsed = parse_jd(jd_raw)
    cleaned_jd = jd_parsed["cleaned_text"]

    print("Extracting keywords...")
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(cleaned_jd)

    print(f"  Resume: {len(resume_keywords)} keywords  |  JD: {len(jd_keywords)} keywords")

    print("Scoring...\n")
    result = score_resume(
        resume_text=resume_text,
        jd_text=cleaned_jd,
        resume_keywords=resume_keywords,
        jd_keywords=jd_keywords
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_result(result)


if __name__ == "__main__":
    main()