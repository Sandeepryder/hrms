# services/candidate_service.py
import json
import re
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from master import extract_text
from model import models
from typing import Optional, Dict, Any
from utils.orm_utils import sqlalchemy_obj_to_dict  # see utils below
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def apply_for_job(candidate_data: models.Candidate, db: Session):
    
    try:
        job_id = candidate_data.jobId   
        if not job_id:
            raise HTTPException(status_code=400, detail="jobId is required")

        # check job exists
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # prevent duplicate application by same email for same job
        existing = db.query(models.Candidate).filter(
            models.Candidate.email == candidate_data.email,
            models.Candidate.jobId == job_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Already applied for this job")

        new_candidate = models.Candidate(
            firstName=candidate_data.firstName,
            lastName=candidate_data.lastName,
            email=candidate_data.email,
            phone=candidate_data.phone,
            jobId=job_id,
            status="applied"
        )
        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)
        return new_candidate

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to apply for job: {e}")


def list_candidates(db: Session, job_id: Optional[int] = None):
   
    try:
        q = db.query(models.Candidate).order_by(models.Candidate.createdAt.desc())
        if job_id:
            q = q.filter(models.Candidate.jobId == job_id)
        return q.all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_candidate(candidate_id: int, db: Session):
   
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


def update_candidate(candidate_id: int, update_data: dict, db: Session):
   
    try:
        cand = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
        if not cand:
            raise HTTPException(status_code=404, detail="Candidate not found")

        allowed = {"firstName", "lastName", "phone", "status", "score", "scoreBreakdown", "email"}
        for k, v in update_data.items():
            if k in allowed:
                setattr(cand, k, v)
        db.commit()
        db.refresh(cand)
        return cand
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def parse_resume(candidate_id: int, db: Session):
    # Candidate aur resume fetch karo
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate or not candidate.resume:
        raise HTTPException(status_code=404, detail="Candidate or resume not found")

    # file_path = candidate.resume.path
    file_path = candidate.resume.path

    parsed_text = extract_text(file_path)
   

    if parsed_text.strip() == "" or parsed_text == "Unsupported file format.":
        raise HTTPException(status_code=400, detail="Unable to extract text from resume")

    keywords = extract_keywords(parsed_text)
   
    parsed = models.ResumeParsed(
        candidateId=candidate_id,
        text=parsed_text,
        keywords=keywords
    )

    db.add(parsed)
    db.commit()
    db.refresh(parsed)
    return {"message": "Resume parsed successfully", "keywords": keywords}


def extract_keywords(text: str):
    # simple tech keyword list (you can expand later)
    tech_keywords = [
    # --- General Purpose Languages ---
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go", "rust", "kotlin", "swift",
    "ruby", "perl", "php", "r", "dart", "scala", "lua", "objective-c", "haskell", "elixir",
    "erlang", "fortran", "matlab", "groovy", "bash", "shell", "powershell",

    # --- Web Development / Frontend ---
    "html", "css", "sass", "less", "react", "angular", "vue", "nextjs", "nuxtjs", "svelte",
    "jquery", "bootstrap", "tailwind", "astro",

    # --- Backend Frameworks ---
    "django", "flask", "fastapi", "express", "spring", "spring boot", "laravel", "rails",
    "node", "nestjs", "adonisjs", "gin", "fiber", "asp.net", "dotnet",

    # --- Database & Query Languages ---
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis", "oracle", "mariadb",
    "cassandra", "elasticsearch", "neo4j", "dynamodb", "firebase",

    # --- DevOps / Cloud / Tools ---
    "docker", "kubernetes", "jenkins", "terraform", "ansible", "aws", "azure", "gcp",
    "cloudformation", "git", "github", "gitlab", "bitbucket", "circleci", "travisci",
    "helm", "nginx", "apache", "linux", "bash scripting",

    # --- AI / Data Science / ML ---
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "opencv",
    "matplotlib", "seaborn", "xgboost", "lightgbm", "transformers", "huggingface",
    "machine learning", "deep learning", "nlp", "data analysis", "data science",
    "artificial intelligence",

    # --- Mobile Development ---
    "react native", "flutter", "swiftui", "android", "ios", "xcode", "jetpack compose",

    # --- Blockchain / Web3 ---
    "solidity", "web3", "hardhat", "truffle", "ethers.js", "web3.js", "rust", "move", "cadence",

    # --- Testing & Automation ---
    "pytest", "unittest", "selenium", "cypress", "playwright", "jest", "mocha", "chai",
    "junit", "postman",

    # --- Other Popular Technologies ---
    "graphql", "rest api", "grpc", "microservices", "serverless", "mqtt",
    "kafka", "rabbitmq", "redis", "openapi", "swagger",

    # --- Data / BI Tools ---
    "power bi", "tableau", "excel", "looker", "snowflake", "databricks", "bigquery",

    # --- Others ---
    "vim", "emacs", "vscode",    "intellij", "jira", "confluence", "notion"
    ]

    found = [kw for kw in tech_keywords if kw.lower() in text.lower()]
    return found



def calculate_resume_score(candidate_id: int, db: Session):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    parsed = db.query(models.ResumeParsed).filter(models.ResumeParsed.candidateId == candidate_id).first()
    if not parsed or not parsed.text:
        raise HTTPException(status_code=404, detail="Parsed resume not found")

    job = db.query(models.Job).filter(models.Job.id == candidate.jobId).first()
    if not job or not job.description:
        raise HTTPException(status_code=404, detail="Job description not found")

    # ⚙️ Load scoring configuration (or defaults)
    config = db.query(models.ScoringConfig).order_by(models.ScoringConfig.updatedAt.desc()).first()
    if config and config.config:
        config_data = json.loads(config.config)
        weights = config_data.get("weights", {
            "keywords": 0.45,
            "tfidf": 0.35,
            "experience": 0.15,
            "education": 0.05
        })
    else:
        weights = {
            "keywords": 0.45,
            "tfidf": 0.35,
            "experience": 0.15,
            "education": 0.05
        }

    # ========== 1️⃣ Keyword Matching ==========
    job_keywords = [kw.lower() for kw in (job.scoringKeywords or [])]
    resume_keywords = [kw.lower() for kw in (parsed.keywords or [])]

    matched = list(set(job_keywords) & set(resume_keywords))
    keyword_score = min(1, len(matched) / len(job_keywords)) if job_keywords else 0

    # ========== 2️⃣ TF-IDF Similarity ==========
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf = vectorizer.fit_transform([parsed.text, job.description])
        # print("tdidf",tfidf)
        tfidf_similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        # print("similarity",tfidf_similarity)
    except Exception:
        tfidf_similarity = 0

    # ========== 3️⃣ Experience Extraction ==========
    def extract_experience_years(text):
        match = re.search(r"(\d+)\s*(?:years|yrs|year)", text.lower())
        if match:
            return int(match.group(1))
        return 0

    experience_years = extract_experience_years(parsed.text)
    required_years = getattr(job, "requiredExperience", 3)
    experience_score = max(0, min(1, (experience_years - required_years) / 5))

    # ========== 4️⃣ Final Weighted Score ==========
    final_score = (
        weights["keywords"] * keyword_score +
        weights["tfidf"] * tfidf_similarity +
        weights["experience"] * experience_score
    )

    final_score_percent = round(final_score * 100, 2)

    # ========== 5️⃣ Save + Breakdown ==========
    breakdown = {
        "keyword_score": round(keyword_score, 2),
        "tfidf_similarity": round(tfidf_similarity, 2),
        "experience_score": round(experience_score, 2),
        "weights": weights,
        "matched_keywords": matched,
        "experience_years": experience_years,
        "final_score": final_score_percent
    }

    explanation = (
        f"Matched keywords: {matched}. "
        f"TF-IDF similarity={tfidf_similarity:.2f}. "
        f"Experience ≈ {experience_years} yrs → score +{experience_score:.2f}"
    )

    candidate.score = float(final_score_percent)
    candidate.scoreBreakdown = breakdown
    db.commit()
    db.refresh(candidate)

    return {
        "message": "Resume scored successfully",
        "candidate_id": candidate_id,
        "score": final_score_percent,
        "breakdown": breakdown,
        "explanation": explanation
    }

# def calculate_resume_score(candidate_id: int, db: Session):
  
#     candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
#     if not candidate:
#         raise HTTPException(status_code=404, detail="Candidate not found")

 
#     parsed = db.query(models.ResumeParsed).filter(models.ResumeParsed.candidateId == candidate_id).first()
#     if not parsed or not parsed.keywords:
#         raise HTTPException(status_code=404, detail="Parsed resume keywords not found")

 
#     job = db.query(models.Job).filter(models.Job.id == candidate.jobId).first()
#     if not job or not job.scoringKeywords:
#         raise HTTPException(status_code=404, detail="Job keywords not found")

#     # 4️⃣ Matching logic
#     job_keywords = [kw.lower() for kw in job.scoringKeywords]
#     resume_keywords = [kw.lower() for kw in parsed.keywords]

#     matched = list(set(job_keywords) & set(resume_keywords))
#     score = round((len(matched) / len(job_keywords)) * 100, 2)

#     # 5️⃣ Candidate table update karo
#     candidate.score = score
#     candidate.scoreBreakdown = {
#         "job_keywords": job_keywords,
#         "resume_keywords": resume_keywords,
#         "matched": matched,
#         "match_count": len(matched),
#         "total_keywords": len(job_keywords),
#         "final_score": score
#     }

#     db.commit()
#     db.refresh(candidate)

#     return {
#         "message": "Resume scored successfully",
#         "candidate_id": candidate_id,
#         "score": score,
#         "matched_keywords": matched
#     }

