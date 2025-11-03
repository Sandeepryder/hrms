from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import schemas
from services import job_service as JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/create-job",response_model=schemas.JobResponse) 
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    result = JobService.create_job(job, db)
    return result

@router.get("/get-jobs")
def get_all_jobs(db: Session = Depends(get_db)):
    """
    Anyone can list all jobs.
    """
    return JobService.list_jobs(db)
