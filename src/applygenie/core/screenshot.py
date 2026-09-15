import base64
import io
import logging
from pathlib import Path

import mss
from PIL import Image

from applygenie.config import SCREENSHOT_MAX_WIDTH, SCREENSHOT_QUALITY

logger = logging.getLogger(__name__)


def capture_screenshot(monitor: int = 0) -> tuple[str, dict]:
    """Capture a screenshot and return as (base64_encoded_jpeg, metadata_dict).
    
    Args:
        monitor: Monitor index. 0 = all monitors combined, 1 = primary, 2+ = secondary.
    
    Returns:
        Tuple of (base64 encoded JPEG string, metadata dict with width/height/monitor info)
    """
    try:
        with mss.mss() as sct:
            monitors = sct.monitors
            if monitor >= len(monitors):
                monitor = 0  # fallback to all monitors
            
            screenshot = sct.grab(monitors[monitor])
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            total_monitors = len(monitors) - 1
    except Exception as e:
        logger.warning(f"mss screen capture failed: {e}. Falling back to PIL ImageGrab.")
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab(all_screens=True)
            total_monitors = 1
        except Exception as e2:
            logger.warning(f"Desktop screenshot unavailable in current session context ({e2}). Generating placeholder.")
            img = Image.new("RGB", (1920, 1080), color=(25, 25, 30))
            total_monitors = 1
        
        # Downscale if too large to save tokens
        original_size = img.size
        if img.width > SCREENSHOT_MAX_WIDTH:
            ratio = SCREENSHOT_MAX_WIDTH / img.width
            new_size = (SCREENSHOT_MAX_WIDTH, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Encode to JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=SCREENSHOT_QUALITY)
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        metadata = {
            "monitor": monitor,
            "original_width": original_size[0],
            "original_height": original_size[1],
            "encoded_width": img.width,
            "encoded_height": img.height,
            "total_monitors": total_monitors,
        }
        
        logger.info(f"Screenshot captured: monitor={monitor}, size={img.size}")
        return b64, metadata


def get_screen_info() -> dict:
    """Get information about all connected monitors."""
    with mss.mss() as sct:
        return {
            "total_monitors": len(sct.monitors) - 1,
            "monitors": [
                {
                    "index": i,
                    "left": m["left"],
                    "top": m["top"],
                    "width": m["width"],
                    "height": m["height"],
                }
                for i, m in enumerate(sct.monitors)
            ],
        }
