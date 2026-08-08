import os
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from database import Base, engine, get_db
from grader import grade_submission
from models import Assessment, User, UserRole as ModelUserRole
from schemas import (
    AssessmentResponse,
    SubmissionRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management API", version="1.0.0")

os.makedirs(os.path.join("static", "badges"), exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=ModelUserRole(payload.role.value),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user_id=user.id, role=user.role.value)
    return TokenResponse(access_token=token)


@app.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/submit", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def submit(
    payload: SubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = grade_submission(payload.submission_text)

    assessment = Assessment(
        user_id=current_user.id,
        submission_text=payload.submission_text,
        competency=result["competency"],
        mastery_level=result["mastery_level"],
        confidence=result["confidence"],
        feedback=result["feedback"],
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment
