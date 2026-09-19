"""Playwright browser lifecycle management for ApplyGenie.

Manages persistent browser contexts with stealth configuration.
"""

import base64
import logging
import os
from pathlib import Path
from typing import Any, Optional

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Playwright
except ImportError:
    sync_playwright = None

logger = logging.getLogger(__name__)

class BrowserEngine:
    def __init__(self) -> None:
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright_context = None

    def launch(self, headless: bool = False) -> None:
        if sync_playwright is None:
            raise RuntimeError("playwright is not installed. Run 'uv pip install playwright' and 'playwright install'")
        
        self._playwright_context = sync_playwright()
        self.playwright = self._playwright_context.start()
        
        user_data_dir = Path.home() / ".applygenie" / "browser_data"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        from applygenie.browser.stealth import get_stealth_args, get_realistic_user_agent, get_realistic_viewport
        
        args = get_stealth_args()
        viewport = get_realistic_viewport()
        
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=headless,
            args=args,
            user_agent=get_realistic_user_agent(),
            viewport=viewport,
            locale="en-US",
            timezone_id="America/New_York",
            bypass_csp=True,
        )
        self.browser = self.context.browser
        
        if len(self.context.pages) > 0:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

    def get_page(self) -> Page:
        if self.page is None:
            if self.context is None:
                raise RuntimeError("Browser not launched")
            self.page = self.context.new_page()
        return self.page

    def navigate(self, url: str) -> str:
        page = self.get_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
        except Exception as e:
            logger.warning(f"Navigation warning: {e}")
        from applygenie.browser.stealth import inject_stealth_scripts
        try:
            inject_stealth_scripts(page)
        except Exception:
            pass
        return page.title()

    def close(self) -> None:
        if self.context:
            self.context.close()
            self.context = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
            self._playwright_context = None
        self.browser = None
        self.page = None

    def get_page_text(self) -> str:
        page = self.get_page()
        return page.evaluate("document.body.innerText")

    def get_page_screenshot(self) -> str:
        page = self.get_page()
        screenshot_bytes = page.screenshot(full_page=True)
        return base64.b64encode(screenshot_bytes).decode("utf-8")

    @property
    def is_running(self) -> bool:
        return self.context is not None
