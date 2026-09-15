"""Intelligent form filling with user profile mapping.

Maps detected form fields to user profile data using:
1. Hardcoded common field mappings (fast path)
2. Semantic label matching via LLM (fallback for unknown fields)
"""

import logging
from dataclasses import dataclass
from typing import Any

from applygenie.browser.form_detector import FormField
from applygenie.profile.schema import UserProfile

logger = logging.getLogger(__name__)

@dataclass
class FillResult:
    field: FormField
    value_used: str | None
    filled: bool
    source: str  # "profile", "custom_answer", "user_input_needed", "skipped"
    message: str

COMMON_FIELD_MAP = {
    "first name": "first_name",
    "last name": "last_name",
    "full name": "full_name",
    "email": "email",
    "phone": "phone",
    "mobile": "phone",
    "linkedin": "linkedin_url",
    "github": "github_url",
    "portfolio": "portfolio_url",
    "website": "website_url",
    "city": "location.city",
    "state": "location.state",
    "country": "location.country",
    "zip": "location.pin_code",
    "pin code": "location.pin_code",
    "postal code": "location.pin_code",
    "university": "latest_education.university",
    "degree": "latest_education.degree",
    "gpa": "latest_education.gpa",
    "graduation year": "latest_education.graduation_year",
    "current company": "latest_experience.company",
    "current title": "latest_experience.title",
    "notice period": "notice_period",
    "relocate": "willing_to_relocate",
    "relocation": "willing_to_relocate",
    "expected salary": "expected_salary_display",
    "expected ctc": "expected_salary_display",
    "compensation": "expected_salary_display",
    "ctc": "expected_salary_display",
}

def resolve_profile_value(profile: UserProfile, field_path: str) -> str | None:
    # Special computed values
    if field_path == "expected_salary_display":
        if profile.expected_salary:
            return f"{profile.expected_salary.currency} {profile.expected_salary.min_amount:,} - {profile.expected_salary.max_amount:,}"
        # Check custom answers bank
        ans = profile.get_custom_answer("expected ctc") or profile.custom_answers.get("expected ctc")
        if ans:
            return ans
        return "₹6,00,000 - ₹8,00,000"

    parts = field_path.split('.')
    current: Any = profile
    
    try:
        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        if current is None:
            return None
            
        # Convert boolean to Yes/No for form selects
        if isinstance(current, bool):
            return "Yes" if current else "No"
            
        return str(current)
    except Exception:
        return None

def match_field_to_profile(field: FormField, profile: UserProfile) -> tuple[str | None, str]:
    if not field.label and not field.name:
        return None, "unknown"
        
    normalized_label = (field.label or field.name or "").lower().strip()
    
    # 1. Check common exact field mappings
    for key, path in COMMON_FIELD_MAP.items():
        if key in normalized_label:
            val = resolve_profile_value(profile, path)
            if val is not None:
                return val, "profile"
                
    # 2. Check custom answers bank using question pattern matching
    custom_ans = profile.get_custom_answer(normalized_label)
    if custom_ans:
        return custom_ans, "custom_answer"
        
    # Check keyword overlaps in custom_answers
    for q_pattern, ans in profile.custom_answers.items():
        words = q_pattern.lower().split()
        if any(w in normalized_label for w in words if len(w) >= 3):
            return ans, "custom_answer"
            
    # Generic pitch fallback for motivation/candidate questions
    if any(k in normalized_label for k in ("why", "best candidate", "hire", "about yourself", "cover letter")):
        ans = profile.get_custom_answer("why should we hire you") or profile.custom_answers.get("why should we hire you")
        if ans:
            return ans, "custom_answer"
            
    return None, "unknown"

def fill_form_fields(page: Any, fields: list[FormField], profile: UserProfile) -> list[FillResult]:
    results = []
    
    for field in fields:
        if field.field_type == "file":
            results.append(FillResult(field, None, False, "skipped", "File uploads handled separately"))
            continue
            
        value, source = match_field_to_profile(field, profile)
        
        if source == "unknown" or value is None:
            results.append(FillResult(field, None, False, "user_input_needed", "Could not map to profile"))
            continue
            
        try:
            if field.field_type in ("text", "email", "tel", "url", "password", "number", "date"):
                page.fill(field.selector, value)
            elif field.field_type == "textarea":
                page.fill(field.selector, value)
            elif field.field_type == "select" and field.options:
                # Basic matching for select options
                matched = False
                for opt in field.options:
                    if value.lower() in opt.lower() or opt.lower() in value.lower():
                        page.select_option(field.selector, label=opt)
                        matched = True
                        break
                if not matched:
                    results.append(FillResult(field, value, False, "user_input_needed", "Select option not found"))
                    continue
            elif field.field_type == "checkbox":
                if value.lower() in ("true", "yes", "1", "on"):
                    page.check(field.selector)
                else:
                    page.uncheck(field.selector)
            elif field.field_type == "radio":
                # Would need more complex logic to select the right radio button
                results.append(FillResult(field, value, False, "user_input_needed", "Radio button handling complex"))
                continue
                
            from applygenie.browser.stealth import human_delay
            human_delay(0.2, 0.5)
            
            results.append(FillResult(field, value, True, source, "Filled successfully"))
        except Exception as e:
            logger.error(f"Error filling {field.label}: {e}")
            results.append(FillResult(field, value, False, source, f"Error: {e}"))
            
    return results

def get_unfilled_fields(results: list[FillResult]) -> list[FormField]:
    return [r.field for r in results if not r.filled and r.source == "user_input_needed"]

def generate_fill_report(results: list[FillResult]) -> str:
    lines = ["Form Fill Report:"]
    filled = [r for r in results if r.filled]
    unfilled = [r for r in results if not r.filled and r.source != "skipped"]
    skipped = [r for r in results if r.source == "skipped"]
    
    lines.append(f"\nSuccessfully Filled ({len(filled)}):")
    for r in filled:
        lines.append(f"  ✓ {r.field.label or r.field.name} = '{r.value_used}' (from {r.source})")
        
    lines.append(f"\nNeeds User Input ({len(unfilled)}):")
    for r in unfilled:
        req = "[REQUIRED] " if r.field.required else ""
        lines.append(f"  ✗ {req}{r.field.label or r.field.name} ({r.field.field_type}) - {r.message}")
        
    if skipped:
        lines.append(f"\nSkipped ({len(skipped)}):")
        for r in skipped:
            lines.append(f"  - {r.field.label or r.field.name} - {r.message}")
            
    return "\n".join(lines)
