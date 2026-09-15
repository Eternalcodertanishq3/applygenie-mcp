import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
import json

from applygenie.config import (
    FAILSAFE_ENABLED,
    LOGS_DIR,
    MAX_ACTIONS_PER_MINUTE,
    MIN_ACTION_DELAY,
)

logger = logging.getLogger(__name__)

class ActionType(Enum):
    SCREENSHOT = "SCREENSHOT"
    MOUSE_CLICK = "MOUSE_CLICK"
    MOUSE_MOVE = "MOUSE_MOVE"
    MOUSE_SCROLL = "MOUSE_SCROLL"
    KEY_TYPE = "KEY_TYPE"
    KEY_PRESS = "KEY_PRESS"
    WINDOW_FOCUS = "WINDOW_FOCUS"
    BROWSER_NAVIGATE = "BROWSER_NAVIGATE"
    FORM_FILL = "FORM_FILL"
    FORM_SUBMIT = "FORM_SUBMIT"
    FILE_UPLOAD = "FILE_UPLOAD"
    OTHER = "OTHER"

@dataclass
class ActionRecord:
    timestamp: datetime
    action_type: ActionType
    parameters: dict[str, Any]
    result: str
    success: bool

class FailsafeTriggered(Exception):
    pass

class RateLimitExceeded(Exception):
    pass

class SafetyManager:
    def __init__(self) -> None:
        self.action_log: deque[ActionRecord] = deque(maxlen=1000)
        self.last_action_time: float = 0.0
        
    def check_failsafe(self, x: int = 0, y: int = 0) -> None:
        if FAILSAFE_ENABLED and abs(x) <= 5 and abs(y) <= 5:
            raise FailsafeTriggered("Failsafe triggered: mouse coordinates near (0,0)")

    def check_rate_limit(self) -> None:
        now = time.time()
        minute_ago = now - 60.0
        # Count actions in the last minute
        recent_actions = sum(1 for action in self.action_log if action.timestamp.timestamp() > minute_ago)
        if recent_actions >= MAX_ACTIONS_PER_MINUTE:
            raise RateLimitExceeded(f"Rate limit exceeded: {MAX_ACTIONS_PER_MINUTE} actions per minute.")

    def enforce_delay(self) -> None:
        now = time.time()
        elapsed = now - self.last_action_time
        if elapsed < MIN_ACTION_DELAY:
            time.sleep(MIN_ACTION_DELAY - elapsed)
        self.last_action_time = time.time()

    def log_action(self, action_type: ActionType, parameters: dict[str, Any], result: str, success: bool = True) -> None:
        record = ActionRecord(
            timestamp=datetime.now(),
            action_type=action_type,
            parameters=parameters,
            result=result,
            success=success
        )
        self.action_log.append(record)
        logger.debug(f"Action logged: {action_type.name} - {success}")

    def get_action_log(self, last_n: int = 50) -> list[dict[str, Any]]:
        actions = list(self.action_log)[-last_n:]
        return [
            {
                "timestamp": a.timestamp.isoformat(),
                "action_type": a.action_type.name,
                "parameters": a.parameters,
                "result": a.result,
                "success": a.success,
            }
            for a in actions
        ]

    def requires_confirmation(self, action_type: ActionType) -> bool:
        return action_type in {ActionType.FORM_SUBMIT, ActionType.FILE_UPLOAD}

    def export_log(self, filepath: Path | None = None) -> str:
        if filepath is None:
            filepath = LOGS_DIR / f"action_log_{int(time.time())}.json"
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.get_action_log(len(self.action_log)), f, indent=2)
            
        return str(filepath)

    def reset(self) -> None:
        self.action_log.clear()
        self.last_action_time = 0.0

safety = SafetyManager()

def safe_action(action_type: ActionType):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                safety.check_rate_limit()
                safety.enforce_delay()
                result = func(*args, **kwargs)
                safety.log_action(action_type, {"args": args, "kwargs": kwargs}, str(result), success=True)
                return result
            except Exception as e:
                safety.log_action(action_type, {"args": args, "kwargs": kwargs}, str(e), success=False)
                raise e
        return wrapper
    return decorator
