"""User profile data models for ApplyGenie.

Pydantic v2 models representing all data needed to fill any job application form.
"""

from datetime import date, datetime
from pydantic import BaseModel, Field
from enum import Enum
import re

class WorkAuthorization(str, Enum):
    CITIZEN = "CITIZEN"
    PERMANENT_RESIDENT = "PERMANENT_RESIDENT"
    VISA_REQUIRED = "VISA_REQUIRED"
    OTHER = "OTHER"

class Proficiency(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"
    NATIVE = "NATIVE"

class Location(BaseModel):
    city: str
    state: str | None = None
    country: str
    pin_code: str | None = None

class SalaryRange(BaseModel):
    min_amount: int
    max_amount: int
    currency: str = "INR"
    period: str = "yearly"

class Education(BaseModel):
    degree: str
    field_of_study: str
    university: str
    graduation_year: int
    gpa: float | None = None
    gpa_scale: float = 10.0

class Experience(BaseModel):
    title: str
    company: str
    location: str | None = None
    start_date: str
    end_date: str | None = None
    description: str
    skills_used: list[str] = Field(default_factory=list)
    is_internship: bool = False

class Project(BaseModel):
    name: str
    description: str
    tech_stack: list[str] = Field(default_factory=list)
    url: str | None = None
    github_url: str | None = None
    start_date: str | None = None
    end_date: str | None = None

class Certification(BaseModel):
    name: str
    issuer: str
    date_obtained: str | None = None
    credential_id: str | None = None
    url: str | None = None

class Language(BaseModel):
    language: str
    proficiency: Proficiency

class EEOData(BaseModel):
    gender: str | None = None
    race_ethnicity: str | None = None
    veteran_status: str | None = None
    disability_status: str | None = None

class UserProfile(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    location: Location
    date_of_birth: date | None = None
    gender: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    website_url: str | None = None
    education: list[Education] = Field(default_factory=list)
    experiences: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    work_authorization: WorkAuthorization = WorkAuthorization.CITIZEN
    willing_to_relocate: bool = True
    preferred_locations: list[str] = Field(default_factory=list)
    notice_period: str = "Immediate"
    expected_salary: SalaryRange | None = None
    open_to_remote: bool = True
    travel_domestically: bool = True
    travel_internationally: bool = False
    default_resume_path: str | None = None
    default_cover_letter_path: str | None = None
    resumes: dict[str, str] = Field(default_factory=dict)
    custom_answers: dict[str, str] = Field(default_factory=dict)
    eeo_data: EEOData | None = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self) -> str:
        parts = [self.location.city]
        if self.location.state:
            parts.append(self.location.state)
        parts.append(self.location.country)
        if self.location.pin_code:
            parts.append(self.location.pin_code)
        return ", ".join(parts)

    @property
    def years_of_experience(self) -> float:
        total_months = 0
        for exp in self.experiences:
            try:
                start = datetime.strptime(exp.start_date, "%b %Y")
                end = datetime.strptime(exp.end_date, "%b %Y") if exp.end_date else datetime.now()
                total_months += (end.year - start.year) * 12 + (end.month - start.month)
            except ValueError:
                pass
        return round(total_months / 12, 1)

    @property
    def latest_education(self) -> Education | None:
        if not self.education:
            return None
        return max(self.education, key=lambda e: e.graduation_year)

    def get_custom_answer(self, question: str) -> str | None:
        question_lower = question.lower()
        for q, a in self.custom_answers.items():
            if q.lower() in question_lower or question_lower in q.lower():
                return a
        return None
