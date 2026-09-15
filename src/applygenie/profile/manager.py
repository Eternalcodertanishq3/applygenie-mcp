"""User profile manager — CRUD operations on local JSON profile file."""

import json
import logging
from pathlib import Path
from typing import Any

try:
    from applygenie.config import PROFILE_PATH
except ImportError:
    import os
    PROFILE_PATH = Path(os.environ.get("APPLYGENIE_PROFILE_PATH", Path.home() / ".applygenie" / "profile.json"))

from applygenie.profile.schema import (
    UserProfile, Education, Experience, Project, Certification, Language, Location, SalaryRange
)

logger = logging.getLogger(__name__)

def load_profile() -> UserProfile | None:
    """Load profile from PROFILE_PATH, return None if not exists."""
    path = Path(PROFILE_PATH)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return UserProfile.model_validate(data)
    except Exception as e:
        logger.error(f"Failed to load profile: {e}")
        return None

def save_profile(profile: UserProfile) -> str:
    """Save profile to PROFILE_PATH, return filepath."""
    path = Path(PROFILE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
    return str(path)

def create_profile(**kwargs) -> UserProfile:
    """Create new profile from keyword args, save it."""
    profile = UserProfile(**kwargs)
    save_profile(profile)
    return profile

def update_profile_field(field: str, value: Any) -> UserProfile:
    """Update a specific top-level field."""
    profile = load_profile()
    if not profile:
        raise ValueError("Profile not found")
    setattr(profile, field, value)
    save_profile(profile)
    return profile

def add_education(education: Education) -> UserProfile:
    """Append to education list."""
    profile = load_profile()
    if not profile:
        raise ValueError("Profile not found")
    profile.education.append(education)
    save_profile(profile)
    return profile

def add_experience(experience: Experience) -> UserProfile:
    """Append to experiences list."""
    profile = load_profile()
    if not profile:
        raise ValueError("Profile not found")
    profile.experiences.append(experience)
    save_profile(profile)
    return profile

def add_project(project: Project) -> UserProfile:
    """Append to projects list."""
    profile = load_profile()
    if not profile:
        raise ValueError("Profile not found")
    profile.projects.append(project)
    save_profile(profile)
    return profile

def add_certification(cert: Certification) -> UserProfile:
    """Append to certifications list."""
    profile = load_profile()
    if not profile:
        raise ValueError("Profile not found")
    profile.certifications.append(cert)
    save_profile(profile)
    return profile

def add_skill(skill: str) -> UserProfile:
    """Append to skills list."""
    profile = load_profile()
    if not profile:
        raise ValueError("Profile not found")
    if skill not in profile.skills:
        profile.skills.append(skill)
    save_profile(profile)
    return profile

def save_custom_answer(question: str, answer: str) -> UserProfile:
    """Save reusable answer."""
    profile = load_profile()
    if not profile:
        raise ValueError("Profile not found")
    profile.custom_answers[question] = answer
    save_profile(profile)
    return profile

def get_profile_summary() -> dict:
    """Return a concise summary."""
    profile = load_profile()
    if not profile:
        return {}
    return {
        "name": profile.full_name,
        "email": profile.email,
        "phone": profile.phone,
        "skills_count": len(profile.skills),
        "experience_count": len(profile.experiences),
        "education_count": len(profile.education),
        "projects_count": len(profile.projects),
        "latest_education": profile.latest_education.degree if profile.latest_education else None,
        "years_of_experience": profile.years_of_experience
    }

def export_profile_for_form() -> dict:
    """Return flat dict suitable for form field mapping."""
    profile = load_profile()
    if not profile:
        return {}
    
    flat = {
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "email": profile.email,
        "phone": profile.phone,
        "city": profile.location.city,
        "state": profile.location.state or "",
        "country": profile.location.country,
        "pin_code": profile.location.pin_code or "",
        "linkedin_url": profile.linkedin_url or "",
        "github_url": profile.github_url or "",
        "portfolio_url": profile.portfolio_url or "",
        "website_url": profile.website_url or "",
        "work_authorization": profile.work_authorization.value,
        "willing_to_relocate": "Yes" if profile.willing_to_relocate else "No",
        "notice_period": profile.notice_period,
    }
    return flat
