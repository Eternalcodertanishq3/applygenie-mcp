import logging
import random
import time
from typing import Union
from pynput.keyboard import Controller, Key, KeyCode

from applygenie.config import BLOCKED_KEY_COMBOS

logger = logging.getLogger(__name__)
keyboard = Controller()

def _parse_key(key_name: str) -> Union[Key, KeyCode]:
    """Map string names to pynput key objects."""
    key_map = {
        "enter": Key.enter,
        "tab": Key.tab,
        "backspace": Key.backspace,
        "delete": Key.delete,
        "escape": Key.esc,
        "space": Key.space,
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right,
        "home": Key.home,
        "end": Key.end,
        "pageup": Key.page_up,
        "pagedown": Key.page_down,
        "ctrl": Key.ctrl,
        "alt": Key.alt,
        "shift": Key.shift,
        "win": Key.cmd,
    }
    for i in range(1, 13):
        key_map[f"f{i}"] = getattr(Key, f"f{i}")

    key_name = key_name.lower().strip()
    return key_map.get(key_name) or KeyCode.from_char(key_name)

def _randomized_delay(interval: float):
    """Wait for an interval with +/- 30% jitter."""
    jitter = interval * 0.3
    delay = random.uniform(interval - jitter, interval + jitter)
    time.sleep(max(0.001, delay))

def type_text(text: str, interval: float = 0.03) -> str:
    """Type text character by character with randomized delays."""
    logger.info(f"Typing text (length: {len(text)})")
    for char in text:
        keyboard.type(char)
        _randomized_delay(interval)
    return f"Successfully typed {len(text)} characters."

def press_key(key_combo: str) -> str:
    """Parse and execute key combos like 'ctrl+a'."""
    normalized_combo = key_combo.lower().strip()
    if normalized_combo in BLOCKED_KEY_COMBOS:
        raise ValueError(f"Blocked key combo: {key_combo}")
    
    logger.info(f"Pressing key combo: {key_combo}")
    keys_to_press = [_parse_key(k) for k in normalized_combo.split('+')]
    
    with keyboard.pressed(*keys_to_press[:-1]):
        keyboard.press(keys_to_press[-1])
        keyboard.release(keys_to_press[-1])
        
    return f"Successfully pressed {key_combo}"

def press_hotkey(*keys: str) -> str:
    """Press multiple keys simultaneously."""
    combo = "+".join(keys).lower()
    return press_key(combo)
