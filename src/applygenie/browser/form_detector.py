"""Hybrid form field detection using DOM parsing and accessibility tree.

Detects form fields on any web page by combining:
1. Standard HTML input/select/textarea elements
2. Accessibility tree parsing for custom components
3. Label-to-field association via 'for' attribute, aria-label, proximity
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class FormField:
    selector: str
    label: str
    field_type: str
    required: bool = False
    options: list[str] | None = None
    current_value: str | None = None
    placeholder: str | None = None
    name: str | None = None
    element_id: str | None = None

def detect_form_fields(page: Any) -> list[FormField]:
    # Use page.evaluate to run JS that finds form fields and their labels
    # This is much faster and more reliable than multiple locator calls
    script = """
    () => {
        const fields = [];
        const elements = document.querySelectorAll('input:not([type="hidden"]), select, textarea');
        
        elements.forEach((el, index) => {
            const rect = el.getBoundingClientRect();
            // Skip hidden elements
            if (rect.width === 0 || rect.height === 0) return;
            
            let label = el.getAttribute('aria-label') || '';
            const id = el.id;
            
            if (!label && id) {
                const labelEl = document.querySelector(`label[for="${id}"]`);
                if (labelEl) label = labelEl.innerText;
            }
            
            if (!label) {
                let current = el;
                while (current.parentElement && current.parentElement.tagName !== 'BODY') {
                    if (current.parentElement.tagName === 'LABEL') {
                        const clone = current.parentElement.cloneNode(true);
                        const inputs = clone.querySelectorAll('input, select, textarea');
                        inputs.forEach(i => i.remove());
                        label = clone.innerText.trim();
                        break;
                    }
                    current = current.parentElement;
                }
            }
            
            if (!label) label = el.getAttribute('placeholder') || '';
            
            const fieldType = el.tagName.toLowerCase() === 'input' ? (el.type || 'text') : el.tagName.toLowerCase();
            
            let options = null;
            if (fieldType === 'select') {
                options = Array.from(el.options).map(opt => opt.text);
            }
            
            // Assign a unique attribute for our selector if needed, or use a robust CSS selector
            el.setAttribute('data-applygenie-idx', index.toString());
            const selector = `${el.tagName.toLowerCase()}[data-applygenie-idx="${index}"]`;
            
            fields.push({
                selector: selector,
                label: label.trim(),
                field_type: fieldType,
                required: el.required || el.getAttribute('aria-required') === 'true',
                options: options,
                current_value: el.value,
                placeholder: el.getAttribute('placeholder') || null,
                name: el.name || null,
                element_id: id || null,
                top: rect.top
            });
        });
        
        // Sort by visual position
        fields.sort((a, b) => a.top - b.top);
        return fields;
    }
    """
    
    try:
        raw_fields = page.evaluate(script)
        results = []
        for rf in raw_fields:
            rf.pop('top', None)  # Remove internal sorting property
            results.append(FormField(**rf))
        return results
    except Exception as e:
        logger.error(f"Error detecting form fields: {e}")
        return []

def detect_submit_button(page: Any) -> str | None:
    selectors = [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Submit')",
        "button:has-text('Apply')",
        "button:has-text('Send')",
        "button:has-text('Continue')"
    ]
    for selector in selectors:
        if page.locator(selector).count() > 0:
            return selector
    return None

def get_form_summary(fields: list[FormField]) -> str:
    lines = [f"Found {len(fields)} form fields:"]
    for i, field in enumerate(fields, 1):
        req = "[required] " if field.required else ""
        opts = f" - options: {field.options}" if field.options else ""
        val = f" - currently: '{field.current_value}'" if field.current_value else " - currently empty"
        if field.field_type == "file":
            val = " - no file selected" if not field.current_value else f" - selected: {field.current_value}"
            
        lines.append(f"{i}. {req}{field.label or (field.name or 'Unknown')} ({field.field_type}){opts}{val}")
    
    return "\n".join(lines)
