import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Enum, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class UserRole(str, enum.Enum):
    student = "student"
    instructor = "instructor"


class SubmissionType(str, enum.Enum):
    assignment = "assignment"
    project = "project"


class ActivityType(str, enum.Enum):
    assignment = "assignment"
    project = "project"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    assessments: Mapped[list["Assessment"]] = relationship(back_populates="user")
    badges: Mapped[list["Badge"]] = relationship(back_populates="user")
    instructor_domains: Mapped[list["InstructorDomain"]] = relationship(back_populates="instructor")
    received_suggestions: Mapped[list["SuggestedActivity"]] = relationship(foreign_keys="SuggestedActivity.student_id")


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    submission_text: Mapped[str] = mapped_column(Text, nullable=False)
    submission_type: Mapped[SubmissionType] = mapped_column(Enum(SubmissionType), nullable=False)
    competency: Mapped[str] = mapped_column(String(255), nullable=False)
    mastery_level: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("suggested_activities.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="assessments")
    badge: Mapped["Badge"] = relationship(back_populates="assessment")


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    assessment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assessments.id"), unique=True, nullable=False
    )
    competency: Mapped[str] = mapped_column(String(255), nullable=False)
    achievement_level: Mapped[str] = mapped_column(String(50), nullable=False)
    issuer: Mapped[str] = mapped_column(
        String(255), default="ARSII / Skill Badge Platform", nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    issue_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    blockchain_tx: Mapped[str] = mapped_column(String(255), nullable=True, default=None)

    user: Mapped["User"] = relationship(back_populates="badges")
    assessment: Mapped["Assessment"] = relationship(back_populates="badge")


class InstructorDomain(Base):
    __tablename__ = "instructor_domains"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    instructor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    competency: Mapped[str] = mapped_column(String(255), nullable=False)

    instructor: Mapped["User"] = relationship(back_populates="instructor_domains")


class SuggestedActivity(Base):
    __tablename__ = "suggested_activities"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    instructor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    competency: Mapped[str] = mapped_column(String(255), nullable=False)
    activity_type: Mapped[ActivityType] = mapped_column(Enum(ActivityType), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    instructor: Mapped["User"] = relationship(foreign_keys="SuggestedActivity.instructor_id")
    student: Mapped["User"] = relationship(foreign_keys="SuggestedActivity.student_id")
    response_assessment: Mapped["Assessment"] = relationship(foreign_keys="Assessment.suggestion_id")
