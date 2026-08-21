JOB_ROLES = {
    "AI/ML Engineer": {
        "description": "Designs, builds, and deploys machine learning and deep learning models for intelligent applications.",
        "required_skills": ["Machine Learning", "Deep Learning", "Python"],
        "optional_skills": ["PyTorch", "TensorFlow", "Natural Language Processing", "Computer Vision", "MLOps", "Docker", "Algorithms", "Scikit-learn", "Git"]
    },
    "Data Scientist": {
        "description": "Analyzes complex datasets to extract actionable insights, build predictive models, and guide decision-making.",
        "required_skills": ["Data Analysis", "Python", "SQL"],
        "optional_skills": ["Machine Learning", "Statistics", "Data Visualization", "Pandas", "NumPy", "Scikit-learn", "R", "Exploratory Data Analysis", "Big Data"]
    },
    "Data Engineer": {
        "description": "Constructs, maintains, and optimizes data pipelines, architectures, and large-scale data processing systems.",
        "required_skills": ["Data Engineering", "SQL", "Python"],
        "optional_skills": ["ETL Pipelines", "Big Data", "Apache Spark", "PostgreSQL", "MongoDB", "Apache Kafka", "Apache Airflow", "Docker", "AWS"]
    },
    "NLP Specialist": {
        "description": "Develops natural language processing models, text analytics, language models, and conversational systems.",
        "required_skills": ["Natural Language Processing", "Python"],
        "optional_skills": ["Large Language Models", "Transformers", "BERT", "SpaCy", "NLTK", "Hugging Face", "Deep Learning", "PyTorch", "Text Classification"]
    },
    "Computer Vision Engineer": {
        "description": "Builds vision-based AI solutions for object detection, image classification, and video analytics.",
        "required_skills": ["Computer Vision", "Python"],
        "optional_skills": ["OpenCV", "Deep Learning", "CNN", "PyTorch", "TensorFlow", "YOLO", "Image Segmentation", "Object Detection"]
    },
    "Frontend Developer": {
        "description": "Crafts interactive, responsive, and aesthetically modern user interfaces for web and mobile apps.",
        "required_skills": ["JavaScript", "HTML", "CSS"],
        "optional_skills": ["React", "TypeScript", "Next.js", "Vue.js", "Angular", "Tailwind CSS", "Frontend Development", "Svelte"]
    },
    "Backend Developer": {
        "description": "Builds scalable server-side applications, REST APIs, database schemas, and microservice architectures.",
        "required_skills": ["Backend Development", "SQL"],
        "optional_skills": ["Python", "FastAPI", "Django", "Node.js", "Express.js", "PostgreSQL", "Docker", "REST API", "Microservices", "Java", "Go"]
    },
    "Full Stack Developer": {
        "description": "Develops both client-side and server-side components, handling end-to-end web product architecture.",
        "required_skills": ["Full Stack Development", "JavaScript", "SQL"],
        "optional_skills": ["React", "Python", "Node.js", "HTML", "CSS", "TypeScript", "REST API", "PostgreSQL", "MongoDB", "Docker"]
    },
    "DevOps / Cloud Engineer": {
        "description": "Manages cloud infrastructure, CI/CD pipelines, container orchestration, and system reliability.",
        "required_skills": ["DevOps", "Cloud Computing"],
        "optional_skills": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Linux", "Bash", "GitHub Actions", "NGINX"]
    },
    "Cybersecurity Analyst": {
        "description": "Protects organizational networks, systems, and application security through threat detection and audits.",
        "required_skills": ["Cybersecurity"],
        "optional_skills": ["Network Security", "Penetration Testing", "Cryptography", "Linux", "Python", "Bash"]
    }
}


def suggest_job_roles(extracted_entities: dict) -> list[dict]:
    """
    Given extracted skills/technologies/languages, calculate match percentages for predefined job roles.
    Returns sorted list of suggestions with match score, matched skills, and skill gaps.
    """
    user_skills = set(
        extracted_entities.get("skills", []) +
        extracted_entities.get("technologies", []) +
        extracted_entities.get("languages", [])
    )

    # Also include lowercase variants for forgiving matching
    user_skills_lower = {s.lower() for s in user_skills}

    suggestions = []

    for role_name, role_info in JOB_ROLES.items():
        req_skills = role_info["required_skills"]
        opt_skills = role_info["optional_skills"]
        all_role_skills = req_skills + opt_skills

        # Find matches
        matched_req = [s for s in req_skills if s in user_skills or s.lower() in user_skills_lower]
        matched_opt = [s for s in opt_skills if s in user_skills or s.lower() in user_skills_lower]
        matched_all = matched_req + matched_opt

        missing_req = [s for s in req_skills if s not in matched_req]
        missing_opt = [s for s in opt_skills if s not in matched_opt]

        # Scoring logic:
        # Required skills carry 60% weight, optional carry 40% weight
        req_score = (len(matched_req) / len(req_skills)) * 60.0 if req_skills else 60.0
        opt_score = (len(matched_opt) / len(opt_skills)) * 40.0 if opt_skills else 40.0
        match_score = round(req_score + opt_score, 1)

        # Candidate suitability tag
        if match_score >= 75:
            suitability = "Strong Fit"
        elif match_score >= 45:
            suitability = "Moderate Fit"
        elif match_score >= 20:
            suitability = "Potential Fit"
        else:
            suitability = "Low Match"

        suggestions.append({
            "role": role_name,
            "description": role_info["description"],
            "match_score": match_score,
            "suitability": suitability,
            "matched_skills": matched_all,
            "missing_required": missing_req,
            "missing_optional": missing_opt,
            "total_matched": len(matched_all),
            "total_role_skills": len(all_role_skills)
        })

    # Sort descending by match score
    suggestions.sort(key=lambda x: x["match_score"], reverse=True)
    return suggestions


def match_candidate_to_jd(candidate_entities: dict, jd_text: str, jd_extracted: dict = None) -> dict:
    """
    Match candidate's extracted profile against a specific Job Description (JD).
    If jd_extracted is not provided, extracts skills from jd_text automatically.
    """
    from backend.extractor import extract_information

    if not jd_extracted:
        jd_extracted = extract_information(jd_text)

    cand_skills = set(
        candidate_entities.get("skills", []) +
        candidate_entities.get("technologies", []) +
        candidate_entities.get("languages", [])
    )
    cand_skills_lower = {s.lower() for s in cand_skills}

    jd_skills = set(
        jd_extracted.get("skills", []) +
        jd_extracted.get("technologies", []) +
        jd_extracted.get("languages", [])
    )

    if not jd_skills:
        return {
            "match_score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "jd_skills": [],
            "suitability": "Insufficient JD entities"
        }

    matched = [s for s in jd_skills if s in cand_skills or s.lower() in cand_skills_lower]
    missing = [s for s in jd_skills if s not in matched]

    match_score = round((len(matched) / len(jd_skills)) * 100.0, 1)

    if match_score >= 80:
        suitability = "Excellent Match"
    elif match_score >= 60:
        suitability = "Good Match"
    elif match_score >= 35:
        suitability = "Partial Match"
    else:
        suitability = "Low Match"

    return {
        "match_score": match_score,
        "suitability": suitability,
        "matched_skills": matched,
        "missing_skills": missing,
        "jd_skills": list(jd_skills),
        "cand_skill_count": len(cand_skills),
        "jd_skill_count": len(jd_skills)
    }