import os
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from models import Badge, Assessment, User

def generate_badge_svg(badge_id: str, competency: str, mastery_level: str, recipient_name: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300">
    <path d="M150 10 L280 50 L280 150 C280 230 150 280 150 280 C150 280 20 230 20 150 L20 50 Z" fill="#2d3748" stroke="#4fd1c5" stroke-width="8" />
    <text x="150" y="80" font-family="Arial, sans-serif" font-size="20" fill="#ffffff" text-anchor="middle" font-weight="bold">SKILL BADGE</text>
    <text x="150" y="130" font-family="Arial, sans-serif" font-size="18" fill="#4fd1c5" text-anchor="middle">{competency}</text>
    <text x="150" y="170" font-family="Arial, sans-serif" font-size="16" fill="#e2e8f0" text-anchor="middle">Level: {mastery_level}</text>
    <text x="150" y="220" font-family="Arial, sans-serif" font-size="14" fill="#a0aec0" text-anchor="middle">Awarded to</text>
    <text x="150" y="245" font-family="Arial, sans-serif" font-size="16" fill="#ffffff" text-anchor="middle" font-style="italic">{recipient_name}</text>
    <text x="150" y="265" font-family="Arial, sans-serif" font-size="10" fill="#718096" text-anchor="middle">ID: {badge_id[:8]}</text>
</svg>"""

def save_badge_image(badge_id: str, svg_content: str) -> str:
    directory = os.path.join("static", "badges")
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{badge_id}.svg")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    return f"/static/badges/{badge_id}.svg"

def issue_badge_if_eligible(db: Session, assessment: Assessment, user: User) -> Optional[Badge]:
    # 1. Eligibility Check: Case-insensitive check for Level 2 or Level 3
    level_normalized = str(assessment.mastery_level).strip().title()
    if level_normalized not in ["Level 2", "Level 3"]:
        return None

    # 2. Prevent duplicate badge generation for the same assessment
    existing_badge = db.query(Badge).filter(Badge.assessment_id == assessment.id).first()
    if existing_badge:
        return existing_badge

    # 3. Generate unique UUID and image path
    badge_id = str(uuid.uuid4())
    recipient_display_name = user.fullname

    svg_content = generate_badge_svg(
        badge_id=badge_id,
        competency=assessment.competency,
        mastery_level=assessment.mastery_level,
        recipient_name=recipient_display_name
    )
    
    image_url = save_badge_image(badge_id, svg_content)

    # 4. Create and save Badge DB record
    new_badge = Badge(
        id=badge_id,
        user_id=user.id,
        assessment_id=assessment.id,
        competency=assessment.competency,
        achievement_level=assessment.mastery_level,
        issuer="ARSII / Skill Badge Platform",
        description=f"Demonstrated {assessment.mastery_level} competency in {assessment.competency}.",
        image_url=image_url
    )

    db.add(new_badge)
    db.commit()
    db.refresh(new_badge)

    return new_badge