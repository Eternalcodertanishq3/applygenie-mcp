import logging
import re
from typing import Dict, List, Optional
import pygetwindow as gw
from pywinauto import Application

logger = logging.getLogger(__name__)

def _fuzzy_match(query: str, title: str) -> float:
    """Simple fuzzy matching score."""
    q_lower = query.lower()
    t_lower = title.lower()
    if q_lower == t_lower:
        return 1.0
    if q_lower in t_lower:
        return 0.8
    # Simple word overlap
    q_words = set(q_lower.split())
    t_words = set(t_lower.split())
    if not q_words:
        return 0.0
    overlap = len(q_words & t_words) / len(q_words)
    return overlap * 0.5

def list_windows() -> List[Dict]:
    """Return all visible windows with title, position, size, and activity status."""
    windows = []
    try:
        all_windows = gw.getAllWindows()
        for w in all_windows:
            if not w.title.strip() or not w.visible:
                continue
            windows.append({
                "title": w.title,
                "x": w.left,
                "y": w.top,
                "width": w.width,
                "height": w.height,
                "is_active": w.isActive,
            })
    except Exception as e:
        logger.error(f"Error listing windows: {e}")
    return windows

def _find_window_fuzzy(title: str) -> Optional[gw.Window]:
    windows = gw.getAllWindows()
    best_match = None
    best_score = 0.0
    
    for w in windows:
        if not w.title.strip():
            continue
        score = _fuzzy_match(title, w.title)
        if score > best_score:
            best_score = score
            best_match = w
            
    return best_match if best_score > 0.3 else None

def focus_window(title: str) -> str:
    """Bring window to foreground by fuzzy title match."""
    w = _find_window_fuzzy(title)
    if w:
        try:
            w.activate()
            return f"Focused window: {w.title}"
        except Exception as e:
            logger.warning(f"pygetwindow failed to activate: {e}. Trying pywinauto.")
            try:
                app = Application().connect(handle=w._hWnd)
                app.window(handle=w._hWnd).set_focus()
                return f"Focused window (pywinauto): {w.title}"
            except Exception as e2:
                return f"Failed to focus window {title}: {e2}"
    return f"Window not found: {title}"

def minimize_window(title: str) -> str:
    w = _find_window_fuzzy(title)
    if w:
        w.minimize()
        return f"Minimized window: {w.title}"
    return f"Window not found: {title}"

def maximize_window(title: str) -> str:
    w = _find_window_fuzzy(title)
    if w:
        w.maximize()
        return f"Maximized window: {w.title}"
    return f"Window not found: {title}"

def get_active_window() -> Optional[Dict]:
    """Return info about currently focused window."""
    try:
        w = gw.getActiveWindow()
        if w:
            return {
                "title": w.title,
                "x": w.left,
                "y": w.top,
                "width": w.width,
                "height": w.height,
                "is_active": True,
            }
    except Exception as e:
        logger.error(f"Error getting active window: {e}")
    return None

def find_windows(pattern: str) -> List[Dict]:
    """Search windows by regex/substring pattern."""
    windows = list_windows()
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        return [w for w in windows if regex.search(w["title"])]
    except re.error:
        # Fallback to substring
        return [w for w in windows if pattern.lower() in w["title"].lower()]
