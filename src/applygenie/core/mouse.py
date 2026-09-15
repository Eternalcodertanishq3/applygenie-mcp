import ctypes
import logging
import time
from typing import Dict, Tuple
from pynput.mouse import Controller, Button

from applygenie.config import FAILSAFE_ENABLED

logger = logging.getLogger(__name__)
mouse = Controller()

class FailsafeError(Exception):
    pass

def _get_dpi_scale() -> float:
    """Query Windows DPI and return scaling factor."""
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        dpi = user32.GetDpiForSystem()
        return dpi / 96.0
    except Exception:
        return 1.0

def _adjust_for_dpi(x: int, y: int) -> Tuple[int, int]:
    """Adjust coordinates based on DPI scale."""
    scale = _get_dpi_scale()
    return int(x * scale), int(y * scale)

def _check_failsafe(x: int, y: int):
    """Abort if close to (0,0)."""
    if FAILSAFE_ENABLED and x <= 5 and y <= 5:
        logger.error("Failsafe triggered.")
        raise FailsafeError("Mouse coordinates triggered failsafe abort.")

def click(x: int, y: int, button: str = "left", clicks: int = 1) -> str:
    """Move to position and click."""
    _check_failsafe(x, y)
    adj_x, adj_y = _adjust_for_dpi(x, y)
    mouse.position = (adj_x, adj_y)
    time.sleep(0.05)
    btn = getattr(Button, button.lower(), Button.left)
    mouse.click(btn, clicks)
    logger.info(f"Clicked {button} at ({x}, {y}) {clicks} times")
    return f"Clicked {button} at ({x}, {y})"

def move(x: int, y: int) -> str:
    """Move mouse to absolute position."""
    _check_failsafe(x, y)
    adj_x, adj_y = _adjust_for_dpi(x, y)
    mouse.position = (adj_x, adj_y)
    return f"Moved to ({x}, {y})"

def double_click(x: int, y: int) -> str:
    return click(x, y, button="left", clicks=2)

def right_click(x: int, y: int) -> str:
    return click(x, y, button="right", clicks=1)

def drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> str:
    """Click and drag from start to end."""
    _check_failsafe(start_x, start_y)
    adj_start = _adjust_for_dpi(start_x, start_y)
    adj_end = _adjust_for_dpi(end_x, end_y)
    
    mouse.position = adj_start
    time.sleep(0.05)
    mouse.press(Button.left)
    time.sleep(0.05)
    
    # Simple linear interpolation for drag
    steps = int(duration * 60)
    for i in range(steps):
        t = i / steps
        cur_x = int(adj_start[0] + (adj_end[0] - adj_start[0]) * t)
        cur_y = int(adj_start[1] + (adj_end[1] - adj_start[1]) * t)
        mouse.position = (cur_x, cur_y)
        time.sleep(duration / steps)
        
    mouse.position = adj_end
    mouse.release(Button.left)
    return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"

def scroll(direction: str, amount: int = 3) -> str:
    """Scroll up or down."""
    dy = amount if direction.lower() == "up" else -amount
    mouse.scroll(0, dy)
    return f"Scrolled {direction} by {amount}"

def get_position() -> Dict[str, int]:
    """Return current mouse position."""
    try:
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        scale = _get_dpi_scale()
        return {"x": int(pt.x / scale), "y": int(pt.y / scale)}
    except Exception:
        pos = mouse.position or (0, 0)
        scale = _get_dpi_scale()
        return {"x": int(pos[0] / scale), "y": int(pos[1] / scale)}
