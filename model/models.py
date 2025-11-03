from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, func,Enum
)
from sqlalchemy.orm import relationship
from database import Base
import enum


class RoleEnum(str, enum.Enum):
    HR = "HR"
    CANDIDATE = "CANDIDATE"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.CANDIDATE)


# ================= JOB MODEL ===================
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=func.now())
    scoringKeywords = Column(JSON, nullable=True)
    candidates = relationship("Candidate", back_populates="job")


# ================= CANDIDATE MODEL ===================
class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    jobId = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    job = relationship("Job", back_populates="candidates")
    resume = relationship("ResumeFile", back_populates="candidate",uselist=False)
    parsedResume = relationship("ResumeParsed", back_populates="candidate", uselist=False)
    interviews = relationship("Interview", back_populates="candidate")
    feedbacks = relationship("Feedback", back_populates="candidate")
    score = Column(Float, nullable=True)
    scoreBreakdown = Column(JSON, nullable=True)
    status = Column(String, default="applied")  # applied, screened, interviewed, offered, rejected, hired
    createdAt = Column(DateTime(timezone=True), server_default=func.now())


# ================= RESUME FILE MODEL ===================
class ResumeFile(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidateId = Column(Integer, ForeignKey("candidates.id"))
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    mimetype = Column(String)
    size = Column(Integer)
    uploadedAt = Column(DateTime, default=func.now())
    candidate = relationship("Candidate", back_populates="resume")


# ================= RESUME PARSED MODEL ===================
class ResumeParsed(Base):
    __tablename__ = "resume_parsed"

    id = Column(Integer, primary_key=True, index=True)
    candidateId = Column(Integer, ForeignKey("candidates.id"))
    text = Column(Text, nullable=False)
    keywords = Column(JSON, nullable=True)
    candidate = relationship("Candidate", back_populates="parsedResume")


# ================= INTERVIEW MODEL ===================
class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidateId = Column(Integer, ForeignKey("candidates.id"))
    scheduledAt = Column(DateTime, nullable=False)
    interviewer = Column(String, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, completed, canceled
    createdAt = Column(DateTime, default=func.now())
    candidate = relationship("Candidate", back_populates="interviews")


# ================= FEEDBACK MODEL ===================
class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    candidateId = Column(Integer, ForeignKey("candidates.id"))
    interviewer = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    createdAt = Column(DateTime, default=func.now())
    candidate = relationship("Candidate", back_populates="feedbacks")


# ================= SCORING CONFIG MODEL ===================
class ScoringConfig(Base):
    __tablename__ = "scoring_config"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    config = Column(JSON, nullable=True)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
