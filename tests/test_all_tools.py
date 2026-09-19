"""Comprehensive Tool Coverage and Annotation Verification Suite.

Ensures all 45 MCP tools exposed by ApplyGenie are tested and verified,
validating explicit boolean declarations for all 4 modern MCP hints:
1. readOnlyHint
2. destructiveHint
3. idempotentHint
4. openWorldHint
"""

import pytest
from applygenie.server import mcp

EXPECTED_TOOLS = [
    # 1. Desktop Control
    "screenshot",
    "get_screen_size",
    "mouse_click",
    "mouse_move",
    "mouse_scroll",
    "mouse_drag",
    "get_mouse_position",
    "type_text_input",
    "press_keyboard_key",
    "list_open_windows",
    "focus_app_window",
    "minimize_app_window",
    "maximize_app_window",
    "get_current_window",
    "search_windows",
    "wait_seconds",
    "get_action_history",

    # 2. Profile Management
    "get_user_profile",
    "get_user_profile_summary",
    "setup_user_profile",
    "update_profile_attribute",
    "add_work_experience",
    "add_education_entry",
    "add_project_entry",
    "save_portal_custom_answer",
    "parse_resume_file",

    # 3. Browser Automation & Form Filling
    "browser_open",
    "browser_navigate",
    "browser_get_page_text",
    "browser_get_page_screenshot",
    "browser_detect_form_fields",
    "browser_fill_detected_form",
    "browser_upload_resume",
    "browser_submit_form",
    "browser_close",

    # 4. Application Tracker
    "track_application",
    "update_application_progress",
    "get_tracked_applications",
    "search_tracked_applications",
    "get_application_analytics",

    # 5. Mock Interview Engine
    "start_mock_interview",
    "get_coding_hint",
    "analyze_behavioral_star_answer",
    "advance_system_design_interview",
    "generate_interview_scorecard",
]


@pytest.mark.asyncio
async def test_all_45_tools_registered():
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}
    assert len(tools) == 45, f"Expected 45 tools, found {len(tools)}"
    for expected in EXPECTED_TOOLS:
        assert expected in tool_names, f"Missing expected tool: {expected}"


@pytest.mark.asyncio
async def test_all_tools_have_m8ven_annotations():
    tools = await mcp.list_tools()
    for tool in tools:
        assert tool.annotations is not None, f"Tool {tool.name} missing annotations"
        data = tool.annotations.model_dump(by_alias=True)
        for hint in ["readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"]:
            assert hint in data, f"Tool {tool.name} missing {hint}"
            assert isinstance(data[hint], bool), f"Tool {tool.name} {hint} is not boolean: {data[hint]}"


@pytest.mark.asyncio
async def test_all_tools_have_descriptions():
    tools = await mcp.list_tools()
    for tool in tools:
        assert tool.description and len(tool.description.strip()) > 10, f"Tool {tool.name} lacks meaningful description"
