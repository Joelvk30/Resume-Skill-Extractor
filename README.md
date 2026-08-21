# Resume-Skill-Extractor
# AI Recruiter — NLP + Chatbot Track (MIC AIML Department Recruitment)

# Project Overview
AI Recruiter is a rule-based NLP assistant that analyzes free-form, conversational text — rather than structured resumes — and extracts the *skills*, *technologies*, and *programming languages* a person mentions. It then uses that extracted profile to 
(1) suggest and rank the best-fitting job roles from a predefined set, and 
(2) match a candidate directly against a specific job description, all without using an LLM API.

This project implements:
Part 1 – Extraction:* Converts conversational input into structured output listing detected skills, technologies, and languages.
Part 2 – Matching:* Suggests suitable job roles from a curated list of 10 predefined roles, ranked by a weighted match score against each role's required and optional skills, and separately matches a candidate's profile against a specific job description by extracting the JD's skills and computing overlap.

# Problem Statement
Recruiters and candidates rarely describe experience in neat, structured categories — people talk casually, use abbreviations (e.g., "ML" instead of "Machine Learning"), and mix multi-word phrases with single terms. This project addresses the challenge of reliably extracting structured, standardized information from that kind of unstructured, conversational text, without relying on an LLM API.

# Installation Instructions
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <your-repo-folder>

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download required NLTK data (only needed once — the script also does this automatically)
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet')"

# 5. Run the chatbot
python main.py   # replace with your actual entry-point filename
```

> Fill in the exact entry-point filename and confirm the install steps match your actual project structure before submitting.

# Dataset Used
No external dataset is required for this track. The system processes free-form conversational text provided directly by the user at runtime. Job role definitions used for Part 2 matching (`JOB_ROLES`) are hand-curated in-code — 10 roles (AI/ML Engineer, Data Scientist, Data Engineer, NLP Specialist, Computer Vision Engineer, Frontend Developer, Backend Developer, Full Stack Developer, DevOps/Cloud Engineer, Cybersecurity Analyst), each with a description, required skills, and optional skills. 
# Methodology
1. *Text normalization* — input text is lowercased, whitespace is collapsed, and non-essential punctuation is stripped while preserving characters meaningful to technical terms (`+`, `#`, `.`, `-`), so terms like "C++" and "C#" remain intact.
2. *Tokenization* — normalized text is split into individual word tokens.
3. *N-gram generation* — consecutive tokens are combined into overlapping phrases (1-word, 2-word, 3-word, etc.) so multi-word skills like "machine learning" or "natural language processing" can be matched, not just single words.
4. *Alias resolution* — abbreviations and nicknames (e.g., "ml", "js", "k8s") are expanded to their full canonical term using an alias dictionary before lookup.
5. *Dictionary lookup* — resolved phrases are checked against curated `SKILLS`, `TECHNOLOGIES`, and `PROGRAMMING_LANGUAGES` dictionaries to produce clean, human-readable labels (e.g., "ml" → "machine learning" → "Machine Learning").
6. *Deeper preprocessing (NLTK) — for additional analysis, text is also processed with NLTK: tokenized, stripped of stopwords, and lemmatized to base word forms.
7. *Chatbot routing*— the chatbot first checks for simple conversational intents (greetings, farewells, "what's your name," etc.) via keyword matching, then falls back to the extraction pipeline above to detect and report skills/technologies/languages, with a graceful fallback response if nothing is found.
8. **Job role suggestion (Part 2)** — the candidate's extracted skills, technologies, and languages are merged into a single set (with a lowercase variant for forgiving, case-insensitive matching) and compared against each of the 10 predefined job roles in `JOB_ROLES`. For each role, a **match score** is computed as a weighted sum: the fraction of *required* skills matched contributes up to 60 points, and the fraction of *optional* skills matched contributes up to 40 points. Each role is then labeled by suitability tier — **Strong Fit** (≥75), **Moderate Fit** (≥45), **Potential Fit** (≥20), or **Low Match** (below 20) — and all roles are returned sorted by score, descending, along with the specific matched skills and missing required/optional skills for each.
9. *Job-description matching (Part 2)* — a candidate's extracted profile can also be matched directly against a specific job description. If the JD hasn't already been processed, its text is passed through the same Part 1 extraction pipeline (`extract_information`) to get its own skill set. The match score is the percentage of the JD's extracted skills that the candidate also has, and the result is labeled *Excellent Match* (≥80%), *Good Match* (≥60%), **Partial Match** (≥35%), or **Low Match** (below 35%), along with the specific matched and missing skills.

## Technologies Used
- **Python**
- **NLTK** (tokenization, stopword removal, lemmatization)
- **`re` (Regular Expressions)** — text cleaning and normalization
- **`string`** — punctuation handling
- Pure Python (dictionaries, sets, list comprehensions) for the job-role scoring and JD-matching logic in Part 2 — no external ML/embedding libraries were needed for this rule-based approach

## Results
[Fill in: e.g., "The extraction pipeline correctly identifies skills/technologies/languages across N test sentences, including abbreviated and multi-word phrasing. The matching feature correctly suggests relevant job roles for M sample profiles." Include a couple of concrete before/after examples if possible.]

## Challenges Faced
[Fill in — e.g., handling overlapping n-grams so the same phrase isn't double-counted, deciding how to prioritize longer multi-word matches over shorter single-word ones, resolving ambiguous aliases, tuning what counts as a "match" for Part 2, etc.]

## Future Improvements
- Expand the skills/technologies/aliases dictionaries with more terms and domains.
- Improve n-gram matching to prioritize the longest matching phrase and avoid partial-overlap double counts.
- Add confidence scoring for detected skills.
- [Add ideas specific to your Part 2 matching approach, e.g., moving from rule-based matching to a lightweight similarity model.]


## Screenshots

<img width="798" height="220" alt="image" src="https://github.com/user-attachments/assets/09c07723-f6b0-43fc-9383-73bc79d96132" />
---

