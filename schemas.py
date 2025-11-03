# schemas.py
from enum import Enum
from pydantic import BaseModel 
from typing import List, Optional,Dict
from datetime import datetime


# class RoleEnum(str, Enum):
#     HR = "HR"
#     CANDIDATE = "CANDIDATE"

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    title: str
    description: str
    scoringKeywords: Optional[List[str]] = []

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    scoringKeywords: Optional[List[str]] = []
    createdAt: datetime

    class Config:
        # pydantic v2 replacement for orm_mode=True
        from_attributes = True


class CandidateCreate(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None
    jobId: int

class CandidateResponse(BaseModel):
    id: int
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None
    jobId: int
    score: Optional[float] = None
    scoreBreakdown: Optional[Dict] = None
    status: str
    createdAt: datetime

    class Config:
        # Pydantic v2: allow reading from SQLAlchemy objects
        from_attributes = True

class CandidateUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    score: Optional[float] = None
    scoreBreakdown: Optional[Dict] = None
    email: Optional[str] = None

class FileMeta(BaseModel):
    filename: str
    path: str
    mimetype: str
    size: int

class ResumeFileResponse(BaseModel):
    id: int
    candidateId: int
    filename: str
    path: str
    mimetype: str
    size: int
    uploadedAt: datetime

    class Config:
        from_attributes = True

class ParsedResumeBody(BaseModel):
    text: str
    keywords: Optional[List[str]] = []

class ScoreBody(BaseModel):
    score: float
    breakdown: Dict



class InterviewCreate(BaseModel):
    candidateId: int
    scheduledAt: datetime
    interviewer: str


class InterviewResponse(BaseModel):
    id: int
    candidateId: int
    scheduledAt: datetime
    interviewer: str
    status: str
    createdAt: datetime

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    candidateId: int
    interviewer: str
    rating: float
    notes: str | None = None


class FeedbackResponse(BaseModel):
    id: int
    candidateId: int
    rating: float
    notes: str | None = None
    createdAt: datetime

    class Config:
        from_attributes = True