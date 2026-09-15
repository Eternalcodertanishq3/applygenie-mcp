"""Anti-detection measures and human-like behavior simulation."""

import logging
import random
import time
from typing import Any

logger = logging.getLogger(__name__)

def human_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    time.sleep(random.uniform(min_seconds, max_seconds))

def human_type_delay() -> float:
    return random.uniform(0.05, 0.15)

def get_stealth_args() -> list[str]:
    return [
        "--disable-blink-features=AutomationControlled",
        "--disable-features=TranslateUI",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-popup-blocking"
    ]

def get_realistic_user_agent() -> str:
    # A realistic recent Chrome user agent
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_realistic_viewport() -> dict:
    return {"width": 1920, "height": 1080}

def inject_stealth_scripts(page: Any) -> None:
    script = """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3]
    });
    
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
    });
    
    window.chrome = {
        runtime: {}
    };
    """
    page.add_init_script(script)

def detect_captcha(page: Any) -> bool:
    try:
        # Basic check for common captchas
        captcha_selectors = [
            "iframe[src*='recaptcha']",
            "iframe[src*='hcaptcha']",
            "iframe[src*='cloudflare']"
        ]
        for selector in captcha_selectors:
            if page.locator(selector).count() > 0:
                return True
        return False
    except Exception as e:
        logger.error(f"Error detecting captcha: {e}")
        return False

def dismiss_cookie_banner(page: Any) -> bool:
    try:
        selectors = [
            "button:has-text('Accept All')",
            "button:has-text('Accept Cookies')",
            "button:has-text('I Accept')",
            "button:has-text('Got it')",
            "button:has-text('Agree')"
        ]
        for selector in selectors:
            loc = page.locator(selector)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click()
                human_delay(0.5, 1.0)
                return True
        return False
    except Exception as e:
        logger.error(f"Error dismissing cookie banner: {e}")
        return False
