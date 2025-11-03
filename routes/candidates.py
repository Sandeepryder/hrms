# routes/candidates.py
import base64
from datetime import datetime
import os
import re
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from database import get_db
from model import models
from services import candidate_service as CandidateService
from sqlalchemy.orm import Session
import schemas
from services.auth_services import require_candidate, require_hr
router = APIRouter(prefix="/candidates", tags=["Candidates"])


UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/apply", response_model=schemas.CandidateResponse)
def apply_for_job(candidate: schemas.CandidateCreate, db: Session = Depends(get_db),current_user: models.User = Depends(require_candidate)):
    return CandidateService.apply_for_job(candidate, db)


@router.get("/list",response_model=list[schemas.CandidateResponse])
def list_candidates(jobId: int | None = None, db: Session = Depends(get_db)):
    
    return CandidateService.list_candidates(db, job_id=jobId)


@router.get("/{candidate_id}",response_model=schemas.CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db),current_user: models.User = Depends(require_hr)):
    return CandidateService.get_candidate(candidate_id, db)


@router.patch("/{candidate_id}", response_model=schemas.CandidateResponse)
def update_candidate(candidate_id: int, update_data: dict, db: Session = Depends(get_db)):
  
    return CandidateService.update_candidate(candidate_id, update_data, db)


@router.post("/{candidate_id}/upload-resume")
def upload_resume(candidate_id: int, payload: dict, db: Session = Depends(get_db),current_user: models.User = Depends(require_candidate)):
    try:
        image_data = payload.get("image_url")
        if not image_data:
            raise HTTPException(status_code=400, detail="Missing image_url field")

        # detect file type
        if "application/pdf" in image_data:
            ext = "pdf"
        elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in image_data:
            ext = "docx"
        elif "application/msword" in image_data:
            ext = "doc"
        elif "image/png" in image_data:
            ext = "png"
        elif "image/jpeg" in image_data:
            ext = "jpg"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # decode base64 data
        file_data = re.sub('^data:.*;base64,', '', image_data)
        binary = base64.b64decode(file_data)

        # save file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{candidate_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as f:
            f.write(binary)

        # store metadata
        db_file = models.ResumeFile(
            candidateId=candidate_id,
            filename=filename,
            path=file_path,
            mimetype=f"application/{ext}",
            size=len(binary),
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        parsed_data = CandidateService.parse_resume(candidate_id, db)

        score_data = CandidateService.calculate_resume_score(candidate_id, db)

        return {
            "success": True,
            "message": "Resume uploaded successfully",
            "data": {
                "candidate_id": candidate_id,
                # "filename": File.filename,
                # "mimetype": File.content_type,
                "path": file_path,
                "keywords":parsed_data.get("keywords"),
                "score": score_data.get("score")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

# @router.post("/{candidate_id}/upload-resume")
# def upload_resume(candidate_id: int, file: UploadFile = File(...), db: Session = Depends(get_db),current_user: models.User = Depends(require_candidate)):
#     try:
#         # Check file type
#         allowed_ext = ["pdf", "doc", "docx", "png", "jpg", "jpeg"]
#         ext = file.filename.split(".")[-1].lower()
#         if ext not in allowed_ext:
#             raise HTTPException(status_code=400, detail="Invalid file format. Only PDF, DOC, DOCX, PNG, JPG allowed.")

#         # Save file locally
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
#         file_path = os.path.join(UPLOAD_DIR, f"{candidate_id}_{timestamp}_{file.filename}")
#         with open(file_path, "wb") as f:
#             f.write(file.file.read())

#         # Save file metadata in DB
#         file_meta = models.ResumeFile(
#             candidateId=candidate_id,
#             filename=file.filename,
#             path=file_path,
#             mimetype=file.content_type,
#             size=os.path.getsize(file_path),
#         )

#         db.add(file_meta)
#         db.commit()
#         db.refresh(file_meta)

#         parsed_data = CandidateService.parse_resume(candidate_id, db)

#         score_data = CandidateService.calculate_resume_score(candidate_id, db)

#         return {
#             "success": True,
#             "message": "Resume uploaded successfully",
#             "data": {
#                 "candidate_id": candidate_id,
#                 "filename": file.filename,
#                 "mimetype": file.content_type,
#                 "path": file_path,
#                 "keywords":parsed_data.get("keywords"),
#                 "score": score_data.get("score")
#             }
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))

