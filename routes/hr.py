from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from model import models
import schemas
from database import get_db
from services import job_service as JobService
from services.auth_services import require_candidate, require_hr


router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/create-job", response_model=schemas.JobResponse)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db),current_user: models.User = Depends(require_hr)):
    return JobService.create_job(job,db)

@router.get("/get-jobs", response_model=list[schemas.JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    return JobService.list_jobs(db)


@router.post("/schedule", response_model=schemas.InterviewResponse)
def schedule_interview(data: schemas.InterviewCreate, db: Session = Depends(get_db),current_user: models.User = Depends(require_hr)):
    return JobService.schedule_interview(data, db)

@router.patch("/interview/{interview_id}/status")
def update_interview_status(interview_id: int, status: str, db: Session = Depends(get_db),current_user: models.User = Depends(require_hr)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview.status = status
    db.commit()
    db.refresh(interview)

    # Update candidate status also if needed
    if status == "completed":
        candidate = db.query(models.Candidate).filter(models.Candidate.id == interview.candidateId).first()
        candidate.status = "interview_completed"
        db.commit()

    return {"message": "Interview status updated", "data": interview}


@router.post("/give", response_model=schemas.FeedbackResponse)
def give_feedback(data: schemas.FeedbackCreate, db: Session = Depends(get_db),current_user: models.User = Depends(require_hr)):
    return JobService.add_feedback(data, db)