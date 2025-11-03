import os
import shutil
from fastapi import FastAPI , APIRouter, Form, UploadFile

from utils.scoring import score_resume
from utils.text_extraction import extract_text

router = APIRouter(prefix="/api/recruitment/resumes", tags=["Resumes"])

UPLOAD_DIR = "uploads/resumes"

@router.post("/upload")
async def upload_resume(candidateId : int = Form(...), file: UploadFile = None):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(file_path)

    score, breakdown = score_resume(text, candidateId)

    return {
        "success": True,
        "data": {
            "candidateId": candidateId,
            "parsedText": text[:500],
            "score": score,
            "breakdown": breakdown
        }
    }
