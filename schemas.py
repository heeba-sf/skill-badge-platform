from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    student = "student"
    instructor = "instructor"


class MasteryLevel(str, Enum):
    not_demonstrated = "Not Demonstrated"
    level_1 = "Level 1"
    level_2 = "Level 2"
    level_3 = "Level 3"


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: UserRole

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SubmissionRequest(BaseModel):
    submission_text: str = Field(..., min_length=1)


class AssessmentResponse(BaseModel):
    id: str
    competency: str
    mastery_level: MasteryLevel
    confidence: float
    feedback: str
    created_at: datetime

    model_config = {"from_attributes": True}
