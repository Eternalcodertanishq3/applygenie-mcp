"""Tests for User Profile Manager and Schema validation."""

import pytest
from applygenie.profile.schema import (
    UserProfile, Location, Experience, Education, Project, WorkAuthorization
)
from applygenie.profile.manager import (
    create_profile, load_profile, save_profile, update_profile_field, add_skill, add_experience
)


def test_user_profile_creation(tmp_path, monkeypatch):
    test_profile_path = tmp_path / "test_profile.json"
    monkeypatch.setattr("applygenie.profile.manager.PROFILE_PATH", test_profile_path)

    loc = Location(city="Hindaun City", state="Rajasthan", country="India", pin_code="322230")
    profile = create_profile(
        first_name="Tanishq",
        last_name="Mangal",
        email="tanishkmangal3@gmail.com",
        phone="+91 6367733171",
        location=loc,
        linkedin_url="https://linkedin.com/in/tanishq",
        github_url="https://github.com/Eternalcodertanishq3",
        skills=["Python", "PyTorch", "FastAPI"],
    )

    assert profile.full_name == "Tanishq Mangal"
    assert profile.location.city == "Hindaun City"
    assert "Python" in profile.skills

    # Test load
    loaded = load_profile()
    assert loaded is not None
    assert loaded.email == "tanishkmangal3@gmail.com"

    # Test add skill
    updated = add_skill("Docker")
    assert "Docker" in updated.skills

    # Test add experience
    exp = Experience(
        title="AI Engineer Intern",
        company="Avinya Biomedical",
        start_date="Jun 2025",
        end_date="Aug 2025",
        description="Built computer vision diagnostics pipeline.",
        skills_used=["PyTorch", "OpenCV"],
        is_internship=True,
    )
    updated_with_exp = add_experience(exp)
    assert len(updated_with_exp.experiences) == 1
    assert updated_with_exp.experiences[0].company == "Avinya Biomedical"
