"""ApplyGenie MCP Server — Your magical AI assistant that grants your job wishes.

This is the main entry point for the ApplyGenie MCP server.
It registers tools across all 5 operational pillars:
1. Desktop Control (Screenshots, Mouse, Keyboard, Window Management)
2. User Profile & Resume Management (CRUD, Parsing, Custom Answers)
3. Browser Automation & Form Filling (Playwright stealth, form detection, autofill, file upload)
4. Job Application Tracker (SQLite database, status tracking, search, analytics)
5. Mock Interview Preparation (Coding hint ladders, STAR behavioral coaching, system design)
"""

import json
import logging
from typing import Any

from fastmcp import FastMCP, Image as MCPImage

from applygenie.config import APP_NAME, APP_VERSION, ensure_data_dirs
from applygenie.core.keyboard import press_key, type_text
from applygenie.core.mouse import click, double_click, drag, get_position, move, right_click, scroll
from applygenie.core.safety import ActionType, safety
from applygenie.core.screenshot import capture_screenshot, get_screen_info
from applygenie.core.window import (
    find_windows,
    focus_window,
    get_active_window,
    list_windows,
    maximize_window,
    minimize_window,
)

# Profile Management
from applygenie.profile.manager import (
    load_profile,
    save_profile,
    create_profile,
    update_profile_field,
    add_experience,
    add_education,
    add_project,
    add_skill,
    save_custom_answer,
    get_profile_summary,
)
from applygenie.profile.schema import Education, Experience, Location, Project, UserProfile
from applygenie.profile.resume_parser import extract_resume_text

# Application Tracker
from applygenie.tracker.models import (
    log_application as db_log_application,
    update_application_status as db_update_status,
    get_application as db_get_application,
    list_applications as db_list_applications,
    search_applications as db_search_applications,
    delete_application as db_delete_application,
)
from applygenie.tracker.analytics import get_application_stats, get_weekly_application_velocity

# Mock Interview Engine
from applygenie.interview.engine import session_engine
from applygenie.interview.feedback import (
    format_coding_rubric,
    format_behavioral_rubric,
    format_system_design_rubric,
)

from applygenie.utils.logging import setup_logging

logger = logging.getLogger(__name__)

# Global singleton browser engine instance (lazy initialized)
_browser_engine = None


def _get_browser_engine():
    global _browser_engine
    if _browser_engine is None:
        try:
            from applygenie.browser.engine import BrowserEngine
            _browser_engine = BrowserEngine()
        except ImportError as err:
            raise RuntimeError(
                "Browser automation requires playwright. Install with: pip install 'applygenie-mcp[browser]' "
                "followed by: playwright install chromium"
            ) from err
    return _browser_engine


# Initialize FastMCP server
mcp = FastMCP(
    name="ApplyGenie",
    version=APP_VERSION,
    description=(
        "ApplyGenie 🧞‍♂️ — Your magical AI assistant that grants your job wishes. "
        "Desktop automation, job application form filling, application tracking, "
        "and company-specific mock interview preparation."
    ),
)


# ═══════════════════════════════════════════════════════════
# Phase 1 Tools: Desktop Control
# ═══════════════════════════════════════════════════════════


@mcp.tool()
def screenshot(monitor: int = 0) -> MCPImage:
    """Capture a screenshot of the display.

    Args:
        monitor: Monitor index. 0 = all monitors combined, 1 = primary monitor.
    """
    safety.log_action(ActionType.SCREENSHOT, {"monitor": monitor}, "capturing")
    b64, metadata = capture_screenshot(monitor)
    return MCPImage(data=b64, format="jpeg")


@mcp.tool()
def get_screen_size() -> dict[str, Any]:
    """Get information about all connected monitors including resolutions and bounds."""
    return get_screen_info()


@mcp.tool()
def mouse_click(x: int, y: int, button: str = "left", clicks: int = 1) -> str:
    """Click the mouse at specified screen coordinates.

    Args:
        x: X coordinate (pixels from left)
        y: Y coordinate (pixels from top)
        button: "left", "right", or "middle"
        clicks: Number of clicks (1 for single, 2 for double)
    """
    safety.check_failsafe(x, y)
    safety.check_rate_limit()
    safety.enforce_delay()
    result = click(x, y, button, clicks)
    safety.log_action(ActionType.MOUSE_CLICK, {"x": x, "y": y, "button": button, "clicks": clicks}, str(result))
    return str(result)


@mcp.tool()
def mouse_move(x: int, y: int) -> str:
    """Move the mouse cursor to specific coordinates."""
    safety.check_failsafe(x, y)
    safety.enforce_delay()
    result = move(x, y)
    safety.log_action(ActionType.MOUSE_MOVE, {"x": x, "y": y}, str(result))
    return str(result)


@mcp.tool()
def mouse_scroll(direction: str = "down", amount: int = 3) -> str:
    """Scroll the mouse wheel up or down."""
    safety.check_rate_limit()
    result = scroll(direction, amount)
    safety.log_action(ActionType.MOUSE_SCROLL, {"direction": direction, "amount": amount}, str(result))
    return str(result)


@mcp.tool()
def mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int) -> str:
    """Click and drag from a start position to an end position."""
    safety.check_failsafe(start_x, start_y)
    safety.check_failsafe(end_x, end_y)
    safety.check_rate_limit()
    safety.enforce_delay()
    result = drag(start_x, start_y, end_x, end_y)
    safety.log_action(ActionType.MOUSE_CLICK, {"start": (start_x, start_y), "end": (end_x, end_y)}, str(result))
    return str(result)


@mcp.tool()
def get_mouse_position() -> dict[str, Any]:
    """Get the current mouse cursor position coordinates."""
    return get_position()


@mcp.tool()
def type_text_input(text: str, interval: float = 0.03) -> str:
    """Type text using simulated keyboard with randomized human-like keystroke delays."""
    safety.check_rate_limit()
    safety.enforce_delay()
    result = type_text(text, interval)
    safety.log_action(ActionType.KEY_TYPE, {"text_length": len(text)}, str(result))
    return str(result)


@mcp.tool()
def press_keyboard_key(keys: str) -> str:
    """Press a key or key combination (e.g. 'enter', 'tab', 'ctrl+a', 'alt+tab')."""
    safety.check_rate_limit()
    safety.enforce_delay()
    result = press_key(keys)
    safety.log_action(ActionType.KEY_PRESS, {"keys": keys}, str(result))
    return str(result)


@mcp.tool()
def list_open_windows() -> list[dict[str, Any]]:
    """List all currently visible desktop windows with titles and geometry."""
    return list_windows()


@mcp.tool()
def focus_app_window(title: str) -> str:
    """Bring a desktop window to the foreground by its title (fuzzy match supported)."""
    safety.enforce_delay()
    result = focus_window(title)
    safety.log_action(ActionType.WINDOW_FOCUS, {"title": title}, str(result))
    return str(result)


@mcp.tool()
def minimize_app_window(title: str) -> str:
    """Minimize a window by title."""
    return str(minimize_window(title))


@mcp.tool()
def maximize_app_window(title: str) -> str:
    """Maximize a window by title."""
    return str(maximize_window(title))


@mcp.tool()
def get_current_window() -> dict[str, Any]:
    """Get information about the currently active focused window."""
    return get_active_window() or {"title": "Unknown", "is_active": False}


@mcp.tool()
def search_windows(pattern: str) -> list[dict[str, Any]]:
    """Search for windows matching a regex or substring pattern."""
    return find_windows(pattern)


@mcp.tool()
def wait_seconds(seconds: float = 1.0) -> str:
    """Pause execution for a specified duration (capped at 30 seconds for safety)."""
    import time
    seconds = min(seconds, 30.0)
    time.sleep(seconds)
    return f"Waited {seconds} seconds."


@mcp.tool()
def get_action_history(last_n: int = 20) -> list[dict[str, Any]]:
    """Inspect recent safety audit log records performed by ApplyGenie."""
    return safety.get_action_log(min(last_n, 100))


# ═══════════════════════════════════════════════════════════
# Phase 2 Tools: Profile & Resume Management
# ═══════════════════════════════════════════════════════════


@mcp.tool()
def get_user_profile() -> dict[str, Any]:
    """Retrieve the saved candidate profile for job applications."""
    profile = load_profile()
    if profile is None:
        return {"status": "not_found", "message": "No profile configured yet. Call setup_user_profile first."}
    return profile.model_dump()


@mcp.tool()
def get_user_profile_summary() -> dict[str, Any]:
    """Get a concise summary of candidate credentials, skills count, and experiences."""
    return get_profile_summary()


@mcp.tool()
def setup_user_profile(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    city: str,
    country: str,
    state: str | None = None,
    pin_code: str | None = None,
    linkedin_url: str | None = None,
    github_url: str | None = None,
    portfolio_url: str | None = None,
    skills: list[str] | None = None,
    notice_period: str = "Immediate",
    willing_to_relocate: bool = True,
    default_resume_path: str | None = None,
) -> dict[str, Any]:
    """Initialize or overwrite the candidate profile data."""
    loc = Location(city=city, state=state, country=country, pin_code=pin_code)
    prof = create_profile(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        location=loc,
        linkedin_url=linkedin_url,
        github_url=github_url,
        portfolio_url=portfolio_url,
        skills=skills or [],
        notice_period=notice_period,
        willing_to_relocate=willing_to_relocate,
        default_resume_path=default_resume_path,
    )
    return {"status": "success", "profile": prof.model_dump()}


@mcp.tool()
def update_profile_attribute(field_name: str, value: Any) -> dict[str, Any]:
    """Update a specific top-level field in the candidate profile."""
    prof = update_profile_field(field_name, value)
    return {"status": "updated", "field": field_name, "value": value}


@mcp.tool()
def add_work_experience(
    title: str,
    company: str,
    start_date: str,
    end_date: str | None = None,
    description: str = "",
    skills_used: list[str] | None = None,
    is_internship: bool = False,
) -> dict[str, Any]:
    """Add a work experience or internship entry to the candidate profile."""
    exp = Experience(
        title=title,
        company=company,
        start_date=start_date,
        end_date=end_date,
        description=description,
        skills_used=skills_used or [],
        is_internship=is_internship,
    )
    prof = add_experience(exp)
    return {"status": "success", "total_experiences": len(prof.experiences)}


@mcp.tool()
def add_education_entry(
    degree: str,
    field_of_study: str,
    university: str,
    graduation_year: int,
    gpa: float | None = None,
) -> dict[str, Any]:
    """Add an academic degree entry to the candidate profile."""
    edu = Education(
        degree=degree,
        field_of_study=field_of_study,
        university=university,
        graduation_year=graduation_year,
        gpa=gpa,
    )
    prof = add_education(edu)
    return {"status": "success", "total_education": len(prof.education)}


@mcp.tool()
def add_project_entry(
    name: str,
    description: str,
    tech_stack: list[str],
    url: str | None = None,
    github_url: str | None = None,
) -> dict[str, Any]:
    """Add a notable project to the candidate profile."""
    proj = Project(
        name=name,
        description=description,
        tech_stack=tech_stack,
        url=url,
        github_url=github_url,
    )
    prof = add_project(proj)
    return {"status": "success", "total_projects": len(prof.projects)}


@mcp.tool()
def save_portal_custom_answer(question_pattern: str, answer_text: str) -> dict[str, Any]:
    """Save a reusable answer for common portal questions (e.g. 'Why should we hire you?')."""
    prof = save_custom_answer(question_pattern, answer_text)
    return {"status": "saved", "pattern": question_pattern}


@mcp.tool()
def parse_resume_file(filepath: str) -> dict[str, Any]:
    """Extract raw text from a PDF or DOCX resume file."""
    text = extract_resume_text(filepath)
    return {"status": "extracted", "char_count": len(text), "preview": text[:500]}


# ═══════════════════════════════════════════════════════════
# Phase 3 Tools: Browser Automation & Form Filling
# ═══════════════════════════════════════════════════════════


@mcp.tool()
def browser_open(url: str | None = None, headless: bool = False) -> str:
    """Launch stealth Playwright browser and optionally navigate to an initial URL."""
    engine = _get_browser_engine()
    title = engine.launch(headless=headless)
    if url:
        return engine.navigate(url)
    return f"Stealth browser launched ({title})"


@mcp.tool()
def browser_navigate(url: str) -> str:
    """Navigate the active browser to a specific URL."""
    engine = _get_browser_engine()
    return engine.navigate(url)


@mcp.tool()
def browser_get_page_text() -> str:
    """Extract visible text content from the current active web page."""
    engine = _get_browser_engine()
    return engine.get_page_text()


@mcp.tool()
def browser_get_page_screenshot() -> MCPImage:
    """Capture a screenshot of the current active browser tab."""
    engine = _get_browser_engine()
    b64 = engine.get_page_screenshot()
    return MCPImage(data=b64, format="jpeg")


@mcp.tool()
def browser_detect_form_fields() -> dict[str, Any]:
    """Detect all inputs, textareas, selects, and upload fields on the current page."""
    engine = _get_browser_engine()
    from applygenie.browser.form_detector import detect_form_fields, detect_submit_button, get_form_summary
    page = engine.get_page()
    fields = detect_form_fields(page)
    submit_btn = detect_submit_button(page)
    summary = get_form_summary(fields)
    return {
        "fields_count": len(fields),
        "submit_button_detected": submit_btn,
        "summary": summary,
        "fields": [
            {
                "selector": f.selector,
                "label": f.label,
                "field_type": f.field_type,
                "required": f.required,
                "options": f.options,
                "placeholder": f.placeholder,
            }
            for f in fields
        ],
    }


@mcp.tool()
def browser_fill_detected_form() -> dict[str, Any]:
    """Intelligently map profile data and fill all detected form fields on the current page."""
    profile = load_profile()
    if not profile:
        return {"error": "No user profile found. Please run setup_user_profile first."}

    engine = _get_browser_engine()
    from applygenie.browser.form_detector import detect_form_fields
    from applygenie.browser.form_filler import fill_form_fields, generate_fill_report

    page = engine.get_page()
    fields = detect_form_fields(page)
    results = fill_form_fields(page, fields, profile)
    report = generate_fill_report(results)

    safety.log_action(ActionType.FORM_FILL, {"fields_count": len(fields)}, report)
    return {
        "status": "completed",
        "filled_report": report,
        "total_fields": len(fields),
        "filled_count": sum(1 for r in results if r.filled),
    }


@mcp.tool()
def browser_upload_resume(filepath: str | None = None) -> str:
    """Upload resume to the detected resume/CV file input field."""
    engine = _get_browser_engine()
    profile = load_profile()
    target_path = filepath or (profile.default_resume_path if profile else None)

    if not target_path:
        return "Error: No resume filepath specified and no default set in profile."

    from applygenie.browser.file_uploader import upload_resume
    from applygenie.browser.form_detector import detect_form_fields

    page = engine.get_page()
    fields = detect_form_fields(page)
    res = upload_resume(page, fields, profile or UserProfile(first_name="", last_name="", email="", phone="", location=Location(city="", country="")))
    safety.log_action(ActionType.FILE_UPLOAD, {"file": target_path}, res)
    return res


@mcp.tool()
def browser_submit_form(confirm: bool = False) -> str:
    """Submit the current form. REQUIRES explicit confirmation (confirm=True)."""
    if not confirm:
        return (
            "Safety Check: You must pass confirm=True to submit the application form. "
            "Please visually verify all filled values first using browser_get_page_screenshot."
        )

    engine = _get_browser_engine()
    from applygenie.browser.form_detector import detect_submit_button

    page = engine.get_page()
    btn = detect_submit_button(page)
    if not btn:
        return "Could not unambiguously detect the submit button. Please inspect the page."

    page.click(btn)
    safety.log_action(ActionType.FORM_SUBMIT, {"button": btn}, "submitted", success=True)
    return f"Successfully clicked submit button ({btn})."


@mcp.tool()
def browser_close() -> str:
    """Close the active browser instance."""
    engine = _get_browser_engine()
    engine.close()
    return "Browser closed."


# ═══════════════════════════════════════════════════════════
# Phase 4 Tools: Job Application Tracker & Analytics
# ═══════════════════════════════════════════════════════════


@mcp.tool()
def track_application(
    company: str,
    role: str,
    portal: str | None = None,
    url: str | None = None,
    resume_used: str | None = None,
    cover_letter_used: str | None = None,
    notes: str | None = None,
    salary_range: str | None = None,
    location: str | None = None,
    remote_type: str | None = None,
) -> dict[str, Any]:
    """Record a newly submitted job application in the local tracker database."""
    app_id = db_log_application(
        company=company,
        role=role,
        portal=portal,
        url=url,
        resume_used=resume_used,
        cover_letter_used=cover_letter_used,
        notes=notes,
        salary_range=salary_range,
        location=location,
        remote_type=remote_type,
    )
    return {"status": "logged", "application_id": app_id, "company": company, "role": role}


@mcp.tool()
def update_application_progress(
    application_id: int,
    status: str,
    notes: str | None = None,
) -> str:
    """Update application stage (e.g. 'interview', 'screening', 'technical', 'offer', 'rejected')."""
    return db_update_status(application_id, status, notes)


@mcp.tool()
def get_tracked_applications(
    status: str | None = None,
    company: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List tracked applications with optional status or company filters."""
    return db_list_applications(status=status, company=company, limit=limit)


@mcp.tool()
def search_tracked_applications(query: str) -> list[dict[str, Any]]:
    """Search tracked applications by keyword across company, role, and notes."""
    return db_search_applications(query)


@mcp.tool()
def get_application_analytics() -> dict[str, Any]:
    """Get aggregated statistics: total applications, interview conversion rate, offer rate, top portals."""
    return get_application_stats()


# ═══════════════════════════════════════════════════════════
# Phase 5 Tools: Mock Interview Engine
# ═══════════════════════════════════════════════════════════


@mcp.tool()
def start_mock_interview(
    interview_type: str,
    company: str = "General",
    difficulty: str = "medium",
) -> dict[str, Any]:
    """Begin an interactive mock interview session.

    Args:
        interview_type: "coding", "behavioral", or "system_design"
        company: Target company (e.g. "Amazon", "Google", "Meta", "General")
        difficulty: "easy", "medium", or "hard"
    """
    return session_engine.start_session(
        session_type=interview_type,
        company=company,
        difficulty=difficulty,
    )


@mcp.tool()
def get_coding_hint() -> dict[str, Any]:
    """Request the next Socratic hint rung for an active coding challenge."""
    return session_engine.get_hint()


@mcp.tool()
def analyze_behavioral_star_answer(response_text: str) -> dict[str, Any]:
    """Analyze a candidate behavioral response for STAR structure, 'I vs We' ownership ratio, and pacing."""
    return session_engine.analyze_behavioral_answer(response_text)


@mcp.tool()
def advance_system_design_interview(candidate_response: str) -> dict[str, Any]:
    """Submit architectural proposal for current system design phase and advance to next phase."""
    return session_engine.advance_system_design(candidate_response)


@mcp.tool()
def generate_interview_scorecard(
    interview_type: str,
    score_1: int,
    score_2: int,
    score_3: int,
    score_4: int,
    score_5: int = 4,
    feedback_notes: str = "",
) -> dict[str, Any]:
    """Generate a standardized 1-5 evaluation rubric and final hiring recommendation.

    Args:
        interview_type: "coding", "behavioral", or "system_design"
        score_1 through score_5: Integer scores between 1 and 5 for respective rubric criteria
        feedback_notes: Detailed coaching feedback for the candidate
    """
    match interview_type.lower():
        case "coding":
            return format_coding_rubric(score_1, score_2, score_3, score_4, feedback_notes)
        case "behavioral":
            return format_behavioral_rubric(score_1, score_2, score_3, score_4, score_5, feedback_notes)
        case "system_design" | "system-design":
            return format_system_design_rubric(score_1, score_2, score_3, score_4, score_5, feedback_notes)
        case _:
            return {"error": f"Unknown interview type: {interview_type}"}


# ═══════════════════════════════════════════════════════════
# Server Entry Point
# ═══════════════════════════════════════════════════════════


def main():
    """Start the ApplyGenie MCP server."""
    ensure_data_dirs()
    setup_logging()
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} (MCP Stdio)")
    mcp.run()


if __name__ == "__main__":
    main()
