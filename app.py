"""
app.py
------
Flask web application for the Resume Scorer.

Routes:
  GET  /           → Serve the main UI (index.html)
  POST /score      → Accept resume file + JD text, return JSON score result
  GET  /health     → Health check
"""

import os
import json
import sys
import uuid
import logging

from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.resume_parser import parse_resume
from parsers.jd_parser import parse_jd
from extractors.keyword_extractor import extract_keywords
from matcher.scorer import score_resume

# ── Configuration ──────────────────────────────────────────────────────────────

CONFIG_PATH = os.path.join("matcher", "data", "config.json")
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

UPLOAD_FOLDER = CONFIG["flask"]["upload_folder"]
ALLOWED_EXTENSIONS = set(CONFIG["upload"]["allowed_extensions"])
MAX_FILE_MB = CONFIG["upload"]["max_file_size_mb"]

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Flask App ──────────────────────────────────────────────────────────────────

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_MB * 1024 * 1024  # Convert MB → bytes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_file(filepath: str):
    """Delete uploaded file after processing to save disk space."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        logger.warning(f"Could not delete temp file {filepath}: {e}")


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main UI."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "message": "Resume Scorer is running."})


@app.route("/score", methods=["POST"])
def score():
    """
    Main scoring endpoint.

    Expects multipart/form-data with:
      - file: resume PDF or DOCX
      - jd:   job description plain text

    Returns JSON with score, matched/missing skills, suggestions.
    """
    # ── 1. Validate inputs ────────────────────────────────────────────────────

    if "file" not in request.files:
        return jsonify({"error": "No resume file uploaded. Please attach a PDF or DOCX."}), 400

    file = request.files["file"]
    jd_text = request.form.get("jd", "").strip()

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    if not jd_text:
        return jsonify({"error": "Job description text is required."}), 400

    if len(jd_text) < 50:
        return jsonify({"error": "Job description is too short. Please paste the full JD."}), 400

    # ── 2. Save uploaded file temporarily ─────────────────────────────────────

    # Use UUID prefix to avoid filename collisions
    safe_name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    file.save(filepath)
    logger.info(f"Saved upload: {filepath}")

    try:
        # ── 3. Parse resume ───────────────────────────────────────────────────
        logger.info("Parsing resume...")
        resume_text = parse_resume(filepath)

        if len(resume_text.strip()) < 100:
            return jsonify({"error": "Could not extract enough text from the resume. Try a different file."}), 422

        # ── 4. Parse JD ───────────────────────────────────────────────────────
        logger.info("Parsing JD...")
        jd_parsed = parse_jd(jd_text)
        cleaned_jd = jd_parsed["cleaned_text"]

        # ── 5. Extract keywords ───────────────────────────────────────────────
        logger.info("Extracting keywords...")
        resume_keywords = extract_keywords(resume_text)
        jd_keywords = extract_keywords(cleaned_jd)

        logger.info(f"Resume keywords: {len(resume_keywords)} | JD keywords: {len(jd_keywords)}")

        # ── 6. Score ──────────────────────────────────────────────────────────
        logger.info("Scoring...")
        result = score_resume(
            resume_text=resume_text,
            jd_text=cleaned_jd,
            resume_keywords=resume_keywords,
            jd_keywords=jd_keywords
        )

        result["filename"] = file.filename  # Echo back filename for UI
        logger.info(f"Score: {result['overall_score']} ({result['score_label']})")

        return jsonify(result), 200

    except FileNotFoundError as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 404

    except ValueError as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 422

    except Exception as e:
        logger.exception("Unexpected error during scoring")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    finally:
        # Always clean up the uploaded file
        cleanup_file(filepath)


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = CONFIG["flask"]["port"]
    debug = CONFIG["flask"]["debug"]
    print(f"\n🚀 Resume Scorer running at http://localhost:{port}\n")
    app.run(debug=debug, port=port)