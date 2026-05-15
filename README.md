```markdown
# 📄 Resume Scorer — AI-Powered Resume Matching System

A web application that compares your resume against any job description and gives you an instant match score, identifies missing skills, and provides actionable suggestions to improve your resume.

🔗 **Live Demo:** https://resume-scorer-qbtc.onrender.com

---

## ✨ Features

- 📁 Upload resume in **PDF or DOCX** format
- 📋 Paste any **Job Description** text
- 📊 Get an **overall match score** out of 100
- ✅ See **matched skills** found in both resume and JD
- ❌ See **missing skills** you need to add
- 💡 Get **actionable suggestions** to improve your resume
- 🌟 View **bonus skills** you bring beyond the JD requirements
- 🔒 Privacy-safe — uploaded files deleted immediately after scoring

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Resume Parsing | pdfplumber, python-docx |
| Keyword Extraction | Skills Taxonomy (200+ skills across 12 categories) |
| Scoring Engine | Weighted formula (Skills 50% + Keywords 30% + Experience 20%) |
| Frontend | HTML5, CSS3, JavaScript |
| Deployment | Render |

---

## 📁 Project Structure

```
resume-scorer/
├── extractors/
│   └── keyword_extractor.py     # Keyword extraction from text
├── matcher/
│   ├── scorer.py                # Scoring engine
│   └── data/
│       ├── config.json          # Scoring weights and config
│       └── skills_taxonomy.json # 200+ skills database
├── parsers/
│   ├── resume_parser.py         # PDF and DOCX text extraction
│   └── jd_parser.py             # Job description cleaning
├── templates/
│   └── index.html               # Frontend UI
├── static/
│   └── styles.css               # Styling
├── app.py                       # Flask application
├── main.py                      # CLI entry point
├── render.yaml                  # Render deployment config
└── requirements.txt             # Python dependencies
```

---

## 🚀 How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/siri2975/resume-scorer.git
cd resume-scorer
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create required folders**
```bash
mkdir uploads
```

**5. Run the app**
```bash
python app.py
```

**6. Open in browser**
```
http://localhost:5000
```

---

## 📊 How Scoring Works

The overall score is calculated using a weighted formula:

| Component | Weight | Description |
|---|---|---|
| Skills Match | 50% | How many JD skills appear in your resume |
| Keyword Coverage | 30% | How many JD keywords are present in resume |
| Experience Alignment | 20% | Seniority level match between resume and JD |

**Score Labels:**

| Score | Label |
|---|---|
| 0 – 39 | 🔴 Poor |
| 40 – 59 | 🟡 Fair |
| 60 – 79 | 🔵 Good |
| 80 – 100 | 🟢 Excellent |

---

## 🖥️ How It Works

```
User uploads Resume (PDF/DOCX)
          ↓
Text extracted using pdfplumber / python-docx
          ↓
User pastes Job Description
          ↓
Keywords extracted from both using Skills Taxonomy
          ↓
Scoring engine computes weighted match score
          ↓
Results displayed — Score, Matched Skills,
Missing Skills, Suggestions, Bonus Skills
```

---

## ⚙️ Requirements

- Python 3.9+
- Flask
- pdfplumber
- python-docx
- gunicorn

Install all with:
```bash
pip install -r requirements.txt
```

---

## 👩‍💻 Developer

**Thadvai Siri Vardhini**
- GitHub: [@siri2975](https://github.com/siri2975)
- LinkedIn: [siri-vardhini-thadvai](https://linkedin.com/in/siri-vardhini-thadvai-519456318)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
```
