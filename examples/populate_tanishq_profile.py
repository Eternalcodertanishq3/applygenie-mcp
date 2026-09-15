import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from applygenie.profile.schema import Location, Experience, Education, Project, WorkAuthorization
from applygenie.profile.manager import (
    create_profile, add_experience, add_education, add_project, save_custom_answer, get_profile_summary
)
from applygenie.tracker.models import log_application
from applygenie.tracker.analytics import get_application_stats

print("=== SEEDING TANISHQ'S LIVE PROFILE INTO APPLYGENIE ===")

loc = Location(
    city="Hindaun City",
    state="Rajasthan",
    country="India",
    pin_code="322230"
)

profile = create_profile(
    first_name="Tanishq",
    last_name="Mangal",
    email="tanishkmangal3@gmail.com",
    phone="+91 6367733171",
    location=loc,
    linkedin_url="https://linkedin.com/in/tanishq-mangal",
    github_url="https://github.com/Eternalcodertanishq3",
    portfolio_url="https://tanishq-creates.netlify.app/",
    skills=[
        "Python", "PyTorch", "FastAPI", "React", "Node.js", "Docker",
        "Computer Vision", "Vector Databases", "pgvector", "FAISS",
        "PostgreSQL", "C++", "Rust", "LLMs", "RAG"
    ],
    work_authorization=WorkAuthorization.CITIZEN,
    willing_to_relocate=True,
    preferred_locations=["Bangalore", "Vadodara", "Jaipur", "Remote"],
    notice_period="Immediate",
    open_to_remote=True,
    default_resume_path=r"C:\Personal Projects\resume generator\Tanishq_Mangal_Cyncly_AIML_Resume.pdf",
    default_cover_letter_path=r"C:\Personal Projects\resume generator\Tanishq_Mangal_Cyncly_Cover_Letter.pdf"
)

# Add Education
add_education(Education(
    degree="B.Tech Computer Science and Engineering",
    field_of_study="Computer Science",
    university="Parul University",
    graduation_year=2026,
    gpa=7.72,
    gpa_scale=10.0
))

# Add Experiences
add_experience(Experience(
    title="AI/ML Engineer Intern",
    company="Jashma Infosoft Pvt Ltd",
    location="Vadodara, India",
    start_date="Jan 2026",
    end_date="Apr 2026",
    description="Developed high-throughput API endpoints and integrated computer vision & NLP models into client-facing platforms.",
    skills_used=["Python", "FastAPI", "Docker", "PyTorch"],
    is_internship=True
))

add_experience(Experience(
    title="Computer Vision Intern",
    company="Avinya Biomedical",
    location="Remote",
    start_date="Jun 2025",
    end_date="Aug 2025",
    description="Built automated medical diagnostic segmentation pipelines using OpenCV and PyTorch deep convolutional networks.",
    skills_used=["Python", "PyTorch", "OpenCV", "ResNet"],
    is_internship=True
))

# Add Key Projects
add_project(Project(
    name="Semantic-6G",
    description="Neural semantic communication system compressing telemetry over wireless channels using autoencoders.",
    tech_stack=["PyTorch", "Python", "NumPy"],
    github_url="https://github.com/Eternalcodertanishq3/Semantic-6G"
))

add_project(Project(
    name="Axiorynth",
    description="Grandmaster-grade chess platform featuring a custom Rust bitboard engine and real-time kinetic telemetry.",
    tech_stack=["Rust", "Axum", "Next.js", "WebSockets"],
    github_url="https://github.com/Eternalcodertanishq3/Axiorynth"
))

# Add Common Reusable Portal Answers
save_custom_answer(
    "why should we hire you",
    "I combine rigorous systems-level engineering in Rust and C++ with production-ready AI engineering in PyTorch, FastAPI, and Docker. As an immediate joiner based in Hindaun City willing to relocate to Bangalore or work remotely, I hit the ground running shipping robust code on day one."
)

save_custom_answer(
    "expected ctc",
    "6,00,000 - 8,00,000 INR per annum (negotiable based on role scope and benefits)"
)

# Log the Cyncly job we worked on into the Tracker
log_application(
    company="Cyncly",
    role="AI/ML Engineer",
    portal="Oracle Cloud",
    url="https://cyncly.oraclecloud.com/",
    resume_used=r"C:\Personal Projects\resume generator\Tanishq_Mangal_Cyncly_AIML_Resume.pdf",
    cover_letter_used=r"C:\Personal Projects\resume generator\Tanishq_Mangal_Cyncly_Cover_Letter.pdf",
    notes="Tailored for Computer Vision + Vector DBs + FastAPI serving. Immediate Bangalore relocation.",
    salary_range="6-8 LPA",
    location="Bangalore",
    remote_type="On-site / Hybrid"
)

print("\n--- PROFILE SUMMARY ---")
summary = get_profile_summary()
for k, v in summary.items():
    print(f"  {k}: {v}")

print("\n--- TRACKER ANALYTICS ---")
stats = get_application_stats()
print(f"  Total Applications Logged: {stats['total_applications']}")
print(f"  Top Portals: {stats['portal_breakdown']}")

print("\n>>> APPLYGENIE BRAIN FULLY PRIMED & READY FOR AUTONOMOUS ACTIONS! <<<")
