import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
import re

import models
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from blockchain_service import anchor_badge_on_chain, verify_badge_on_chain
from auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
    require_role,
)
from badge_service import issue_badge_if_eligible
from database import Base, engine, get_db
from grader import grade_submission
from models import Assessment, Badge, User, UserRole as ModelUserRole, InstructorDomain, SuggestedActivity
from schemas import (
    AssessmentResponse,
    BadgeResponse,
    OpenBadgeAssertion20,
    SubmissionRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    SuggestedActivityRequest,
    SuggestedActivityResponse,
    StudentReportResponse,
    UserReportResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(os.path.join("static", "badges"), exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


def build_badge_assertion(badge: models.Badge, user: models.User, request: Request) -> dict:
    base_url = str(request.base_url).rstrip('/').replace("localhost", "127.0.0.1")

    # Standardize date string to YYYY-MM-DDTHH:MM:SSZ (stripping microseconds)
    if isinstance(badge.issue_date, datetime):
        date_str = badge.issue_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        raw_str = str(badge.issue_date).replace(" ", "T").split(".")[0]
        date_str = f"{raw_str}Z" if not raw_str.endswith("Z") else raw_str

    return {
        "@context": "https://w3id.org/openbadges/v2",
        "type": "Assertion",
        "id": f"{base_url}/badges/{badge.id}",
        "recipient": {
            "type": "email",
            "hashed": False,
            "identity": user.email
        },
        "issuedOn": date_str,
        "badge": {
            "name": badge.competency,
            "description": badge.description,
            "image": f"{base_url}{badge.image_url}",
            "criteria": f"{base_url}/badges/{badge.id}",
            "issuer": {
                "name": badge.issuer,
                "url": f"{base_url}/"
            }
        },
        "verification": {
            "type": "hosted"
        }
    }


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
    
    # Create instructor domains if registering as instructor with domains
    if payload.role.value == "instructor" and payload.domains:
        for domain in payload.domains:
            instructor_domain = InstructorDomain(
                instructor_id=user.id,
                competency=domain
            )
            db.add(instructor_domain)
        db.commit()
    
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
    return TokenResponse(access_token=token, role=user.role.value)


@app.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/competencies")
def get_competencies():
    """
    Parse rubric.md and return a list of competency names.
    Extracts headers in the format "# Competency: X"
    """
    rubric_path = Path(__file__).resolve().parent / "rubric.md"
    if not rubric_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rubric file not found",
        )
    
    rubric_content = rubric_path.read_text(encoding="utf-8")
    competency_pattern = r"# Competency:\s*(.+)"
    competencies = re.findall(competency_pattern, rubric_content)
    
    return competencies


@app.get("/me/report", response_model=UserReportResponse)
def get_my_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns the current user's full history: all their assessments and badges.
    """
    assessments = db.query(Assessment).filter(Assessment.user_id == current_user.id).all()
    badges = db.query(Badge).filter(Badge.user_id == current_user.id).all()
    
    return UserReportResponse(
        assessments=assessments,
        badges=badges
    )


@app.get("/instructor/domains")
def get_instructor_domains(
    current_user: User = Depends(require_role("instructor")),
    db: Session = Depends(get_db),
):
    """
    Returns the current instructor's list of taught domains.
    """
    domains = db.query(InstructorDomain).filter(InstructorDomain.instructor_id == current_user.id).all()
    return [domain.competency for domain in domains]


@app.get("/instructor/students", response_model=list[StudentReportResponse])
def get_instructor_students(
    current_user: User = Depends(require_role("instructor")),
    db: Session = Depends(get_db),
):
    """
    Returns students who have at least one assessment matching one of the instructor's domains.
    Response includes student_id, email, and which of the instructor's domains this student has activity in.
    """
    # Get instructor's domains
    instructor_domains = db.query(InstructorDomain).filter(InstructorDomain.instructor_id == current_user.id).all()
    domain_names = [domain.competency for domain in instructor_domains]
    
    if not domain_names:
        return []
    
    # Find students with assessments in these domains
    students_with_activity = db.query(User).join(Assessment).filter(
        User.role == ModelUserRole.student,
        Assessment.competency.in_(domain_names)
    ).distinct().all()
    
    result = []
    for student in students_with_activity:
        # Get which domains this student has activity in
        student_assessments = db.query(Assessment).filter(
            Assessment.user_id == student.id,
            Assessment.competency.in_(domain_names)
        ).all()
        student_domains = list(set([assessment.competency for assessment in student_assessments]))
        
        result.append(StudentReportResponse(
            student_id=student.id,
            email=student.email,
            competencies=student_domains
        ))
    
    return result


@app.get("/instructor/students/{student_id}/report", response_model=UserReportResponse)
def get_student_report(
    student_id: str,
    current_user: User = Depends(require_role("instructor")),
    db: Session = Depends(get_db),
):
    """
    Returns that student's assessments and badges, FILTERED to only competencies within the instructor's declared domains.
    Returns 403 if the student has no activity in any of the instructor's domains.
    """
    # Get instructor's domains
    instructor_domains = db.query(InstructorDomain).filter(InstructorDomain.instructor_id == current_user.id).all()
    domain_names = [domain.competency for domain in instructor_domains]
    
    if not domain_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor has no assigned domains"
        )
    
    # Check if student has activity in instructor's domains
    student_assessments = db.query(Assessment).filter(
        Assessment.user_id == student_id,
        Assessment.competency.in_(domain_names)
    ).all()
    
    if not student_assessments:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student has no activity in your assigned domains"
        )
    
    # Get student's badges in instructor's domains
    student_badges = db.query(Badge).filter(
        Badge.user_id == student_id,
        Badge.competency.in_(domain_names)
    ).all()
    
    return UserReportResponse(
        assessments=student_assessments,
        badges=student_badges
    )


@app.post("/instructor/students/{student_id}/suggest-activity", response_model=SuggestedActivityResponse, status_code=status.HTTP_201_CREATED)
def suggest_activity(
    student_id: str,
    payload: SuggestedActivityRequest,
    current_user: User = Depends(require_role("instructor")),
    db: Session = Depends(get_db),
):
    """
    Creates a suggested activity for a student.
    Verifies the competency is one of the instructor's declared domains (400 error if not).
    """
    # Verify the competency is in instructor's domains
    instructor_domain = db.query(InstructorDomain).filter(
        InstructorDomain.instructor_id == current_user.id,
        InstructorDomain.competency == payload.competency
    ).first()
    
    if not instructor_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are not authorized to suggest activities for competency: {payload.competency}"
        )
    
    # Verify student exists
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Create suggested activity
    suggested_activity = SuggestedActivity(
        instructor_id=current_user.id,
        student_id=student_id,
        competency=payload.competency,
        activity_type=payload.activity_type.value,
        message=payload.message
    )
    db.add(suggested_activity)
    db.commit()
    db.refresh(suggested_activity)
    
    return suggested_activity


@app.get("/instructor/students/{student_id}/suggestions", response_model=list[SuggestedActivityResponse])
def get_student_suggestions(
    student_id: str,
    current_user: User = Depends(require_role("instructor")),
    db: Session = Depends(get_db),
):
    """
    Returns all suggestions the current instructor has sent to this student.
    """
    suggestions = db.query(SuggestedActivity).filter(
        SuggestedActivity.instructor_id == current_user.id,
        SuggestedActivity.student_id == student_id
    ).all()
    
    return suggestions


@app.post("/submit", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def submit(
    payload: SubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = grade_submission(payload.code)

    assessment = Assessment(
        user_id=current_user.id,
        submission_text=payload.code,
        submission_type=payload.submission_type,
        competency=payload.competency,
        mastery_level=result["mastery_level"],
        confidence=result["confidence"],
        feedback=result["feedback"],
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    issued_badge = issue_badge_if_eligible(db, assessment, current_user)
    print(f"[DEBUG BADGE] Issued badge: {issued_badge}")
    
    return assessment


@app.get("/badges/my-badges", response_model=list[BadgeResponse])
def get_my_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    print(f"[DEBUG BADGE] Fetching badges for user {current_user.id}")
    badges = db.query(Badge).filter(Badge.user_id == current_user.id).all()
    return badges


@app.get("/badges/{badge_id}", response_model=OpenBadgeAssertion20)
def get_badge(badge_id: str, request: Request, db: Session = Depends(get_db)):
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found",
        )
    user = db.query(User).filter(User.id == badge.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Associated user not found")
        
    return build_badge_assertion(badge, user, request)


@app.get("/badges/{badge_id}/image")
def get_badge_image(badge_id: str, db: Session = Depends(get_db)):
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found",
        )
    
    file_path = os.path.join("static", "badges", f"{badge_id}.svg")
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    return FileResponse(file_path, media_type="image/svg+xml")


@app.post("/badges/{badge_id}/anchor")
def anchor_badge(
    badge_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    badge = db.query(models.Badge).filter(models.Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")

    user = db.query(models.User).filter(models.User.id == badge.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Associated user not found")

    assertion = build_badge_assertion(badge, user, request)
    print("\n[DEBUG ANCHOR PAYLOAD]:", json.dumps(assertion, sort_keys=True))

    try:
        tx_hash = anchor_badge_on_chain(badge.id, assertion)
        badge.blockchain_tx = tx_hash
        db.commit()
        db.refresh(badge)
        return {
            "message": "Badge successfully anchored on blockchain",
            "badge_id": badge.id,
            "blockchain_tx": tx_hash
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blockchain transaction failed: {str(e)}")


@app.get("/badges/{badge_id}/verify-on-chain")
def verify_badge_on_chain_endpoint(
    badge_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    badge = db.query(models.Badge).filter(models.Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")

    user = db.query(models.User).filter(models.User.id == badge.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Associated user not found")

    assertion = build_badge_assertion(badge, user, request)
    print("\n[DEBUG VERIFY PAYLOAD]:", json.dumps(assertion, sort_keys=True))
    
    try:
        verification_result = verify_badge_on_chain(badge.id, assertion)
        return verification_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"On-chain verification failed: {str(e)}")