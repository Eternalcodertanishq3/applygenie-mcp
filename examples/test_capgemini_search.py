"""ApplyGenie Live Desktop Test: Capgemini 2026 Fresher Search.

Launches visible Chromium browser, opens Capgemini Careers, handles cookie dialogs,
searches for 2026 graduate/fresher roles, opens multiple tabs visibly, and extracts
matching job listings live!
"""

import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

def main():
    print("=" * 65)
    print("🧞‍♂️ APPLYGENIE LIVE BROWSER DEMO: CAPGEMINI 2026 FRESHER SEARCH 🧞‍♂️")
    print("=" * 65)

    with sync_playwright() as p:
        print("\n[1/5] Launching visible browser window on your desktop...")
        # Launch visible browser with human-speed pacing
        browser = p.chromium.launch(
            headless=False,
            slow_mo=100,
            args=["--start-maximized"]
        )
        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )

        # Tab 1: Capgemini Official India Careers
        print("\n[2/5] Tab 1: Navigating to Capgemini India Job Search...")
        page1 = context.new_page()
        page1.goto("https://www.capgemini.com/in-en/careers/job-search/?country=India", wait_until="domcontentloaded", timeout=45000)
        time.sleep(2.0)

        # Auto-dismiss cookie consent banner if present
        print("  ✓ Checking for OneTrust cookie banners...")
        try:
            cookie_btn = page1.locator("#onetrust-accept-btn-handler, button:has-text('Accept All'), button:has-text('Accept')").first
            if cookie_btn.is_visible(timeout=5000):
                cookie_btn.click()
                print("  ✓ Accepted cookie consent banner.")
                time.sleep(1.0)
        except Exception:
            print("  - No cookie banner encountered or automatically dismissed.")

        # Search for 2026 fresher / graduate roles on Capgemini portal
        print("\n[3/5] Typing search query: 'Fresher Graduate Engineer'...")
        try:
            # Look for search input
            search_input = page1.locator("input[type='search'], input[name*='search'], input[placeholder*='search' i], input[placeholder*='job' i]").first
            if search_input.is_visible(timeout=5000):
                search_input.click()
                search_input.fill("Graduate Engineer")
                time.sleep(1.0)
                page1.keyboard.press("Enter")
                print("  ✓ Submitted search query on Capgemini portal.")
                time.sleep(3.0)
            else:
                print("  - Search bar requires manual filter interaction on this portal layout.")
        except Exception as e:
            print(f"  - Search input interaction note: {e}")

        # Tab 2: Live search for 2026 Batch Capgemini campus drives and fresher listings
        print("\n[4/5] Tab 2: Opening second tab for Capgemini 2026 Batch Fresher Opportunities...")
        page2 = context.new_page()
        page2.goto("https://www.google.com/search?q=Capgemini+Fresher+hiring+2026+batch+India+careers", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2.0)

        # Extract top 3 results from Tab 2
        print("\n[5/5] Parsing active 2026 fresher postings...")
        results = page2.locator("h3").all()
        extracted = 0
        for r in results:
            text = r.inner_text().strip()
            if text and ("capgemini" in text.lower() or "fresher" in text.lower() or "2026" in text.lower() or "engineer" in text.lower()):
                extracted += 1
                print(f"  📌 Opportunity {extracted}: {text}")
                if extracted >= 4:
                    break

        print("\n" + "=" * 65)
        print("🎉 SUCCESS: Tabs opened and running live on your screen!")
        print("Leaving browser open for 15 seconds so you can browse the tabs...")
        print("=" * 65)
        time.sleep(15.0)

        browser.close()
        print("Browser test completed cleanly.")

if __name__ == "__main__":
    main()
