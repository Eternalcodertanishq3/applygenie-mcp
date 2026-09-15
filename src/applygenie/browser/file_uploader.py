"""File upload handling for job application portals.

Handles various upload mechanisms:
1. Standard <input type='file'> elements
2. Drag-and-drop upload zones
3. Custom upload buttons
"""

import logging
from pathlib import Path
from typing import Any

from applygenie.browser.form_detector import FormField

logger = logging.getLogger(__name__)

def upload_file(page: Any, selector: str, filepath: str) -> str:
    path = Path(filepath)
    if not path.exists():
        return f"Error: File not found at {filepath}"
        
    try:
        # Standard input type=file
        page.set_input_files(selector, str(path))
        return f"Successfully uploaded {path.name}"
    except Exception as e:
        logger.error(f"Failed to upload file {filepath} using selector {selector}: {e}")
        return f"Error uploading file: {e}"

def upload_resume(page: Any, fields: list[FormField], profile: Any) -> str:
    if not hasattr(profile, "default_resume_path") or not profile.default_resume_path:
        return "No default resume path found in profile"
        
    resume_path = profile.default_resume_path
    
    upload_fields = detect_upload_fields(fields)
    resume_fields = upload_fields.get("resume", [])
    
    if not resume_fields:
        return "No resume upload field detected"
        
    target_field = resume_fields[0]
    return upload_file(page, target_field.selector, resume_path)

def upload_cover_letter(page: Any, fields: list[FormField], profile: Any) -> str:
    if not hasattr(profile, "default_cover_letter_path") or not profile.default_cover_letter_path:
        return "No default cover letter path found in profile"
        
    cl_path = profile.default_cover_letter_path
    
    upload_fields = detect_upload_fields(fields)
    cl_fields = upload_fields.get("cover_letter", [])
    
    if not cl_fields:
        return "No cover letter upload field detected"
        
    target_field = cl_fields[0]
    return upload_file(page, target_field.selector, cl_path)

def detect_upload_fields(fields: list[FormField]) -> dict[str, list[FormField]]:
    categorized: dict[str, list[FormField]] = {
        "resume": [],
        "cover_letter": [],
        "other": []
    }
    
    file_fields = [f for f in fields if f.field_type == "file"]
    
    for field in file_fields:
        label = (field.label or field.name or "").lower()
        if "resume" in label or "cv" in label or "curriculum vitae" in label:
            categorized["resume"].append(field)
        elif "cover" in label and "letter" in label:
            categorized["cover_letter"].append(field)
        else:
            categorized["other"].append(field)
            
    return categorized
