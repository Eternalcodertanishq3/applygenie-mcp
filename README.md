# ApplyGenie MCP 🧞‍♂️

> **Your magical AI assistant that grants your job wishes.**  
> A production-grade [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for desktop control, autonomous job application form filling, local application tracking, and personalized AI mock interview preparation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Standard-orange.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastMCP](https://img.shields.io/badge/built%20with-FastMCP-green.svg)](https://github.com/jlowin/fastmcp)

---

## 🌟 What is ApplyGenie?

ApplyGenie bridges the gap between job discovery, form filling, application tracking, and interview readiness. It runs locally as an MCP server, empowering LLM agents (Claude Desktop, Cursor, Antigravity, VS Code, Windsurf) with **35+ specialized tools**:

1. 🖥️ **Desktop Control & Vision**: Fast screenshot captures (`mss`), DPI-corrected mouse navigation, human-like typing jitter (`pynput`), and native Windows window management (`pywinauto`).
2. 📋 **Smart Candidate Profile**: Local JSON schema storing your education, work experiences, skills, work authorizations, and custom portal answer banks.
3. 🌐 **AI Browser Automation & Form Filling**: Playwright-powered stealth engine that parses forms using DOM + Accessibility Trees, maps fields to your profile, uploads PDF/DOCX resumes, and requests explicit confirmation before submitting.
4. 📊 **Application Tracker & Analytics**: Local SQLite database logging every applied role, tracking interview conversion rates, and charting application velocity.
5. 🎤 **Mock Interview Engine**: Socratic coding hint ladders (4 rungs), behavioral STAR coaching ("I" vs "We" ownership ratio analysis), and 4-phase system design state machines.

---

## 🚀 Quickstart & Installation

### Option 1: Run directly with `uvx` (Zero manual setup)
```bash
uvx applygenie-mcp
```

### Option 2: Install via `pip`
```bash
pip install applygenie-mcp

# With full browser automation support:
pip install "applygenie-mcp[browser]"
playwright install chromium
```

---

## ⚙️ Configuration for MCP Clients

### 1. Claude Desktop
Add to your `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "applygenie": {
      "command": "uvx",
      "args": ["applygenie-mcp"]
    }
  }
}
```

### 2. Google Antigravity
Add to your project's `.agents/mcp_config.json` or `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "applygenie": {
      "command": "python",
      "args": ["-m", "applygenie.server"],
      "cwd": "C:\\Personal Projects\\applygenie-mcp"
    }
  }
}
```

### 3. Cursor / Windsurf
Navigate to **Settings > Features > MCP > Add New MCP Server**:
- **Name:** `ApplyGenie`
- **Type:** `command`
- **Command:** `uvx applygenie-mcp`

---

## 🛠️ Complete MCP Tool Reference

### 1. Desktop Control & Vision
| Tool | Description |
| :--- | :--- |
| `screenshot(monitor=0)` | Captures JPEG screenshot encoded in base64. |
| `get_screen_size()` | Enumerates all connected monitors and resolution bounds. |
| `mouse_click(x, y, button, clicks)` | Clicks mouse with DPI scaling correction. |
| `mouse_move(x, y)` | Moves mouse cursor smoothly to target coordinates. |
| `mouse_scroll(direction, amount)` | Scrolls mouse wheel up or down. |
| `mouse_drag(start_x, start_y, end_x, end_y)` | Performs click-and-drag between coordinates. |
| `get_mouse_position()` | Returns current mouse cursor coordinates. |
| `type_text_input(text, interval)` | Types text with randomized jitter (±30%) to emulate human cadence. |
| `press_keyboard_key(keys)` | Executes hotkeys (e.g. `ctrl+a`, `tab`, `enter`). |
| `list_open_windows()` | Returns all visible application windows. |
| `focus_app_window(title)` | Brings target window to foreground via fuzzy title match. |
| `minimize_app_window(title)` | Minimizes target window. |
| `maximize_app_window(title)` | Maximizes target window. |
| `get_current_window()` | Returns info about currently focused active window. |
| `search_windows(pattern)` | Finds windows matching regex or substring. |
| `wait_seconds(seconds)` | Pauses execution safely (capped at 30s). |
| `get_action_history(last_n)` | Inspects safety audit action logs. |

### 2. Profile & Resume Management
| Tool | Description |
| :--- | :--- |
| `get_user_profile()` | Loads complete candidate profile. |
| `get_user_profile_summary()` | Returns concise summary of skills, credentials, and work history. |
| `setup_user_profile(...)` | Initializes candidate personal info, URLs, location, and defaults. |
| `update_profile_attribute(field, val)` | Updates a specific top-level profile field. |
| `add_work_experience(...)` | Appends a work experience or internship entry. |
| `add_education_entry(...)` | Appends a degree / university qualification. |
| `add_project_entry(...)` | Appends a notable software project. |
| `save_portal_custom_answer(pattern, ans)` | Saves reusable answer for portal questions (e.g. "Why hire you?"). |
| `parse_resume_file(filepath)` | Extracts text from PDF or DOCX resume. |

### 3. Browser Automation & Form Filling
| Tool | Description |
| :--- | :--- |
| `browser_open(url, headless)` | Launches stealth Chromium browser. |
| `browser_navigate(url)` | Navigates browser to destination page. |
| `browser_get_page_text()` | Extracts visible text content from current tab. |
| `browser_get_page_screenshot()` | Captures high-res screenshot of current webpage. |
| `browser_detect_form_fields()` | Parses inputs, textareas, selects, and file upload fields. |
| `browser_fill_detected_form()` | Auto-maps profile data and fills all detected inputs. |
| `browser_upload_resume(filepath)` | Uploads resume PDF/DOCX to detected file input field. |
| `browser_submit_form(confirm=True)` | Clicks submit button (**Requires explicit human confirmation**). |
| `browser_close()` | Closes browser gracefully. |

### 4. Application Tracker
| Tool | Description |
| :--- | :--- |
| `track_application(...)` | Records a new application in local SQLite database. |
| `update_application_progress(id, status)` | Updates status (`interview`, `screening`, `offer`, `rejected`). |
| `get_tracked_applications(...)` | Lists applications with optional status/company filtering. |
| `search_tracked_applications(query)` | Full-text search across roles, companies, and notes. |
| `get_application_analytics()` | Computes interview conversion rates, offer rates, and top companies. |

### 5. Mock Interview Engine
| Tool | Description |
| :--- | :--- |
| `start_mock_interview(type, company, diff)` | Starts coding, behavioral, or system design session. |
| `get_coding_hint()` | Advances the 4-rung Socratic hint ladder without spoiling answers. |
| `analyze_behavioral_star_answer(text)` | Evaluates STAR structure and calculates "I" vs "We" ownership ratio. |
| `advance_system_design_interview(input)` | Steps through 4 architectural interview phases. |
| `generate_interview_scorecard(...)` | Produces structured 1-5 rubric report card and hiring recommendation. |

---

## 🛡️ Safety & Failsafe Architecture

ApplyGenie enforces strict safety guardrails:
1. **Mouse Corner Failsafe**: Moving the cursor to screen corner `(0, 0)` immediately halts all automation.
2. **Rate Limiting**: Enforces a maximum action frequency (default: 30 actions/min) and minimum delays to prevent runaway loops.
3. **Human-in-the-Loop Confirmation**: Form submission and destructive actions require explicit `confirm=True` confirmation. The copilot fills 95% of the form, pausing for human review.
4. **Local Data Storage**: All candidate profile data, resume caches, and application records stay on your local disk at `~/.applygenie/`. No telemetry, no cloud sync.
5. **Key Combo Shield**: Dangerous system combinations (`alt+f4`, `ctrl+alt+del`) are blocked by default.

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Developed with ❤️ by **Tanishq Mangal** (`tanishkmangal3@gmail.com`).
