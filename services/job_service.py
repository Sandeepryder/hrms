from fastapi import HTTPException
from sqlalchemy.orm import Session
from model import models

from utils.orm_utils import sqlalchemy_obj_to_dict

def create_job(job_data : models.Job, db: Session):
    try:
        new_job = models.Job(
            title=job_data.title,
            description=job_data.description,
            scoringKeywords=job_data.scoringKeywords
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job
        # job_dict = sqlalchemy_obj_to_dict(new_job)
        # print("job dict", job_dict)
        # return {"success": True, "message": "Job created successfully", "data": job_dict}

    except Exception as e:
        db.rollback()
        return {"success": False, "message": "Failed to create job", "error": str(e)}


def list_jobs(db: Session):
    """
    Show all jobs for HR or candidates.
    """
    return db.query(models.Job).order_by(models.Job.createdAt.desc()).all()


def schedule_interview(data :models.Interview, db: Session):
        candidate = db.query(models.Candidate).filter(models.Candidate.id == data.candidateId).first()
        print("candiadate", candidate)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        interview = models.Interview(
            candidateId=data.candidateId,
            scheduledAt=data.scheduledAt,
            interviewer=data.interviewer,
        )

        db.add(interview)
        candidate.status = "interview_scheduled"
        db.commit()
        db.refresh(interview)
        return interview
        # return {"message": "Interview scheduled successfully", "data": interview}



def add_feedback(data: models.Feedback, db: Session):
        interview = db.query(models.Interview).filter(models.Interview.id == data.candidateId).first()
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")

        feedback = models.Feedback(
            candidateId=data.candidateId,
            interviewer=data.interviewer,
            rating=data.rating,
            notes=data.notes
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        return feedback