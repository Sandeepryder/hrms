from fastapi import HTTPException
from sqlalchemy.orm import Session
import json
from model import models

def score_candidate(candidate_id: int, db: Session):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    parsed = candidate.parsedResume
    job = candidate.job

    if not parsed or not job:
        raise HTTPException(status_code=400, detail="Missing parsed resume or job data")

    job_keywords = job.scoringKeywords or []
    resume_keywords = parsed.keywords or []

    # Compare and calculate score
    matched = [kw for kw in resume_keywords if kw.lower() in [jk.lower() for jk in job_keywords]]
    score = round(len(matched) / len(job_keywords) * 100, 2) if job_keywords else 0

    # Update candidate record
    candidate.score = score
    candidate.scoreBreakdown = {
        "matchedKeywords": matched,
        "totalKeywords": len(job_keywords),
        "matchedCount": len(matched)
    }
    candidate.status = "screened"

    db.commit()
    db.refresh(candidate)
    return {
        "candidateId": candidate_id,
        "score": score,
        "matchedKeywords": matched
    }
