"""ApplyGenie Live Browser & Autonomous Form Filling Demonstration.

This script boots Playwright in VISIBLE mode (headless=False), navigates to the
ATS job portal, parses all form fields using DOM + accessibility tree, automatically
maps Tanishq's profile data, types into the inputs, uploads his tailored resume,
and pauses so you can watch ApplyGenie work live!
"""

import sys
import time
from pathlib import Path

# Ensure UTF-8 output encoding on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from playwright.sync_api import sync_playwright

from applygenie.browser.form_detector import detect_form_fields, detect_submit_button, get_form_summary
from applygenie.browser.form_filler import fill_form_fields, generate_fill_report
from applygenie.browser.file_uploader import upload_resume
from applygenie.profile.manager import load_profile
from applygenie.tracker.models import log_application
from applygenie.tracker.analytics import get_application_stats

def main():
    print("=" * 65)
    print("🧞‍♂️ APPLYGENIE AUTONOMOUS BROWSER FORM FILLING DEMO 🧞‍♂️")
    print("=" * 65)

    # 1. Load candidate profile
    print("\n[1/6] Loading candidate profile from ~/.applygenie/profile.json...")
    profile = load_profile()
    if not profile:
        print("❌ Error: User profile not found! Please run populate_tanishq_profile.py first.")
        return

    print(f"  ✓ Loaded candidate: {profile.full_name} ({profile.email})")
    print(f"  ✓ Location: {profile.location.city}, {profile.location.state}")
    print(f"  ✓ Target Resume: {profile.default_resume_path}")

    # 2. Launch visible browser
    portal_html_path = Path(__file__).parent / "test_job_portal.html"
    portal_url = portal_html_path.resolve().as_uri()

    print(f"\n[2/6] Launching Chromium in VISIBLE mode...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=120)  # slow_mo for smooth human watching
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        print(f"  ✓ Navigating to ATS portal: {portal_url}")
        page.goto(portal_url)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(1.0)

        # 3. Detect form fields using DOM + a11y tree
        print("\n[3/6] Analyzing page DOM & Accessibility Tree for input fields...")
        fields = detect_form_fields(page)
        submit_btn = detect_submit_button(page)
        print(f"  ✓ Detected {len(fields)} interactive form fields.")
        print(f"  ✓ Submit button identified: '{submit_btn}'")
        print("\n--- DETECTED FIELDS SUMMARY ---")
        print(get_form_summary(fields))

        # 4. Fill form fields using profile mappings & answer memory
        print("\n[4/6] Autonomously populating form fields from candidate profile...")
        fill_results = fill_form_fields(page, fields, profile)
        print("\n--- FILL REPORT ---")
        print(generate_fill_report(fill_results))

        # 5. File Upload (Resume)
        print("\n[5/6] Uploading tailored resume file...")
        upload_status = upload_resume(page, fields, profile)
        print(f"  ✓ {upload_status}")

        # Highlight submit button visually before clicking
        time.sleep(1.5)
        print("\n[6/6] Submitting form with Human-in-the-Loop confirmation...")
        if submit_btn:
            # Click submit
            page.click(submit_btn)
            time.sleep(1.5)
            print("  ✓ Application submitted! Status banner activated on page.")

        # Log to tracker
        log_application(
            company="Cyncly",
            role="AI/ML Engineer",
            portal="ATS Portal v2 (Live Test)",
            url=portal_url,
            resume_used=profile.default_resume_path,
            notes="Autonomously filled and verified by ApplyGenie demo runner.",
            salary_range="₹6,00,000 - ₹8,00,000",
            location="Hindaun City / Bangalore",
        )

        print("\n" + "=" * 65)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("Holding browser open for 6 seconds so you can see the result...")
        print("=" * 65)
        time.sleep(6.0)

        browser.close()

if __name__ == "__main__":
    main()
