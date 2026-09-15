"""Tests for Safety manager, failsafes, and action logging."""

import pytest
from applygenie.core.safety import (
    SafetyManager, FailsafeTriggered, RateLimitExceeded, ActionType
)


def test_failsafe_trigger():
    manager = SafetyManager()
    # Coordinates at or near (0,0) must trigger failsafe
    with pytest.raises(FailsafeTriggered):
        manager.check_failsafe(0, 0)

    with pytest.raises(FailsafeTriggered):
        manager.check_failsafe(4, 3)

    # Coordinates away from corner should pass
    manager.check_failsafe(100, 200)


def test_action_logging():
    manager = SafetyManager()
    manager.log_action(ActionType.MOUSE_CLICK, {"x": 150, "y": 250}, "Clicked left")
    manager.log_action(ActionType.KEY_TYPE, {"text_length": 15}, "Typed text")

    history = manager.get_action_log(10)
    assert len(history) == 2
    assert history[0]["action_type"] == "MOUSE_CLICK"
    assert history[1]["action_type"] == "KEY_TYPE"
